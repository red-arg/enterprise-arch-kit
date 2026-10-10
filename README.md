# Enterprise Architecture Kit for Claude Code and Codex

Subagents and skills that help developers who build fast with AI ("vibe
coders") stay aligned with your enterprise architecture, standards and tech
stack — **without** blocking them. One shared source generates native files
for both **Claude Code** and **OpenAI Codex**.

> **Status:** the standards under `src/skills/enterprise-standards/references/`
> are illustrative placeholders marked `TODO`. Replace them with your real
> standards before rolling out.

## What's inside

### Skills (identical format in both tools)

| Skill | What it does |
| --- | --- |
| `enterprise-standards` | The source of truth: principles (`AP-*`, `NN-*`), patterns (`PAT-*`), coding standards (`CS-*`), NFRs (`NFR-*`) and the tech radar (`STK-*`, `stack.json`). Every rule has a stable ID. |
| `stack-check` | "Can I use X?" answers and a stdlib-only script that audits package.json, requirements, pyproject, go.mod, pom.xml, Gradle and .csproj against the radar — and tells new usage from existing. |
| `scaffold-service` | Starts new APIs, frontends, workers and jobs on a golden path with auth, config, logging, OTel, CI, Dockerfile and ADRs wired in. |
| `architecture-review` | Checklist and report format: verdict, must-fix, deviations (fix or ADR), unassessed, recommendations — each with `file:line` and a standard ID. |
| `write-adr` | Numbered ADRs in `docs/adr/`, including *exception* ADRs with standards affected, expiry and exit plan. |
| `readability-review` | Readability and ease-of-change review using *The Pragmatic Programmer* principles (`RD-01`–`RD-16`: ETC, DRY, orthogonality, tell-don't-ask, naming, crash early…), capped at the 7 most valuable findings with before/after suggestions. |

### Subagents

| Agent | Role | Access |
| --- | --- | --- |
| `solution_designer` | Turns an idea into a one-to-two-page design brief in `docs/design/` on the approved stack, before code. | Writes docs only |
| `stack_guardian` | Fast dependency audit with approved alternatives. | Read-only, cheap model |
| `architecture_reviewer` | Reviews a branch/PR/design against the standards. | Read-only, high effort |
| `adr_scribe` | Records decisions and exceptions as ADRs. | Writes `docs/adr/` |
| `readability_reviewer` | Reviews implemented code for readability and ease of change (Pragmatic Programmer). Runs alongside `architecture_reviewer` when a feature is done. | Read-only |

### Project instructions

A short block added to `AGENTS.md` (and imported from `CLAUDE.md`) tells the
main agent to default to the standards, follow **guide, don't block**, and
delegate to the agents above automatically — which matters for Codex, since
it only spawns subagents when asked or when `AGENTS.md` says to.

## How "guide, don't block" works

1. Default to `adopt` technologies and golden paths; cite the standard in one line.
2. Off-standard request → explain why the standard exists, offer the compliant option.
3. Developer still wants it → proceed and offer an **exception ADR**.
4. Non-negotiables (`NN-*`: secrets in code, prod data in non-prod,
   unauthenticated external endpoints, unapproved registries) → explain and stop.

## Quick start

Requires Python 3.11+ (standard library only).

```bash
git clone <this repo> && cd enterprise-arch-kit

# 1. Make the standards yours
#    edit src/skills/enterprise-standards/references/*.md and stack.json

# 2. Generate both packages
python3 build.py

# 3. Install into a project (both tools)…
python3 install.py /path/to/project
#    …or one tool, or for every project on your machine
python3 install.py /path/to/project --claude
python3 install.py /path/to/project --codex
python3 install.py --user

# Remove again
python3 install.py /path/to/project --uninstall
```

The installer only touches the kit's own agents/skills and a marked block in
`AGENTS.md`/`CLAUDE.md`; your other files and content are kept. Re-run it to
update. Commit the installed files so the whole team gets them.

## Where things land

| | Claude Code | Codex |
| --- | --- | --- |
| Subagents | `.claude/agents/<name>.md` (YAML frontmatter + prompt) | `.codex/agents/<name>.toml` (`developer_instructions`) |
| Skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Instructions | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` |
| User scope (`--user`) | `~/.claude/…` | `~/.codex/agents`, `~/.agents/skills`, `~/.codex/AGENTS.md` |

## Using it

Most of the time developers don't need to do anything — the instructions
trigger the right agent. To call things directly:

| Goal | Claude Code | Codex |
| --- | --- | --- |
| Design before building | "Use the solution_designer agent to design a leave-request app" | "Spawn solution_designer to design a leave-request app" |
| Start a project | `/scaffold-service` | `$scaffold-service` |
| Can I use X? | `/stack-check can I use MongoDB?` | `$stack-check can I use MongoDB?` |
| Review my branch | `@"architecture_reviewer (agent)" review this branch` | "Spawn architecture_reviewer to review this branch vs main" |
| Readability review | `@"readability_reviewer (agent)" review my changes` or `/readability-review` | "Spawn readability_reviewer to review my changes" or `$readability-review` |
| Record an exception | "Have adr_scribe record an exception for using Flask" | "Spawn adr_scribe to record an exception for using Flask" |

CI example (fails on retired or newly-added hold dependencies):

```bash
python3 .agents/skills/stack-check/scripts/check_stack.py . --since origin/main --strict
```

## Customizing

All authoring happens in `src/`; `dist/` is generated (CI fails if it's stale).

```
src/
  instructions/AGENTS.md            # project instructions block
  skills/<name>/SKILL.md            # Agent Skills standard; may use {{#claude}}…{{/claude}} / {{#codex}}…{{/codex}}
  agents/<name>/agent.toml          # name, description, skills + [claude] and [codex] settings
  agents/<name>/prompt.md           # the agent's instructions (same platform blocks)
```

`agent.toml` maps to each tool like this:

| `agent.toml` | Claude Code | Codex |
| --- | --- | --- |
| `name`, `description` | frontmatter | `name`, `description` |
| `skills` | `skills:` (preloaded) | "load these skills" line prepended to `developer_instructions` |
| `[claude] tools` | `tools:` allowlist | — (use `sandbox_mode`) |
| `[claude] model`, `effort`, `color` | same fields | — |
| `[codex] sandbox_mode`, `model_reasoning_effort`, `model` | — | same keys |
| `prompt.md` | Markdown body (system prompt) | `developer_instructions` |

Tips:

- **Keep IDs stable** once published; ADRs and code comments reference them.
- **Start with your golden paths.** If you have starter repos, point
  `scaffold-service/references/golden-paths.md` at them and tell the skill to
  clone instead of generate.
- **Have real templates?** Swap illustrative defaults in `stack.json` for your
  radar; `tech-stack.md` is regenerated from it.
- Agent names use `snake_case` so the same names work in both tools and the
  shared `AGENTS.md` can refer to them.
- Codex models aren't pinned (agents inherit the parent model); set `model`
  under `[codex]` if you want e.g. a faster model for `stack_guardian`.

## Repository layout

```
build.py      # src/ → dist/claude, dist/codex (validates names, tools, TOML, stack.json)
install.py    # dist/ → a project or your home folder
src/          # edit here
dist/         # generated, committed for convenience
.github/workflows/check.yml   # build --check + checker smoke test
```
