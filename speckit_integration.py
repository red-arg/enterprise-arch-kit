"""Spec Kit (github/spec-kit) integration for the enterprise architecture kit.

Used by install.py --speckit. Standard library only.

What it does in a project:
  1. Initializes Spec Kit if needed (`specify init`) and installs the
     integrations for the requested tools (claude, codex).
  2. Installs (or refreshes) the `enterprise-arch-kit` preset from
     dist/speckit-preset with `specify preset add --dev`.
  3. Spec Kit 1.x applies preset skill overrides only to the *active*
     integration. When both Claude Code and Codex are installed, the composed
     speckit-* skills are mirrored to the other integration, adjusting the
     invocation prefix (`/speckit-` for Claude Code, `$speckit-` for Codex).
  4. Replaces the constitution with the enterprise one, but only if the live
     file is still the untouched generated template (same provenance rule
     Spec Kit uses). Authored constitutions are never overwritten.

Uninstall removes the preset and re-renders the core speckit-* skills for
every installed integration.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

PRESET_ID = "enterprise-arch-kit"
SKILLS_DIR = {"claude": ".claude/skills", "codex": ".agents/skills"}
INVOKE_PREFIX = {"claude": "/speckit-", "codex": "$speckit-"}


class SpecKitError(Exception):
    pass


def _run(cmd: list[str], cwd: Path) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SpecKitError(f"`{' '.join(cmd)}` failed:\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")
    return proc.stdout


def find_specify() -> str:
    exe = shutil.which("specify")
    if not exe:
        raise SpecKitError(
            "Spec Kit's `specify` CLI was not found. Install it first, e.g.\n"
            "  uv tool install specify-cli     (or: pipx install specify-cli)\n"
            "then re-run with --speckit.")
    return exe


def _integration_state(project: Path) -> dict:
    p = project / ".specify" / "integration.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _preset_version(preset_dir: Path) -> str:
    m = re.search(r'^\s*version:\s*"?([^"\n]+)"?', (preset_dir / "preset.yml").read_text(), re.M)
    return m.group(1).strip() if m else "0.0.0"


def _preset_commands(preset_dir: Path) -> list[str]:
    """Command names (e.g. speckit.plan) the preset composes onto."""
    text = (preset_dir / "preset.yml").read_text()
    names = []
    for block in re.split(r"\n\s*-\s+type:", text)[1:]:
        if block.strip().startswith('"command"') or block.strip().startswith("command"):
            m = re.search(r'name:\s*"?([\w.]+)"?', block)
            if m:
                names.append(m.group(1))
    return names


def _split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[: end + 5], text[end + 5:]
    return "", text


def _command_description(preset_dir: Path, command: str) -> str | None:
    f = preset_dir / "commands" / f"{command}.md"
    if not f.exists():
        return None
    fm, _ = _split_frontmatter(f.read_text())
    m = re.search(r"^description:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else None


def _replace_description(frontmatter: str, desc: str) -> str:
    """Replace a (possibly multi-line) top-level description in YAML frontmatter."""
    lines = frontmatter.splitlines(keepends=True)
    out, skipping = [], False
    for line in lines:
        if skipping:
            if line.startswith((" ", "\t")):
                continue
            skipping = False
        if line.startswith("description:"):
            out.append(f"description: {json.dumps(desc)}\n")
            skipping = True
            continue
        out.append(line)
    return "".join(out)


def mirror_skills(project: Path, preset_dir: Path, source: str, targets: list[str]) -> list[str]:
    """Copy composed speckit-* skill bodies from the active integration to others."""
    written = []
    for command in _preset_commands(preset_dir):
        skill = command.replace(".", "-")
        src = project / SKILLS_DIR[source] / skill / "SKILL.md"
        if not src.exists():
            continue
        _, body = _split_frontmatter(src.read_text())
        desc = _command_description(preset_dir, command)
        for target in targets:
            dst = project / SKILLS_DIR[target] / skill / "SKILL.md"
            if not dst.exists():
                continue
            fm, _ = _split_frontmatter(dst.read_text())
            if desc:
                fm = _replace_description(fm, desc)
            new_body = body.replace(INVOKE_PREFIX[source], INVOKE_PREFIX[target])
            dst.write_text(fm + new_body)
            written.append(str(dst.relative_to(project)))
    return written


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply_constitution(project: Path, preset_dir: Path) -> str:
    live = project / ".specify" / "memory" / "constitution.md"
    prov = live.parent / ".constitution-template.json"
    ours = (preset_dir / "templates" / "constitution-template.md").read_bytes()
    if live.exists():
        try:
            recorded = json.loads(prov.read_text()).get("sha256") if prov.exists() else None
        except (json.JSONDecodeError, OSError):
            recorded = None
        if recorded != _sha(live.read_bytes()):
            return "kept (project constitution has been edited)"
        if live.read_bytes() == ours:
            return "already enterprise"
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_bytes(ours)
    prov.write_text(json.dumps({"sha256": _sha(ours),
                                "source": f"{PRESET_ID} v{_preset_version(preset_dir)}"}, indent=2) + "\n")
    return "replaced with the enterprise constitution"


def setup(project: Path, preset_dir: Path, platforms: list[str]) -> list[str]:
    specify = find_specify()
    report = []
    state = _integration_state(project)
    if not state:
        first, rest = platforms[0], platforms[1:]
        _run([specify, "init", "--here", "--force", "--non-interactive",
              "--ignore-agent-tools", "--integration", first], project)
        report.append(f"Spec Kit initialized ({first})")
        state = _integration_state(project)
    else:
        rest = platforms
    installed = set(state.get("installed_integrations", []))
    for p in rest:
        if p not in installed:
            _run([specify, "integration", "install", p], project)
            report.append(f"Spec Kit integration added ({p})")
    state = _integration_state(project)
    installed = [p for p in state.get("installed_integrations", []) if p in SKILLS_DIR]
    active = state.get("integration") or state.get("default_integration")

    listed = _run([specify, "preset", "list"], project)
    if PRESET_ID in listed:
        _run([specify, "preset", "remove", PRESET_ID], project)
    _run([specify, "preset", "add", "--dev", str(preset_dir)], project)
    report.append(f"Preset {PRESET_ID} v{_preset_version(preset_dir)} installed (active: {active})")

    others = [p for p in installed if p != active]
    if active in SKILLS_DIR and others:
        mirrored = mirror_skills(project, preset_dir, active, others)
        report.append(f"Preset skills mirrored to {', '.join(others)} ({len(mirrored)} files)")

    report.append("Constitution " + apply_constitution(project, preset_dir))
    return report


def teardown(project: Path) -> list[str]:
    if not (project / ".specify").exists():
        return []
    specify = find_specify()
    report = []
    if PRESET_ID in _run([specify, "preset", "list"], project):
        _run([specify, "preset", "remove", PRESET_ID], project)
        report.append(f"Preset {PRESET_ID} removed")
    for p in _integration_state(project).get("installed_integrations", []):
        if p in SKILLS_DIR:
            _run([specify, "integration", "upgrade", p, "--force"], project)
            report.append(f"Core speckit skills restored ({p})")
    report.append("Spec Kit itself and the constitution were left in place")
    return report
