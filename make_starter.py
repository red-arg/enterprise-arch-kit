#!/usr/bin/env python3
"""Generate starter/: a ready-to-use template project for vibe coders.

    python3 make_starter.py           # (re)generate starter/
    python3 make_starter.py --check   # exit 1 if starter/ is out of date (for CI)

The starter contains, pre-installed for Claude Code and Codex:
  - the kit's agents, skills and AGENTS.md / CLAUDE.md rules (from dist/)
  - GitHub Spec Kit with the enterprise-arch-kit preset and constitution
  - a dev container so it runs in GitHub Codespaces with nothing to install
  - START-HERE.md, a plain-language welcome page

Publish it as a GitHub template repository (see README, "Starter template").
Requires the Spec Kit CLI (`specify`); run `python3 build.py` first.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "starter"
STARTER_SRC = ROOT / "src" / "starter"
SPECKIT_VERSION = "1.1.3"  # version the starter is generated and tested with


def specify_version() -> str | None:
    exe = shutil.which("specify")
    if not exe:
        return None
    out = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout
    return out.strip().split()[-1] if out.strip() else "unknown"


def generate(dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "starter"
        work.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=work, check=True)
        shutil.copytree(STARTER_SRC, work, dirs_exist_ok=True)
        proc = subprocess.run([sys.executable, str(ROOT / "install.py"), str(work), "--speckit"],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"install.py failed:\n{proc.stdout}\n{proc.stderr}")
        shutil.rmtree(work / ".git")
        for junk in work.rglob("__pycache__"):
            shutil.rmtree(junk, ignore_errors=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(work, dest, symlinks=True)


VOLATILE_KEYS = {"installed_at", "updated_at"}


def _strip_volatile(value):
    if isinstance(value, dict):
        return {k: _strip_volatile(v) for k, v in value.items() if k not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [_strip_volatile(v) for v in value]
    return value


def _normalized(path: Path) -> bytes:
    """File content for comparison. Spec Kit's JSON state files carry install
    timestamps and list files in filesystem order, which differs between
    machines, so JSON is compared as data with sorted keys and no timestamps."""
    data = path.read_bytes()
    if path.suffix == ".json" or path.name == ".registry":
        try:
            parsed = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return data
        return json.dumps(_strip_volatile(parsed), sort_keys=True, indent=1).encode("utf-8")
    return data


def tree_differences(fresh: Path, committed: Path) -> list[str]:
    """Describe how two starter trees differ, ignoring Spec Kit install timestamps."""
    import difflib
    files_f = {p.relative_to(fresh) for p in fresh.rglob("*") if p.is_file()}
    files_c = {p.relative_to(committed) for p in committed.rglob("*") if p.is_file()}
    problems = [f"starter/{f}: missing from starter/ (would be generated)" for f in sorted(files_f - files_c)]
    problems += [f"starter/{f}: in starter/ but no longer generated" for f in sorted(files_c - files_f)]
    for f in sorted(files_f & files_c):
        new, old = _normalized(fresh / f), _normalized(committed / f)
        if new != old:
            try:
                diff = list(difflib.unified_diff(old.decode().splitlines(), new.decode().splitlines(),
                                                 "committed", "generated", lineterm="", n=0))
                detail = " | ".join(line for line in diff[2:8])
            except UnicodeDecodeError:
                detail = "binary content differs"
            problems.append(f"starter/{f}: {detail[:400]}")
    return problems


def trees_equal(a: Path, b: Path) -> bool:
    return not tree_differences(a, b)


def main() -> int:
    if not (ROOT / "dist").exists():
        print("dist/ not found — run: python3 build.py", file=sys.stderr)
        return 1
    version = specify_version()
    if version is None:
        print("The Spec Kit CLI (`specify`) is required: pip install specify-cli==" + SPECKIT_VERSION,
              file=sys.stderr)
        return 1
    if version != SPECKIT_VERSION:
        print(f"warning: specify {version} found; the starter is pinned to {SPECKIT_VERSION}. "
              f"Update SPECKIT_VERSION after testing a new version.", file=sys.stderr)

    if "--check" in sys.argv[1:]:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "starter"
            generate(fresh)
            problems = ["starter/ does not exist"] if not OUT.exists() else tree_differences(fresh, OUT)
            if problems:
                annotate = os.environ.get("GITHUB_ACTIONS") == "true"
                print("starter/ is out of date. Run: python3 make_starter.py", file=sys.stderr)
                for problem in problems[:20]:
                    print(("::error::" if annotate else "  ") + problem, file=sys.stderr if not annotate else sys.stdout)
                return 1
        print("starter/ is up to date.")
        return 0

    generate(OUT)
    files = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"Generated starter/ ({files} files) with Spec Kit {version}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
