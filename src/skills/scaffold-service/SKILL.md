---
name: scaffold-service
description: Start a new app, API, worker or job on the enterprise golden path - approved stack, modules by business capability, swappable local/production infrastructure, and a production handoff - so it runs locally with one command and can be productionized with little effort. Use when someone says "build me an app/tool/API", "start a new project", or begins work that needs a new deployable.
---

# Scaffold on the golden path

The builder wants something working, fast. Engineers later want something
they can take to production without a rewrite. This skill gives both: it
runs locally with one command and no accounts, and it's already shaped like
an enterprise service.

## 1. Understand the business, not the technology

- Infer what's being built from the request. If the core facts are unknown,
  ask the business questions from the `business-context` skill — usually only
  **Q1 (who uses it)** and **Q3 (what information)**, plus **Q5** if the
  request mentions other systems or data.
- **Never** ask about language, framework, database, hosting or structure.
- For anything beyond one small app (several deployables, integrations with
  other systems, sensitive data), have `solution_designer` produce the design
  first.

## 2. Decide the path yourself

Read `references/golden-paths.md` and choose the path, language and ports
from the business context using its tables. Don't confirm technical choices
with the builder. Tell them only what they'll get, in plain words, e.g.
"I'll set up a web app your team can sign into, with a place to store
requests. It'll run on your laptop with one command."

If the builder named a specific technology, treat it as a wish for an
outcome: use the approved equivalent and say so in one plain sentence (see
`enterprise-standards`, "decide, don't ask").

## 3. Generate

Lay out the chosen path exactly as in `golden-paths.md`: modules by business
capability, ports with local and production adapters, one composition file
that selects adapters from configuration. Use the language's standard
project generator where one exists, then reshape to the layout.

**Baseline (every project):**
- [ ] Module(s) named after the business capabilities in the request (PAT-20)
- [ ] Standard ports with local adapters working and seeded with realistic sample data; production adapters implemented where cheap, otherwise fail-fast stubs (PAT-19)
- [ ] Each module's public interface file (business-named operations, input/output types, business errors; no logic) and a **test app factory** (`src/app/test-app.*` / `app/test_app.py`) that wires the app in memory with local adapters and exposes the documented test controls (clock, acting user/role, outside-system data) — see the `tdd` skill; unit test runner with JUnit XML output; `.tdd/` git-ignored; one passing smoke test that builds the app from the factory. Behaviour is then built test-first with the `tdd` skill: functional unit tests only, no browser or HTTP tests (CS-03)
- [ ] One command to run locally (`npm run dev` / `make dev` / `./gradlew bootRun`), documented at the top of the README
- [ ] Config from environment with `.env.example`; local profile is the default; no secrets anywhere (CS-08, PAT-11, NN-01)
- [ ] Structured logging with correlation ID; OpenTelemetry wired with a local no-op exporter (PAT-13); health endpoints (PAT-14)
- [ ] Formatter + linter config (CS-02); `.gitignore` excluding `.env*`, `.data/`, build output
- [ ] CI pipeline: lint, test, dependency/licence scan, `stack-check --strict`, image build (AP-06)
- [ ] `Dockerfile` (multi-stage, non-root) for each deployable (PAT-17)
- [ ] `README.md` — what it does in business terms, how to run it, and a link to the production handoff (CS-01)
- [ ] `docs/production-handoff.md` started via the `production-handoff` skill (or `handoff_scribe`), with the business context, the path chosen, and every port's status
- [ ] `docs/adr/0001-golden-path.md` recording the path and any non-default choice (`write-adr`)

Leave `TODO(engineering):` markers for enterprise-specific values (registry
URLs, IdP issuer, namespaces) and list them in the handoff — don't invent them
and don't ask the builder.

## 4. Hand over to the builder

Run it once yourself to confirm it starts and the sample data shows up. Then
tell the builder in two or three plain sentences: what they can do now, the
one command to run it, and what to ask for next. Nothing about stacks,
adapters or standards.
