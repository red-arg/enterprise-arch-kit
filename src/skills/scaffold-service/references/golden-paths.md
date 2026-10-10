# Golden paths

> TODO(architecture-team): Illustrative defaults aligned with the example
> stack. Replace with links to your real templates/starter repos if you have
> them — then this skill should clone those instead of generating layouts.

## GP-1 — REST/HTTP API

| Language | Framework | Data access | Tests |
| --- | --- | --- | --- |
| **TypeScript (default for BFF/light APIs)** | NestJS | `pg` or Prisma (trial) | Vitest/Jest + Testcontainers |
| **Java (default for transactional services)** | Spring Boot 3 | Spring Data JPA + Flyway | JUnit 5 + Testcontainers |
| **Python (data-heavy APIs)** | FastAPI | SQLAlchemy 2 + Alembic | pytest |

Layout (hexagonal, PAT-01) — shown for TypeScript; mirror it in other languages:

```
<service>/
  src/
    api/            # controllers/routes, request/response DTOs, OpenAPI decorators
    application/    # use cases; no framework or DB imports
    domain/         # entities, value objects, domain errors
    infrastructure/ # DB repositories, HTTP clients (adapters, PAT-09), messaging
    config/         # typed config loaded from env
    observability/  # logger, tracing setup
  test/
    unit/  integration/
  openapi/openapi.yaml   # source of truth for the contract (AP-03, PAT-05)
  migrations/
  docs/adr/
  Dockerfile  .env.example  README.md  CODEOWNERS
```

Shape checklist:
- [ ] OpenAPI spec under `openapi/`, `/v1` prefix (PAT-05, PAT-06)
- [ ] Problem-details error handler (CS-04)
- [ ] `/health/live` and `/health/ready` (PAT-14)
- [ ] OIDC JWT validation middleware + per-route authorization (PAT-10, PAT-12)
- [ ] Outbound HTTP client with timeout and retry policy (PAT-15)
- [ ] Migration tool configured; first migration creates nothing destructive (PAT-18)

## GP-2 — Web frontend

| Default | Notes |
| --- | --- |
| React 19 + TypeScript, Vite | SPA for internal tools |
| Next.js | When SSR/SEO or a BFF is needed |
| Enterprise design system (STK-22) | Mandatory for user-facing UIs |

```
<app>/
  src/
    app/ or pages/   # routes
    components/      # app-specific components built from the design system
    features/<name>/ # feature folders: components, hooks, api calls
    lib/api/         # typed API client generated from the backend OpenAPI spec
    lib/auth/        # OIDC (authorization code + PKCE) via approved library
  tests/
  public/
```

Shape checklist:
- [ ] Login via OIDC with PKCE; no tokens in localStorage (PAT-10)
- [ ] API client generated from OpenAPI, not hand-written
- [ ] Accessibility linting and WCAG 2.2 AA checks (NFR-07)
- [ ] No secrets or backend URLs hard-coded; runtime config (PAT-16)

## GP-3 — Event consumer / worker

Same languages as GP-1. Kafka via the approved client (STK-40).

Shape checklist:
- [ ] CloudEvents envelope; schema registered and versioned (PAT-07)
- [ ] Idempotent handler (dedupe key or upsert) and documented retry/DLQ strategy
- [ ] Consumer lag metric and health endpoint (PAT-13, PAT-14)
- [ ] Graceful shutdown that commits offsets correctly

## GP-4 — Scheduled / batch job

Python 3.12 (default) or the team's service language.

Shape checklist:
- [ ] Runs as a platform-scheduled job (e.g. Kubernetes CronJob), not a sleeping loop
- [ ] Idempotent and safe to re-run; checkpointing for long runs
- [ ] Emits start/finish/failure logs and a duration metric
- [ ] Reads inputs via APIs/events, not another service's database (PAT-03)

## GP-5 — Full stack

Compose GP-2 + GP-1 in one repo only for small Tier 3 apps owned by one
team:

```
<app>/
  apps/web/      # GP-2
  apps/api/      # GP-1
  packages/      # shared UI-agnostic code only (e.g. generated API types) — no shared domain models (PAT-04)
```

For Tier 1/2 or multi-team ownership, use separate repos.
