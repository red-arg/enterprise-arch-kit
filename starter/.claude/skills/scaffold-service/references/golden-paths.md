# Golden paths

> TODO(architecture-team): Illustrative defaults aligned with the example
> stack. If you have starter repos, link them here and have the skill clone
> them instead of generating layouts.

All paths share one structure so every vibe-coded project looks the same to
the engineers who productionize it:

- **Modules by business capability** (PAT-20) — top-level folders are
  business things (`leave-requests`, `approvals`), not `controllers/` and `models/`.
- **Ports and adapters** (PAT-19) — each module's infrastructure needs are
  interfaces with a `local` adapter (zero setup) and a `production` adapter
  (enterprise stack), chosen by configuration.
- **Two profiles** — `local` (default; runs with one command, no accounts,
  sample data) and `production` (enterprise adapters, config from the
  environment and secrets manager). Same code, same build artifact.

## Choosing a path (no questions to the builder)

| The builder describes… | Path |
| --- | --- |
| A tool/app people click through (forms, lists, dashboards, approvals) | **GP-5 full stack** (GP-2 + GP-1) |
| "An API", "a service other systems call", an integration | **GP-1 API** |
| Something that reacts to things happening elsewhere | **GP-3 worker** |
| Something that runs on a schedule, a report, a sync | **GP-4 job** |

Language: TypeScript by default for GP-1/2/5 (one language end to end is
easiest to maintain); Java for transactional, Tier 1/2 or high-volume
back-ends; Python for data- and ML-heavy work. Decide from the business
context — never ask.

## Standard ports

| Port | Local adapter (default) | Production adapter |
| --- | --- | --- |
| **Persistence** | Embedded PostgreSQL-compatible DB (PGlite for Node, H2 in PostgreSQL mode for Java, SQLite via SQLAlchemy for Python) with seed data (STK-34) | Managed PostgreSQL (STK-30) via the same ORM and migrations |
| **Identity** | Dev login: pick a sample user and role, clearly labelled "local only" | Corporate IdP via OIDC (PAT-10); roles from token claims (PAT-12) |
| **Config and secrets** | `.env.local` (git-ignored) generated from `.env.example` | Environment + secrets manager (PAT-11, PAT-16) |
| **Messaging/events** | In-process event bus | Kafka (STK-40), CloudEvents (PAT-07) |
| **File storage** | Local folder `./.data/files` | TODO: enterprise object storage |
| **Notifications (email, chat)** | Writes to console and a local outbox file | TODO: enterprise notification service |
| **External system X** | Fake with realistic sample data | Adapter over X's official API (PAT-09), stub until access is granted |

Rules:
- Ports are defined by what the **business** needs ("find pending requests
  for approver"), not by the technology ("run SQL").
- Production adapters: implement now when it's cheap and testable without
  enterprise access (e.g. PostgreSQL via the same ORM, OIDC with a standard
  library and config). Otherwise generate a stub that throws
  `NotConfiguredError("<port>: production adapter not implemented — see docs/production-handoff.md")`.
- No per-port test suites: ports are exercised by the functional unit
  tests through the test app factory (local adapters), and the same suite
  can run with production adapters in an integration environment.
- **Public interface per module:** one file (`index.ts`, `__init__.py`, or a
  `public/` package) declaring the module's business-named operations,
  input/output types and business errors — no logic, no re-exported internal
  types. It's the only thing functional tests call.
- **Test app factory** (`src/app/test-app.*`): builds the app in memory with
  local adapters and test controls; the functional tests' only entry point.
- Adapter selection lives in a single composition file per deployable
  (`src/app/wiring.*`), driven by config (`DATA_STORE=embedded|postgres`,
  `AUTH_MODE=dev|oidc`, …).

## GP-1 — API / back-end

| Language | Framework | Data access | Tests |
| --- | --- | --- | --- |
| **TypeScript** (default) | NestJS (STK-11) | `pg` + SQL migrations in production, PGlite locally — same PostgreSQL dialect behind the persistence port | Vitest |
| **Java** | Spring Boot 3 (STK-10) | Spring Data JPA + Flyway; H2 (PostgreSQL mode) locally | JUnit 5 |
| **Python** | FastAPI (STK-12) | SQLAlchemy 2 + Alembic; SQLite locally | pytest |

```
<app>/
  src/
    modules/
      <capability>/             # e.g. leave-requests
        domain/                 # entities, rules, domain errors — no framework imports
        application/            # use cases; depends on ports only
        ports/                  # interfaces this module needs (repository, notifier…)
        adapters/
          local/                # zero-setup implementations
          production/           # enterprise-stack implementations or fail-fast stubs
        api/                    # HTTP routes + DTOs for this capability
        index.ts                # the module's public interface
    platform/                   # cross-cutting: config, logging, tracing, auth middleware, errors
    app/wiring.ts               # composition root: picks adapters from config
  test/
    functional/                 # functional unit tests via public interfaces (owned by test_writer)
      <capability>/
    <capability>/...
  openapi/openapi.yaml
  migrations/
  seed/                         # sample data for the local profile
  docs/production-handoff.md  docs/design/  docs/adr/
  Dockerfile  .env.example  README.md  CODEOWNERS
```

Checklist:
- [ ] `/v1` routes with OpenAPI spec (PAT-05, PAT-06) and problem-details errors (CS-04)
- [ ] `/health/live`, `/health/ready` (PAT-14)
- [ ] Auth middleware on every route; role checks in use cases (PAT-10, PAT-12)
- [ ] Outbound calls with timeouts and retries (PAT-15)
- [ ] Migrations shared by both persistence adapters (PAT-18)

## GP-2 — Web front-end

React 19 + TypeScript (STK-20) with Vite; Next.js (STK-21) only if pages must
be public/SEO. Enterprise design system (STK-22) for all UI.

```
<app>/web/
  src/
    features/<capability>/      # mirrors back-end modules: pages, components, hooks
    shared/ui/                  # app components built from the design system
    shared/api/                 # client generated from openapi.yaml
    shared/auth/                # dev login locally; OIDC + PKCE in production
    app/routes.tsx  app/config.ts
```

Checklist:
- [ ] API client generated from the OpenAPI spec, never hand-written
- [ ] No tokens in localStorage; runtime config, no hard-coded URLs (PAT-10, PAT-16)
- [ ] Accessibility checks (NFR-07)

## GP-3 — Event worker

Same languages and module layout as GP-1; the trigger is a consumer instead
of an HTTP route. Local adapter: in-process bus fed by a `seed/events/`
folder. Checklist: CloudEvents + versioned schema (PAT-07), idempotent
handlers, dead-letter strategy, lag metric, graceful shutdown.

## GP-4 — Scheduled job

Python by default (or the project's language). A `run` entry point invoked by
the platform scheduler in production (e.g. Kubernetes CronJob) and by a
script locally. Checklist: idempotent and re-runnable, start/finish/failure
logs and duration metric, inputs via APIs/events never another system's
database (PAT-03).

## GP-5 — Full stack (default for apps people use)

```
<app>/
  api/        # GP-1
  web/        # GP-2
  package.json / Makefile   # `dev` runs both with the local profile
```

One repo, two deployables, one `dev` command. Shared code limited to
generated API types (PAT-04).
