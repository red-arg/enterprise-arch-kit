---
name: scaffold-service
description: Start a new service, API, web app, worker or job on the enterprise golden path with the approved stack and required cross-cutting concerns already wired in. Use when someone says "build me an app/API/service/tool", "start a new project", "set up a repo", or begins a feature that needs a new deployable.
---

# Scaffold on the golden path

Vibe-coded projects drift most in the first hour: framework, folder layout,
auth, config and logging get picked ad hoc and never revisited. This skill
makes the first hour land on the enterprise golden path instead.

## 1. Decide what's being built (ask at most two questions)

Infer from the request where you can. Only ask what you can't infer:

1. **Shape** — REST/HTTP API · web frontend · event consumer/worker ·
   scheduled/batch job · full-stack (frontend + API).
2. **Language** — only if the team has a preference; otherwise use the
   golden-path default for the shape.

Also note, without asking unless it matters now: who uses it (internal /
external), the data it holds (classification, NFR-04), and the service tier
(NFR-01–03; default Tier 3 for prototypes).

For anything beyond a single small service — several services, new data
stores, external integrations — produce a short design first (the
`solution_designer` agent does this) before generating code.

## 2. Pick the golden path

Read `references/golden-paths.md` and choose the matching path. Confirm the
choices with the developer in one short block before writing files:

```
Golden path: REST API · TypeScript · NestJS (STK-02, STK-11)
Data: PostgreSQL (STK-30) via Prisma (trial — owner needed)  ← flagged
Auth: OIDC via corporate IdP (PAT-10) · Tier 3 · Internal data
```

If they ask for something off-path (e.g. Flask, MySQL), follow the
"guide, don't block" rule in `enterprise-standards`: explain, offer the
standard option, and if they insist, proceed and offer an exception ADR.

## 3. Generate

Create the layout from the golden path, then wire in **every** item of the
baseline below — these are what make a prototype promotable later. Use the
language's normal project generator if one exists (e.g. `npm create`,
Spring Initializr conventions) rather than hand-writing boilerplate.

**Baseline (all shapes):**
- [ ] `README.md` — purpose, owner (TODO placeholder if unknown), tier, data classification, how to run/test/deploy (CS-01)
- [ ] `docs/adr/0001-record-architecture-decisions.md` and `docs/adr/0002-<golden path chosen>.md` (use the `write-adr` skill; mark both Accepted only if the developer confirms)
- [ ] `CODEOWNERS` with a TODO team
- [ ] Formatter + linter config for the language (CS-02) and a test setup with one passing test (CS-03)
- [ ] Config from environment with `.env.example` placeholders only; no secrets (CS-08, PAT-11)
- [ ] Structured logging with trace/correlation ID; OpenTelemetry wired with a no-op/local exporter (PAT-13)
- [ ] `.gitignore` that excludes env files, build output and IDE files
- [ ] CI pipeline: lint, test, dependency/licence scan, `stack-check --strict`, container build (AP-06)
- [ ] `Dockerfile` (non-root user, multi-stage) for deployables (PAT-17)

**Plus, by shape:** see the checklist in `references/golden-paths.md`.

Leave `TODO(owner):` markers for anything that needs enterprise-specific
values (registry URLs, IdP issuer, platform namespaces) rather than inventing
them.

## 4. Hand over

Tell the developer in a few lines: what was created, the golden path used,
anything flagged (trial tech, TODOs that block production), and the next step
(usually: build the first feature, then run `architecture-review`).
