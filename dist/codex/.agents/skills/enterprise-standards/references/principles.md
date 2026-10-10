# Architecture principles

> TODO(architecture-team): These are illustrative defaults. Replace with your
> organization's published principles. Keep IDs stable once published.

| ID | Principle | What it means in practice |
| --- | --- | --- |
| AP-01 | **Reuse before buy before build** | Check for an existing platform service or shared library first, then a vendor product on the approved list, and only then build. |
| AP-02 | **Clear ownership and boundaries** | Every service has one owning team and one bounded context. A service owns its data; nobody else reads its database. |
| AP-03 | **API first** | Interfaces are designed and documented (OpenAPI / AsyncAPI) before implementation and are versioned. |
| AP-04 | **Secure by design** | Authenticate every call, authorize at the resource, least privilege everywhere, no secrets in code or config files. |
| AP-05 | **Observable by default** | Structured logs, metrics and traces from day one, not after the first incident. |
| AP-06 | **Automate everything** | Build, test, security scans, infrastructure and deployment are code and run in CI/CD. No manual production changes. |
| AP-07 | **Design for failure** | Assume dependencies fail. Use timeouts, retries with backoff, idempotency and graceful degradation. |
| AP-08 | **Prefer managed and boring** | Choose managed platform services and proven technology over novel or self-hosted options unless there is a documented reason. |
| AP-09 | **Data is classified and protected** | Know the classification of every data element; encrypt in transit and at rest; minimize PII. |
| AP-10 | **Decisions are recorded** | Significant or non-standard decisions are captured as ADRs in the repo. |

## Non-negotiables

These are never waived by an ADR from a delivery team. Escalate to the
architecture/security team instead.

- NN-01: No secrets, keys or credentials committed to source control.
- NN-02: No production data (especially PII) in non-production environments.
- NN-03: All externally reachable endpoints are authenticated (TODO: list approved exceptions such as health checks).
- NN-04: Only dependencies from approved registries/mirrors. TODO: name your internal registry.
