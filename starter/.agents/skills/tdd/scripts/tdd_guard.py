#!/usr/bin/env python3
"""Guards and gates for the test-first cycle. Standard library only (3.9+).

Hooks (Claude Code PreToolUse; read the hook JSON on stdin, exit 2 to block):
  tdd_guard.py hook test-writer   # no reading implementation, write tests only
  tdd_guard.py hook implementer   # never create, edit or delete tests

Cycle gates (any tool; read JUnit XML files or folders of them):
  tdd_guard.py verify-red   --before <junit...> --after <junit...>
      Every NEW test must fail - not pass (vacuous/tautological), not be
      skipped, and not error because the test file can't load.
  tdd_guard.py verify-green --since <red-commit> --results <junit...>
      All tests pass, and no test file changed since the red commit.
  tdd_guard.py verify-task --base <commit-before-the-task>
      The task went through test_writer -> implementer -> architecture_reviewer,
      read from commit trailers since <base>:
        TDD-Step: red          (or TDD-No-Test: <reason>)  - test_writer
        TDD-Step: green                                    - implementer
        TDD-Review: PASS       on the LAST commit, which must change no files

  tdd_guard.py is-test <path>     # debugging: classify a path

Boundaries can be tuned per project with `.tdd-boundary.json` at the repo
root: {"tests": [globs], "implementation": [globs], "public": [globs]}.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_TESTS = [
    "test/*", "*/test/*", "tests/*", "*/tests/*", "__tests__/*", "*/__tests__/*",
    "spec/*", "*/spec/*",
    "*.test.*", "*.spec.*", "*_test.*", "test_*.py", "*/test_*.py", "conftest.py", "*/conftest.py",
    "*Test.java", "*Tests.java", "*IT.java", "*Test.kt", "*Tests.kt",
]
# Functional unit tests call only each module's public interface, so ALL other
# source code is implementation - domain, use cases, ports, adapters, storage.
DEFAULT_IMPLEMENTATION = [
    f"{p}{seg}/*" for seg in ("src", "lib", "app", "server", "internal", "cmd", "pkg",
                              "modules", "domain", "application", "adapters", "infrastructure",
                              "api", "migrations", "controllers", "services", "repositories",
                              "handlers", "features", "components", "pages")
    for p in ("", "*/")
]
# What the tests may rely on: each module's public interface file (top level of
# the module only), the test app factory, and contracts. Patterns starting with
# "re:" are regular expressions; others are globs.
DEFAULT_PUBLIC = [
    r"re:(^|/)modules/[^/]+/(index\.(ts|tsx|js|mjs|cjs)|__init__\.py)$",
    r"re:(^|/)modules/[^/]+/public/[^/]+$",
    r"re:(^|/)app/test[-_]app\.[a-z]+$",
    "openapi/*", "*/openapi/*", "contracts/*", "*/contracts/*",
]
READ_TOOLS = re.compile(
    r"\b(cat|less|more|head|tail|sed|awk|bat|nl|strings|xxd|od|grep|egrep|rg|ag|ack|python3?\s+-c|node\s+-e)\b")
GIT_HISTORY = re.compile(r"\bgit\s+(show|diff|blame|log\s+.*-p|log\s+.*--patch|grep|cat-file)\b")
MUTATING = re.compile(r"(\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|\btee\b|\btruncate\b|>>?|\bgit\s+(checkout|restore|rm|mv|reset|stash))")
ARTEFACT = re.compile(r"(^|/)(__pycache__|node_modules|\.tdd|\.pytest_cache|build|target|dist|coverage)/|\.(pyc|class)$")
LOAD_ERRORS = re.compile(
    r"(ECONNREFUSED|[Cc]onnection refused|fetch failed|EADDRINUSE|did not start|failed to start|"
    r"Timed out waiting for|Cannot find module|Failed to load|ModuleNotFoundError|ImportError|SyntaxError|"
    r"error while loading|cannot find symbol|package .* does not exist|undefined: |"
    r"Failed to resolve import|is not defined|No such file or directory)", re.I)


# ---------------------------------------------------------------- paths
def _root(hook_input: dict | None = None) -> Path:
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), (hook_input or {}).get("cwd")):
        if candidate:
            return Path(candidate).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except FileNotFoundError:
        pass
    return Path.cwd()


def _boundary(root: Path) -> dict:
    cfg = {"tests": DEFAULT_TESTS, "implementation": DEFAULT_IMPLEMENTATION, "public": DEFAULT_PUBLIC}
    f = root / ".tdd-boundary.json"
    if f.exists():
        try:
            cfg.update({k: v for k, v in json.loads(f.read_text()).items() if k in cfg})
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def _rel(path: str, root: Path) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = root / p
    try:
        return p.resolve().relative_to(root).as_posix()
    except ValueError:
        return p.as_posix().lstrip("/")


def _match(rel: str, patterns: list[str]) -> bool:
    name = rel.rsplit("/", 1)[-1]
    for pat in patterns:
        if pat.startswith("re:"):
            if re.search(pat[3:], rel):
                return True
        elif fnmatch.fnmatchcase(rel, pat) or fnmatch.fnmatchcase(name, pat):
            return True
    return False


def is_test(rel: str, cfg: dict) -> bool:
    return _match(rel, cfg["tests"])


def is_implementation(rel: str, cfg: dict) -> bool:
    if is_test(rel, cfg) or _match(rel, cfg["public"]):
        return False
    return _match(rel, cfg["implementation"])


# ---------------------------------------------------------------- hooks
def _block(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def _paths_in_command(command: str) -> list[str]:
    return [t.strip("'\"") for t in re.split(r"\s+", command) if "/" in t or "." in t]


SAFE_TOP_LEVEL = ("specs", "docs", "openapi", "contracts", ".tdd", "test", "tests")


def _search_target_allowed(rel: str, cfg: dict) -> bool:
    """A content search is allowed only inside tests, docs/specs, contracts or public interfaces."""
    if rel in ("", "."):
        return False
    if rel.split("/")[0] in SAFE_TOP_LEVEL:
        return True
    return is_test(rel, cfg) or is_test(rel + "/x", cfg) or _match(rel, cfg["public"]) \
        or _match(rel + "/x", cfg["public"])


def hook_test_writer(data: dict) -> int:
    root = _root(data)
    cfg = _boundary(root)
    tool, inp = data.get("tool_name", ""), data.get("tool_input", {}) or {}

    if tool == "Read":
        rel = _rel(inp.get("file_path", ""), root)
        if is_implementation(rel, cfg):
            return _block(f"test_writer may not read {rel}. Functional tests use only the spec, the "
                          "plan, the modules' public interface files and the test app factory - "
                          "nothing behind the public interface.")
    elif tool == "Grep":
        if not _search_target_allowed(_rel(inp.get("path") or ".", root), cfg):
            return _block("test_writer: search only within tests, specs/, docs/ or contracts - not "
                          "across the codebase (it would expose implementation). Read public "
                          "interface files directly instead.")
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        rel = _rel(inp.get("file_path") or inp.get("notebook_path", ""), root)
        if not (is_test(rel, cfg) or rel.startswith(".tdd/")):
            return _block(f"test_writer writes tests only; {rel} is not a test file. Stubs for public "
                          "operations are created by the implementer.")
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if GIT_HISTORY.search(cmd):
            return _block("test_writer may not inspect code history or diffs (they expose implementation).")
        if READ_TOOLS.search(cmd):
            for token in _paths_in_command(cmd):
                rel = _rel(token, root)
                if is_implementation(rel, cfg) or is_implementation(rel + "/x", cfg):
                    return _block(f"test_writer may not read {rel} - it's behind the public interface.")
            if re.search(r"\b(grep|rg|ag|ack)\b", cmd) and re.search(r"(\s-\w*r|\brg\b|\bag\b)", cmd) \
                    and not re.search(r"\b(tests?|__tests__|spec|specs|docs|contracts|openapi)\b", cmd):
                return _block("test_writer: recursive search must be limited to tests, specs, docs "
                              "or contracts.")
    return 0


def hook_implementer(data: dict) -> int:
    root = _root(data)
    cfg = _boundary(root)
    tool, inp = data.get("tool_name", ""), data.get("tool_input", {}) or {}
    message = ("Tests are owned by test_writer and are the specification. Don't create, change or "
               "delete them. If a test looks wrong, stop and report which test and why.")
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        rel = _rel(inp.get("file_path") or inp.get("notebook_path", ""), root)
        if is_test(rel, cfg):
            return _block(f"{message} ({rel})")
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if MUTATING.search(cmd):
            for token in _paths_in_command(cmd):
                if is_test(_rel(token, root), cfg):
                    return _block(f"{message} ({token})")
    return 0


# ---------------------------------------------------------------- junit
def _junit_files(args: list[str]) -> list[Path]:
    files = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files += sorted(p.rglob("*.xml"))
        elif p.exists():
            files.append(p)
    return files


def read_junit(args: list[str]) -> dict[str, tuple[str, str]]:
    """Return {test_id: (status, message)} with status in passed/failed/error/skipped."""
    results = {}
    for f in _junit_files(args):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for tc in root.iter("testcase"):
            tid = f"{tc.get('file') or tc.get('classname') or ''}::{tc.get('name')}"
            status, msg = "passed", ""
            for child in tc:
                tag = child.tag.lower()
                if tag in ("failure", "error", "skipped"):
                    status = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                    msg = (child.get("message") or "") + " " + (child.text or "")
                    break
            results[tid] = (status, msg.strip()[:300])
    return results


def verify_red(before: list[str], after: list[str]) -> int:
    old, new = read_junit(before), read_junit(after)
    added = {t: r for t, r in new.items() if t not in old}
    if not new:
        print("RED gate: no test results found in --after. Run the suite with JUnit XML output.")
        return 1
    if not added:
        print("RED gate FAILED: no new tests were found. Write failing tests before implementing.")
        return 1
    problems = []
    for tid, (status, msg) in sorted(added.items()):
        if status == "passed":
            problems.append(f"VACUOUS  {tid} passes before implementation - tautological, or the "
                            f"behaviour already exists (then keep it as a regression test and say so).")
        elif status == "skipped":
            problems.append(f"SKIPPED  {tid} - new tests must run and fail.")
        elif LOAD_ERRORS.search(msg):
            problems.append(f"WRONG REASON  {tid} fails because the test couldn't load or the app "
                            f"couldn't be built ({msg[:120]}). The implementer must add the missing "
                            f"public operations as stubs that throw 'not implemented'.")
    regressions = [t for t, (s, _) in old.items() if s == "passed" and new.get(t, ("missing",))[0] != "passed"]
    print(f"RED gate: {len(added)} new test(s); {sum(1 for s, _ in added.values() if s in ('failed', 'error'))} failing.")
    for p in problems:
        print("  " + p)
    for t in regressions:
        print(f"  NOTE  previously passing test now not passing: {t}")
    return 1 if problems else 0


def _changed_tests_since(rev: str, cfg: dict, root: Path) -> list[str]:
    def git(*args: str) -> list[str]:
        out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
        return [line for line in out.stdout.splitlines() if line]
    changed = git("diff", "--name-only", rev) + git("ls-files", "--others", "--exclude-standard")
    return sorted({p for p in changed if is_test(p, cfg) and not ARTEFACT.search(p)})


def verify_green(since: str, results: list[str]) -> int:
    root = _root()
    cfg = _boundary(root)
    ok = True
    touched = _changed_tests_since(since, cfg, root)
    if touched:
        ok = False
        print("GREEN gate FAILED: test files changed after the red commit (tests belong to test_writer):")
        for t in touched:
            print(f"  {t}")
    res = read_junit(results)
    if not res:
        print("GREEN gate FAILED: no test results found. Run the suite with JUnit XML output.")
        return 1
    bad = {t: r for t, r in res.items() if r[0] in ("failed", "error")}
    skipped = [t for t, r in res.items() if r[0] == "skipped"]
    if bad:
        ok = False
        print(f"GREEN gate FAILED: {len(bad)} test(s) not passing:")
        for t, (s, m) in sorted(bad.items())[:20]:
            print(f"  {s.upper()}  {t}  {m[:120]}")
    print(f"GREEN gate: {len(res)} tests, {len(res) - len(bad) - len(skipped)} passing, "
          f"{len(skipped)} skipped; tests unchanged since {since}: {'yes' if not touched else 'NO'}.")
    return 0 if ok else 1


# ---------------------------------------------------------------- task
TRAILER = re.compile(r"^(TDD-[A-Za-z-]+):[ \t]*(.+?)\s*$", re.M)


def _task_commits(base: str, root: Path) -> list[dict]:
    out = subprocess.run(["git", "log", "--reverse", "--format=%H%x1f%B%x1e", f"{base}..HEAD"],
                         cwd=root, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"git log failed: {out.stderr.strip()}")
    commits = []
    for chunk in out.stdout.split("\x1e"):
        if not chunk.strip():
            continue
        sha, _, body = chunk.strip("\n").partition("\x1f")
        files = subprocess.run(["git", "show", "--name-only", "--format=", sha], cwd=root,
                               capture_output=True, text=True).stdout.split()
        trailers = {}
        for key, value in TRAILER.findall(body):
            trailers.setdefault(key, []).append(value)
        commits.append({"sha": sha[:10], "subject": body.splitlines()[0] if body else "",
                        "trailers": trailers, "files": files})
    return commits


def verify_task(base: str) -> int:
    root = _root()
    commits = _task_commits(base, root)
    problems = []
    if not commits:
        print(f"TASK gate FAILED: no commits since {base}.")
        return 1

    def index_of(key: str, value: str | None = None) -> int:
        for i, c in enumerate(commits):
            vals = c["trailers"].get(key, [])
            if vals and (value is None or any(v.upper() == value for v in vals)):
                return i
        return -1

    red, no_test = index_of("TDD-Step", "RED"), index_of("TDD-No-Test")
    green = index_of("TDD-Step", "GREEN")
    last = commits[-1]
    review = [v.upper() for v in last["trailers"].get("TDD-Review", [])]

    if red < 0 and no_test < 0:
        problems.append("no test_writer step: expected a commit with 'TDD-Step: red' or 'TDD-No-Test: <reason>'.")
    if green < 0:
        problems.append("no implementer step: expected a commit with 'TDD-Step: green'.")
    elif red >= 0 and green < red:
        problems.append("the green commit comes before the red commit - tests must be written first.")
    if "PASS" not in review:
        problems.append("the last commit must carry 'TDD-Review: PASS' from architecture_reviewer "
                        f"(found: {', '.join(review) or 'none'}).")
    elif last["files"]:
        problems.append("the review commit changes files - code changed after the review. Re-run "
                        "architecture_reviewer and record its verdict in an empty commit.")
    if green >= 0 and len(commits) - 1 <= green and "PASS" in review:
        problems.append("the review must come after the implementation, in its own commit.")

    steps = []
    for c in commits:
        tags = ", ".join(f"{k.replace('TDD-', '')}={'/'.join(v)}" for k, v in c["trailers"].items()) or "-"
        steps.append(f"  {c['sha']}  {c['subject'][:60]}  [{tags}]")
    print(f"TASK gate: {len(commits)} commit(s) since {base}")
    print("\n".join(steps))
    for prob in problems:
        print(f"  FAILED  {prob}")
    if not problems:
        print("  OK  test_writer -> implementer -> architecture_reviewer (PASS)")
    return 1 if problems else 0


# ---------------------------------------------------------------- cli
def _opt(args: list[str], name: str) -> list[str]:
    if name not in args:
        return []
    i = args.index(name) + 1
    vals = []
    while i < len(args) and not args[i].startswith("--"):
        vals.append(args[i])
        i += 1
    return vals


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "hook":
        try:
            data = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            return 0  # fail open on malformed input rather than block the agent
        role = rest[0] if rest else ""
        return hook_test_writer(data) if role == "test-writer" else hook_implementer(data) \
            if role == "implementer" else 0
    if cmd == "verify-red":
        return verify_red(_opt(rest, "--before"), _opt(rest, "--after"))
    if cmd == "verify-green":
        since = _opt(rest, "--since")
        if not since:
            print("verify-green needs --since <red-commit>")
            return 2
        return verify_green(since[0], _opt(rest, "--results"))
    if cmd == "verify-task":
        base = _opt(rest, "--base")
        if not base:
            print("verify-task needs --base <commit before the task started>")
            return 2
        return verify_task(base[0])
    if cmd == "is-test" and rest:
        cfg = _boundary(_root())
        rel = _rel(rest[0], _root())
        print("test" if is_test(rel, cfg) else "implementation" if is_implementation(rel, cfg) else "other")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
