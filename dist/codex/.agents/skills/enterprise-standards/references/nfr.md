# Default non-functional requirements

> TODO(architecture-team): Illustrative defaults. Replace with your service
> tiers, SLOs and data classification scheme.

## Service tiers

| ID | Tier | Availability target | RTO / RPO | Typical examples |
| --- | --- | --- | --- | --- |
| NFR-01 | Tier 1 – critical | 99.95% | 1 h / 5 min | Customer-facing transactions, payments |
| NFR-02 | Tier 2 – important | 99.9% | 4 h / 1 h | Internal business apps |
| NFR-03 | Tier 3 – supporting | 99.5% | 24 h / 24 h | Reporting, internal tools, prototypes |

Every new service declares its tier in its README. If the developer doesn't
know, default to Tier 3 for prototypes and ask before going to production.

## Cross-cutting

| ID | Requirement |
| --- | --- |
| NFR-04 | **Data classification** — every data store declares the highest classification it holds (TODO: e.g. Public / Internal / Confidential / Restricted). Confidential and above require encryption at rest with managed keys and access logging. |
| NFR-05 | **Performance** — APIs define p95 latency targets in the design. Default target for synchronous user-facing APIs: p95 < 300 ms. |
| NFR-06 | **Scalability** — services are stateless; state lives in managed data stores. Horizontal scaling is the default. |
| NFR-07 | **Accessibility** — user interfaces meet WCAG 2.2 AA. |
| NFR-08 | **Retention** — data has a documented retention period and deletion process. |
| NFR-09 | **Regulatory** — TODO: list regimes that apply (e.g. GDPR, PDPA, PCI DSS, SOX) and which tiers/classifications trigger them. |
