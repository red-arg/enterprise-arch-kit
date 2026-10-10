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

import re
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


TIMESTAMP_RE = re.compile(r'"(installed_at|updated_at)":\s*"[^"]*"')


def _normalized(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix == ".json" or path.name == ".registry":
        data = TIMESTAMP_RE.sub(r'"\1": "<ts>"', data.decode("utf-8")).encode("utf-8")
    return data


def trees_equal(a: Path, b: Path) -> bool:
    """Compare two starter trees, ignoring Spec Kit install timestamps."""
    files_a = {p.relative_to(a) for p in a.rglob("*") if p.is_file()}
    files_b = {p.relative_to(b) for p in b.rglob("*") if p.is_file()}
    if files_a != files_b:
        return False
    return all(_normalized(a / f) == _normalized(b / f) for f in files_a)


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
            if not OUT.exists() or not trees_equal(fresh, OUT):
                print("starter/ is out of date. Run: python3 make_starter.py", file=sys.stderr)
                return 1
        print("starter/ is up to date.")
        return 0

    generate(OUT)
    files = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"Generated starter/ ({files} files) with Spec Kit {version}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
