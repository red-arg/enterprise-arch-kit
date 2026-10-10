#!/usr/bin/env python3
"""Install the kit into a project (or your user profile) for Claude Code and/or Codex.

    python3 install.py /path/to/project            # both tools, project scope
    python3 install.py /path/to/project --claude   # Claude Code only
    python3 install.py /path/to/project --codex    # Codex only
    python3 install.py --user                      # both tools, for every project on this machine
    python3 install.py /path/to/project --uninstall

What it does
  - Copies the kit's agents and skills into the tool's folders. Only the kit's
    own agents/skills are replaced; anything else you have there is untouched.
  - Adds (or refreshes) a marked block in AGENTS.md / CLAUDE.md. Your existing
    content in those files is kept. When both tools are installed, CLAUDE.md
    imports AGENTS.md instead of duplicating it.

Run `python3 build.py` first if you changed anything under src/.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
START = "<!-- enterprise-arch-kit:start -->"
END = "<!-- enterprise-arch-kit:end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
# Agents shipped by earlier versions of the kit, removed on install/uninstall.
LEGACY_AGENTS = ["adr_scribe"]


def targets(project: Path | None, user: bool) -> dict:
    home = Path.home()
    if user:
        return {
            "claude": {"agents": home / ".claude/agents", "skills": home / ".claude/skills",
                       "instructions": home / ".claude/CLAUDE.md"},
            "codex": {"agents": home / ".codex/agents", "skills": home / ".agents/skills",
                      "instructions": home / ".codex/AGENTS.md"},
        }
    assert project is not None
    return {
        "claude": {"agents": project / ".claude/agents", "skills": project / ".claude/skills",
                   "instructions": project / "CLAUDE.md"},
        "codex": {"agents": project / ".codex/agents", "skills": project / ".agents/skills",
                  "instructions": project / "AGENTS.md"},
    }


def set_block(path: Path, body: str | None) -> None:
    """Insert/replace the kit's marked block in a Markdown file (None removes it)."""
    existing = path.read_text() if path.exists() else ""
    stripped = BLOCK_RE.sub("", existing)
    if body is None:
        if path.exists():
            if stripped.strip():
                path.write_text(stripped)
            else:
                path.unlink()
        return
    block = f"{START}\n{body.rstrip()}\n{END}\n"
    if BLOCK_RE.search(existing):
        new = BLOCK_RE.sub(lambda _: block, existing)
    else:
        new = (existing.rstrip() + "\n\n" if existing.strip() else "") + block
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new)


def kit_items(platform: str) -> tuple[list[Path], list[Path]]:
    base = DIST / platform
    agents_dir = base / (".claude/agents" if platform == "claude" else ".codex/agents")
    skills_dir = base / (".claude/skills" if platform == "claude" else ".agents/skills")
    return sorted(agents_dir.iterdir()), sorted(p for p in skills_dir.iterdir() if p.is_dir())


def install(platform: str, t: dict, both: bool, uninstall: bool) -> list[str]:
    agents, skills = kit_items(platform)
    done = []
    ext = ".md" if platform == "claude" else ".toml"
    for legacy in LEGACY_AGENTS:
        (t["agents"] / f"{legacy}{ext}").unlink(missing_ok=True)
    for a in agents:
        dest = t["agents"] / a.name
        if uninstall:
            dest.unlink(missing_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(a, dest)
        done.append(str(dest))
    for s in skills:
        dest = t["skills"] / s.name
        if dest.exists():
            shutil.rmtree(dest)
        if not uninstall:
            shutil.copytree(s, dest)
        done.append(str(dest) + "/")
    if uninstall:
        set_block(t["instructions"], None)
        for d in (t["agents"], t["skills"]):  # remove folders the kit left empty
            for folder in (d, d.parent):
                if folder.is_dir() and not any(folder.iterdir()):
                    folder.rmdir()
    elif platform == "claude" and both:
        # Claude Code imports the Codex AGENTS.md so both tools share one copy.
        user_scope = t["instructions"] == Path.home() / ".claude/CLAUDE.md"
        set_block(t["instructions"], "@~/.codex/AGENTS.md" if user_scope else "@AGENTS.md")
    else:
        src = DIST / platform / ("CLAUDE.md" if platform == "claude" else "AGENTS.md")
        set_block(t["instructions"], src.read_text())
    done.append(str(t["instructions"]))
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?", type=Path)
    ap.add_argument("--claude", action="store_true", help="install for Claude Code")
    ap.add_argument("--codex", action="store_true", help="install for Codex")
    ap.add_argument("--user", action="store_true", help="install into your home folder instead of a project")
    ap.add_argument("--uninstall", action="store_true", help="remove the kit's files and instruction block")
    args = ap.parse_args()

    if not DIST.exists():
        print("dist/ not found — run: python3 build.py", file=sys.stderr)
        return 1
    if args.user == (args.project is not None):
        ap.error("give a project folder, or --user (not both)")
    if args.project is not None and not args.project.is_dir():
        ap.error(f"{args.project} is not a folder")

    platforms = [p for p in ("codex", "claude") if getattr(args, p)] or ["codex", "claude"]
    both = len(platforms) == 2
    t = targets(args.project.resolve() if args.project else None, args.user)
    verb = "Removed" if args.uninstall else "Installed"
    for p in platforms:  # codex first so AGENTS.md exists before CLAUDE.md imports it
        paths = install(p, t[p], both, args.uninstall)
        name = "Claude Code" if p == "claude" else "Codex"
        print(f"{verb} for {name}:")
        for path in paths:
            print(f"  {path}")
    if not args.uninstall:
        print("\nNext: edit the standards in src/skills/enterprise-standards/references/, "
              "run build.py, and re-run this installer to update.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
