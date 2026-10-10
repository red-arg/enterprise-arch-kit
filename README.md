# Enterprise Architecture Kit for Claude Code and Codex

Subagents and skills that let people who aren't software engineers ("vibe
coders") build what they need with AI — while the agents quietly make sure
the result can be taken to production on your enterprise standards,
architecture and tech stack with little extra effort.

One shared source generates native files for both **Claude Code** and
**OpenAI Codex**.

> **Status:** the standards under `src/skills/enterprise-standards/references/`
> are illustrative placeholders marked `TODO`. Replace them with your real
> standards before rolling out.

## The idea

| The builder… | The agents… |
| --- | --- |
| Describes what they want and who it's for | Decide every technical detail on the approved stack and golden path |
| Answers a few plain **business** questions ("Who will use it?", "What information does it handle?", "What if it stopped for a day?") | Translate the answers into technical requirements: tier, data classification, access model, scale, integrations, compliance |
| Is never asked to choose a technology or weigh a technical trade-off | Fix code-quality and alignment issues themselves; record everything else for engineers |
| Gets something that runs on their laptop with one command | Structure it so moving to production is mostly configuration, not a rewrite |

Everything an engineering team needs to productionize lives in one living
document, **`docs/production-handoff.md`**: business context, derived
requirements, architecture as built, the status of every swappable
infrastructure piece, decisions and exceptions, and the remaining gaps with
owner and effort.

## How the code stays easy to productionize, change and scale

- **Golden path from day one** — approved language and framework, so nothing
  needs rewriting later.
- **Modules by business capability** (PAT-20) — `leave-requests`,
  `approvals`, not `controllers/` and `models/`. New capability = new module;
  any module can later become its own service.
- **Swappable infrastructure** (PAT-19) — the database, login, secrets,
  messaging, file storage, notifications and every external system sit
  behind interfaces with a **local adapter** (zero setup: embedded database,
  dev login, fake external systems with sample data) and a **production
  adapter** on the enterprise stack. Switching is configuration only, proven
  by shared contract tests.

## What's inside

### Skills (identical format in both tools)

| Skill | What it does |
| --- | --- |
| `enterprise-standards` | Source of truth: principles (`AP-*`, `NN-*`), patterns (`PAT-*`), coding standards (`CS-*`), NFRs (`NFR-*`) and the tech radar (`STK-*`, `stack.json`). Includes the "decide, don't ask" rules. |
| `business-context` | Plain-language business question bank (Q1–Q8) with defaults, and how each answer maps to technical requirements. |
| `production-handoff` | Template and rules for the living production handoff document. |
| `scaffold-service` | Starts new apps/APIs/workers/jobs on a golden path with modules, local + production adapters, one-command local run, CI and the handoff. |
| `stack-check` | Decides whether a technology is allowed, plus a stdlib-only script auditing package.json, requirements, pyproject, go.mod, pom.xml, Gradle and .csproj — new vs existing usage, and `local`-only packages. |
| `architecture-review` | Standards and productionizability review, sorted into *fix now* (main agent), *record for production* (handoff), *business fact needed* and *exceptions*. |
| `readability-review` | *The Pragmatic Programmer* review (`RD-01`–`RD-16`: ETC, DRY, orthogonality, naming, crash early…), sorted into *fix now* and *record*. |
| `write-adr` | ADRs for decisions and exceptions made by the agents on the builder's behalf, awaiting architecture approval. |

### Subagents

| Agent | Role | Access |
| --- | --- | --- |
| `solution_designer` | Identifies the business questions that matter, decides the technical design, writes the design brief and seeds the handoff. | Writes `docs/` only |
| `stack_guardian` | Dependency audit; tells the main agent what to swap. | Read-only, cheap model |
| `architecture_reviewer` | Standards and production-readiness review. | Read-only, high effort |
| `readability_reviewer` | Pragmatic Programmer readability review. | Read-only |
| `handoff_scribe` | Keeps `docs/production-handoff.md` and `docs/adr/` current. | Writes `docs/` only |

### Project instructions

A block added to `AGENTS.md` (and imported from `CLAUDE.md`) sets the
ground rules for the main agent: who decides what, business questions only,
plain-language communication, automatic delegation, fixing review findings
without asking, and keeping the handoff current. This matters for Codex in
particular, which only spawns subagents when asked or when `AGENTS.md` says to.

## The flow

1. **Builder:** "Build me a leave request app for my team."
2. **`solution_designer`** returns up to three business questions (e.g. "What
   information will it handle?") and designs on sensible defaults meanwhile.
   The main agent asks them in plain language.
3. **Main agent** scaffolds on the golden path (`scaffold-service`) and builds
   in thin slices the builder can see, checking every dependency.
4. **`stack_guardian`** runs when dependencies change.
5. **`architecture_reviewer` + `readability_reviewer`** run in parallel when a
   piece of work is done. The main agent applies the *fix now* items itself
   and re-runs them once.
6. **`handoff_scribe`** records business context, decisions, exceptions and
   remaining gaps in the production handoff.
7. **Builder** hears one or two plain sentences, e.g. "It now remembers
   requests and is ready to move to the company database later."

When the builder asks "can this go live?", the agents confirm the assumed
business facts with plain questions and hand the engineering team the
handoff, with a readiness verdict.

## Spec-driven workflow with GitHub Spec Kit (optional)

The kit integrates with [GitHub Spec Kit](https://github.com/github/spec-kit)
through an **`enterprise-arch-kit` preset** (`src/speckit-preset/`). Spec Kit
captures *what and why* before *how*; the preset makes sure the builder only
ever deals with the *what and why*:

| Spec Kit step | What the preset adds |
| --- | --- |
| `speckit-constitution` | Enterprise constitution generated from the standards (decide-don't-ask, approved stack, golden path, swappable infrastructure, production handoff, review gates) — not authored by the builder |
| `speckit-specify` | No technology in specs; a mandatory **Business Context** section (Q1–Q8, Confirmed/Assumed); clarification markers must be business questions |
| `speckit-clarify` | At most 3 plain business questions from the question bank; technical requirements are derived, never asked |
| `speckit-plan` | Delegated to `solution_designer`; technical context decided from the standards; mandatory **Enterprise Alignment** section (derived requirements, golden path, modules, ports, standards trace, exceptions) |
| `speckit-tasks` | Tasks per port and module, contract tests, review and handoff tasks per user story |
| `speckit-implement` | Golden path, `stack-check`, parallel reviews with fix-now applied, handoff updated, plain-language outcome |

The preset composes onto Spec Kit's own commands (`prepend`/`append`), so
core scripts, extension hooks and future Spec Kit updates keep working. The
builder never types these commands: the `AGENTS.md` rules run them when
something new is requested.

```bash
uv tool install specify-cli            # or: pipx install specify-cli
python3 install.py /path/to/project --speckit             # both tools
python3 install.py /path/to/project --claude --speckit    # one tool
```

`--speckit` initializes Spec Kit if needed, installs the preset, and sets the
enterprise constitution — unless the project's constitution has been edited,
in which case it's left alone. Tested with Spec Kit 1.1.3.

> **Note — both tools in one project:** Spec Kit 1.x applies preset skill
> overrides only to its *active* integration. The installer applies the
> preset natively to Claude Code and mirrors the composed skills to Codex
> (adjusting `/speckit-` → `$speckit-`). If you later run
> `specify integration upgrade codex`, re-run the installer.

## Quick start

Requires Python 3.11+ (standard library only).

```bash
git clone https://github.com/red-arg/enterprise-arch-kit && cd enterprise-arch-kit

# 1. Make the standards yours
#    edit src/skills/enterprise-standards/references/*.md and stack.json,
#    and src/skills/business-context/references/question-bank.md

# 2. Generate both packages
python3 build.py

# 3. Install into a project (both tools)…
python3 install.py /path/to/project
#    …or one tool, or for every project on this machine
python3 install.py /path/to/project --claude
python3 install.py /path/to/project --codex
python3 install.py --user

# Remove again
python3 install.py /path/to/project --uninstall
```

The installer only touches the kit's own agents/skills and a marked block in
`AGENTS.md`/`CLAUDE.md`; everything else is kept. Re-run it to update.
For vibe coders, the simplest rollout is `--user` on their machines, or a
starter repo with the kit pre-installed.

## Where things land

| | Claude Code | Codex |
| --- | --- | --- |
| Subagents | `.claude/agents/<name>.md` | `.codex/agents/<name>.toml` |
| Skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Instructions | `CLAUDE.md` → `@AGENTS.md` | `AGENTS.md` |
| User scope (`--user`) | `~/.claude/…` | `~/.codex/agents`, `~/.agents/skills`, `~/.codex/AGENTS.md` |

CI for generated projects (fails on retired or newly added hold dependencies):

```bash
python3 .agents/skills/stack-check/scripts/check_stack.py . --since origin/main --strict
```

## Customizing

All authoring happens in `src/`; `dist/` is generated (CI fails if it's stale).

```
src/
  instructions/AGENTS.md            # ground rules for the main agent
  skills/<name>/SKILL.md            # Agent Skills standard; may use {{#claude}}…{{/claude}} / {{#codex}}…{{/codex}}
  agents/<name>/agent.toml          # name, description, skills + [claude] and [codex] settings
  agents/<name>/prompt.md           # the agent's instructions (same platform blocks)
```

| `agent.toml` | Claude Code | Codex |
| --- | --- | --- |
| `name`, `description` | frontmatter | `name`, `description` |
| `skills` | `skills:` (preloaded) | "load these skills" line prepended to `developer_instructions` |
| `[claude] tools` | `tools:` allowlist | — (use `sandbox_mode`) |
| `[claude] model`, `effort`, `color` | same fields | — |
| `[codex] sandbox_mode`, `model_reasoning_effort`, `model` | — | same keys |
| `prompt.md` | Markdown body | `developer_instructions` |

Tips:

- **Tune the business questions** in `business-context/references/question-bank.md`
  to your tiers, classification labels, regulators and systems of record.
- **Point golden paths at real starter repos** if you have them.
- **Keep standard IDs stable** once published; ADRs and handoffs cite them.
- Agent names use `snake_case` so the same names work in both tools.

## Repository layout

```
build.py      # src/ → dist/claude, dist/codex, dist/speckit-preset (validates names, tools, TOML, stack.json, preset files)
install.py    # dist/ → a project or your home folder; --speckit adds the Spec Kit preset
speckit_integration.py        # Spec Kit setup, preset install, Codex mirroring, constitution
src/          # edit here (src/speckit-preset/ is the Spec Kit preset)
dist/         # generated, committed for convenience
.github/workflows/check.yml   # build --check, checker, installer and Spec Kit end-to-end tests
```
