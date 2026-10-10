# Architecture and integration patterns

> TODO(architecture-team): Illustrative defaults. Replace with your approved
> patterns and reference implementations. Keep IDs stable once published.

## Structure

| ID | Pattern | Rule |
| --- | --- | --- |
| PAT-01 | **Layered / hexagonal service** | Separate transport (HTTP handlers, consumers), application logic and infrastructure (DB, clients). Business logic never imports framework or driver types directly. See PAT-19 (swappable infrastructure) and PAT-20 (modules by capability). |
| PAT-02 | **Service granularity** | Start with a modular monolith per bounded context. Split into a separate service only for independent scaling, deployment cadence or ownership. Don't create a service per entity. |
| PAT-03 | **Database per service** | Each service owns its schema. Other services get data via its API or events, never by querying its tables. |
| PAT-04 | **Shared libraries are for cross-cutting concerns only** | Logging, auth, telemetry clients — yes. Shared domain models across services — no. |
| PAT-19 | **Swappable infrastructure (ports and adapters)** | Every infrastructure concern — persistence, identity, secrets/config, messaging, file storage, notifications, and each external system — is reached through an interface (port) owned by the application. Each port has a **local adapter** that runs with zero setup (embedded database, dev login, in-process queue, fake external system with sample data) and a **production adapter** on the enterprise stack. The active adapter is chosen by configuration only; business code never knows which one runs. Both profiles pass the same black-box functional suite, which is how the production adapters are verified. If a production adapter isn't built yet, ship a typed stub that fails fast with a clear message and record it in the production handoff. |
| PAT-20 | **Modules by business capability** | Organize code by business capability (`leave-requests`, `approvals`, `notifications`), not by technical layer at the top level. Each module owns its domain, use cases and adapters and exposes a small public interface. Modules talk through those interfaces or domain events — never through each other's internals or tables. A new capability is a new module, and any module can later be extracted into its own service without rewriting its callers (PAT-02). |

## Integration

| ID | Pattern | Rule |
| --- | --- | --- |
| PAT-05 | **Synchronous APIs** | REST over HTTPS with an OpenAPI 3 spec checked into the repo. JSON, `camelCase` fields, RFC 9457 problem details for errors. TODO: note if gRPC is allowed internally. |
| PAT-06 | **API versioning** | Major version in the path (`/v1/…`). Additive changes only within a version. Deprecations announced with a sunset date. |
| PAT-07 | **Asynchronous events** | Use the approved event broker (see tech stack). Events follow CloudEvents, have a versioned schema in the schema registry, and consumers are idempotent. |
| PAT-08 | **API gateway** | Externally exposed APIs go through the enterprise API gateway. Services don't expose themselves to the internet directly. |
| PAT-09 | **Third-party integrations** | Wrap every external vendor API in an adapter (anti-corruption layer) so it can be swapped and mocked. |

## Security

| ID | Pattern | Rule |
| --- | --- | --- |
| PAT-10 | **Identity** | Users authenticate via the corporate IdP using OIDC. Service-to-service uses OAuth2 client credentials or workload identity. No custom login systems or password storage. |
| PAT-11 | **Secrets** | Read secrets at runtime from the approved secrets manager. Never in env files committed to git, never in container images. |
| PAT-12 | **Authorization** | Enforce authorization in the service on every request, based on token claims/scopes. Don't rely on the gateway alone. |

## Operability

| ID | Pattern | Rule |
| --- | --- | --- |
| PAT-13 | **Observability** | OpenTelemetry for traces and metrics. Structured JSON logs with a correlation/trace ID. No PII in logs. |
| PAT-14 | **Health and readiness** | Expose liveness and readiness endpoints (e.g. `/health/live`, `/health/ready`). |
| PAT-15 | **Resilience** | Every outbound call has a timeout. Retries use exponential backoff with jitter and only on idempotent operations. Use circuit breakers for flaky dependencies. |
| PAT-16 | **Configuration** | Twelve-factor: config from environment/config service, same artifact promoted through environments. |
| PAT-17 | **Deployment** | Container image built once in CI, deployed to the approved platform via the standard pipeline. Infrastructure defined in the approved IaC tool. |
| PAT-18 | **Data migrations** | Schema changes via versioned migration tool, backward compatible (expand → migrate → contract). |
