#!/usr/bin/env python3
"""Check a repository's dependencies against the approved tech stack.

Reads dependency manifests (package.json, requirements*.txt, pyproject.toml,
go.mod, pom.xml, build.gradle[.kts], *.csproj) and classifies every dependency
as adopt / trial / hold / retire / unassessed using stack.json.

Standard library only. Python 3.11+.

Usage:
  check_stack.py [REPO_DIR] [--stack PATH] [--since GIT_REF] [--json] [--strict]

  --since REF   Also mark which dependencies are NEW compared to REF
                (e.g. origin/main). Hold/retire matters most for new ones.
  --strict      Exit 1 if any retire dependency, or any NEW hold dependency
                (or any hold dependency when --since is not given).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "dist", "build",
             "target", ".next", "__pycache__", ".tox", "vendor", "bin", "obj",
             ".gradle", ".idea", ".claude", ".codex", ".agents"}
STATUS_ORDER = ["retire", "hold", "unassessed", "trial", "adopt"]


def default_stack_path() -> Path:
    here = Path(__file__).resolve()
    return here.parent.parent.parent / "enterprise-standards" / "references" / "stack.json"


# ---------------------------------------------------------------- parsers
def norm_py(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_package_json(text: str) -> list[tuple[str, str]]:
    data = json.loads(text)
    out = []
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        for name in (data.get(key) or {}):
            out.append(("npm", name))
    return out


REQ_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def parse_requirements(text: str) -> list[tuple[str, str]]:
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue
        m = REQ_RE.match(line)
        if m:
            out.append(("pypi", norm_py(m.group(1))))
    return out


def parse_pyproject(text: str) -> list[tuple[str, str]]:
    data = tomllib.loads(text)
    names: list[str] = []
    proj = data.get("project", {})
    names += proj.get("dependencies", [])
    for group in (proj.get("optional-dependencies") or {}).values():
        names += group
    for group in (data.get("dependency-groups") or {}).values():
        names += [g for g in group if isinstance(g, str)]
    poetry = data.get("tool", {}).get("poetry", {})
    names += [n for n in (poetry.get("dependencies") or {}) if n.lower() != "python"]
    names += list((poetry.get("dev-dependencies") or {}))
    for grp in (poetry.get("group") or {}).values():
        names += list((grp.get("dependencies") or {}))
    out = []
    for n in names:
        m = REQ_RE.match(n)
        if m:
            out.append(("pypi", norm_py(m.group(1))))
    return out


def parse_go_mod(text: str) -> list[tuple[str, str]]:
    out = []
    in_block = False
    for line in text.splitlines():
        s = line.split("//", 1)[0].strip()
        if s.startswith("require ("):
            in_block = True
            continue
        if in_block and s == ")":
            in_block = False
            continue
        if in_block and s:
            out.append(("go", s.split()[0]))
        elif s.startswith("require "):
            parts = s.split()
            if len(parts) >= 2:
                out.append(("go", parts[1]))
    return out


def parse_pom(text: str) -> list[tuple[str, str]]:
    root = ET.fromstring(text)
    out = []
    for dep in root.iter():
        if not dep.tag.endswith("dependency"):
            continue
        g = a = None
        for child in dep:
            if child.tag.endswith("groupId"):
                g = (child.text or "").strip()
            elif child.tag.endswith("artifactId"):
                a = (child.text or "").strip()
        if g and a:
            out.append(("maven", f"{g}:{a}"))
    return out


GRADLE_RE = re.compile(r"""(?:implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly|annotationProcessor|kapt)\s*\(?\s*["']([^:"']+):([^:"']+)""")


def parse_gradle(text: str) -> list[tuple[str, str]]:
    return [("maven", f"{g}:{a}") for g, a in GRADLE_RE.findall(text)]


def parse_csproj(text: str) -> list[tuple[str, str]]:
    root = ET.fromstring(text)
    return [("nuget", el.get("Include")) for el in root.iter()
            if el.tag.endswith("PackageReference") and el.get("Include")]


def parser_for(path: Path):
    n = path.name
    if n == "package.json":
        return parse_package_json
    if n.startswith("requirements") and n.endswith(".txt"):
        return parse_requirements
    if n == "pyproject.toml":
        return parse_pyproject
    if n == "go.mod":
        return parse_go_mod
    if n == "pom.xml":
        return parse_pom
    if n in ("build.gradle", "build.gradle.kts"):
        return parse_gradle
    if n.endswith(".csproj"):
        return parse_csproj
    return None


def find_manifests(repo: Path) -> list[Path]:
    found = []
    for p in repo.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(repo).parts[:-1]):
            continue
        if p.is_file() and parser_for(p):
            found.append(p)
    return sorted(found)


def deps_from(path_label: str, text: str, parser) -> set[tuple[str, str]]:
    try:
        return set(parser(text))
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"warning: could not parse {path_label}: {exc}", file=sys.stderr)
        return set()


def git_show(repo: Path, ref: str, rel: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"],
                              capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ---------------------------------------------------------------- classify
def classify(ecosystem: str, name: str, packages: dict) -> str:
    eco = packages.get(ecosystem, {})
    key = norm_py(name) if ecosystem == "pypi" else name
    # Check the most restrictive statuses first so a specific hold/retire
    # entry wins over a broad adopt wildcard.
    for status in ("retire", "hold", "trial", "adopt"):
        for pattern in eco.get(status, []):
            pat = norm_py(pattern) if ecosystem == "pypi" else pattern
            if fnmatch.fnmatchcase(key, pat):
                return status
    return "unassessed"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--stack", type=Path, default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    stack_path = args.stack or default_stack_path()
    if not stack_path.exists():
        print(f"error: stack file not found: {stack_path}", file=sys.stderr)
        return 2
    packages = json.loads(stack_path.read_text())["packages"]

    rows = []
    for manifest in find_manifests(repo):
        rel = manifest.relative_to(repo).as_posix()
        parser = parser_for(manifest)
        current = deps_from(rel, manifest.read_text(encoding="utf-8", errors="replace"), parser)
        previous: set[tuple[str, str]] | None = None
        if args.since:
            old = git_show(repo, args.since, rel)
            previous = deps_from(f"{args.since}:{rel}", old, parser) if old is not None else set()
        for eco, name in sorted(current):
            rows.append({
                "manifest": rel,
                "ecosystem": eco,
                "package": name,
                "status": classify(eco, name, packages),
                "new": None if previous is None else (eco, name) not in previous,
            })

    rows.sort(key=lambda r: (STATUS_ORDER.index(r["status"]), r["manifest"], r["package"]))
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUS_ORDER}

    blocking = [r for r in rows if r["status"] == "retire"
                or (r["status"] == "hold" and (r["new"] is None or r["new"]))]

    if args.json:
        print(json.dumps({"stack": str(stack_path), "since": args.since,
                          "counts": counts, "dependencies": rows}, indent=2))
    else:
        print(f"# Stack check — {repo.name}\n")
        print(f"Stack file: `{stack_path}`" + (f" · compared with `{args.since}`" if args.since else ""))
        print("\n" + " · ".join(f"{s}: {counts[s]}" for s in STATUS_ORDER) + "\n")
        if not rows:
            print("No dependency manifests found.")
        else:
            new_col = args.since is not None
            print("| Status | Package | Ecosystem | Manifest |" + (" New? |" if new_col else ""))
            print("| --- | --- | --- | --- |" + (" --- |" if new_col else ""))
            for r in rows:
                if r["status"] == "adopt":
                    continue  # keep the table focused on what needs attention
                line = f"| {r['status'].upper()} | `{r['package']}` | {r['ecosystem']} | {r['manifest']} |"
                if new_col:
                    line += " yes |" if r["new"] else " no |"
                print(line)
            print(f"\n({counts['adopt']} adopt dependencies not listed.)")

    if args.strict and blocking:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
