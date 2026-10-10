# Business question bank

> TODO(architecture-team): adjust wording, options and mappings to your
> organization (tiers, classification labels, regulators, systems of record).
> The standard IDs refer to `enterprise-standards`.

Each question is phrased for someone who doesn't build software. The
**Default** is used when the builder says "not sure" or isn't asked.

## Q1 — Who will use it?

> Who is going to use this?
> (a) Just me, to try the idea · (b) My team · (c) People across the company · (d) Customers or partners outside the company · (e) Not sure

| Answer | Derived requirements |
| --- | --- |
| a | Internal, single user. Tier 3 (NFR-03). Still authenticated via corporate IdP before any production use (PAT-10). |
| b, c | Internal users. Corporate IdP login, role-based access if more than one kind of user (PAT-10, PAT-12). Accessibility WCAG 2.2 AA (NFR-07). |
| d | External exposure: API gateway (PAT-08), customer identity (TODO: customer IdP), security review before go-live, Tier 2 minimum. |
| **Default** | **b** — internal team. |

## Q2 — How many people, how often?

> Roughly how many people will use it, and how often?
> (a) A handful, now and then · (b) Tens to hundreds, daily · (c) Thousands or more, or big bursts (e.g. month-end) · (d) Not sure

| Answer | Derived requirements |
| --- | --- |
| a | Single instance is fine; stateless design still required (NFR-06). |
| b | Stateless, horizontally scalable, p95 targets per NFR-05; managed DB with connection pooling. |
| c | Load test before go-live; caching (STK-31) and async processing for heavy work (PAT-07); autoscaling. |
| **Default** | **b**. |

## Q3 — What information does it handle?

> What kind of information will it store or show? Pick the most sensitive.
> (a) Nothing sensitive / public info · (b) Internal work information · (c) Personal details about staff or customers (names, emails, phone numbers) · (d) Financial, health, payment or other highly confidential data · (e) Not sure

| Answer | Derived requirements |
| --- | --- |
| a | Public classification (NFR-04). |
| b | Internal classification. |
| c | Confidential + PII: encryption at rest with managed keys, access logging, retention policy (NFR-04, NFR-08), no PII in logs (PAT-13), privacy regulations (NFR-09). Use synthetic data in development (NN-02). |
| d | Restricted: all of (c) plus security/compliance review before go-live, audit trail of who saw/changed what, possibly PCI/health rules (NFR-09). |
| **Default** | **c** if the app deals with people in any way; otherwise **b**. Err on the safe side. |

## Q4 — What if it stops working?

> If this stopped working for a day, what would happen?
> (a) Minor inconvenience · (b) Some people's work slows down or stops · (c) Customers, revenue or legal obligations would be affected · (d) Not sure

| Answer | Derived requirements |
| --- | --- |
| a | Tier 3 (NFR-03). |
| b | Tier 2 (NFR-02): backups with tested restore, alerting, on-call owner. |
| c | Tier 1 (NFR-01): high availability, multi-zone, runbooks, DR test, formal production readiness review. |
| **Default** | **a** while it's a prototype; must be **confirmed before production**. |

## Q5 — Other systems and data

> Does it need information from, or need to update, any other systems or files? For example the HR system, CRM, finance system, email, calendars, shared spreadsheets.
> Free text, or (a) No, it stands alone · (b) Yes: ___ · (c) Not sure yet

| Answer | Derived requirements |
| --- | --- |
| a | No integration ports beyond its own storage. |
| b | One port per external system with a fake adapter for local use (PAT-09, PAT-19). Prefer the system's official API or events (PAT-05, PAT-07); never read another system's database (PAT-03). Record each system, direction (read/write), and owner in the handoff. |
| **Default** | **a**; add ports when a system is mentioned. |

## Q6 — Lifespan

> How long do you expect this to be used?
> (a) A short trial or demo · (b) A few months · (c) Long-term, as a regular tool · (d) Not sure

| Answer | Derived requirements |
| --- | --- |
| a | Lighter review bar (Good-Enough Software), but still golden-path structure so it can grow. |
| b, c | Full standards; ownership and support model needed before production (Q8). |
| **Default** | **c** — build as if it will last; it usually does. |

## Q7 — Rules it must follow

> Are there any rules this must follow? For example approvals before something happens, a record of who changed what, data that must stay in a certain country, or industry regulations.
> Free text, or (a) None that I know of · (b) Yes: ___

| Answer | Derived requirements |
| --- | --- |
| Approvals | Explicit workflow states in the domain model; who can approve as roles (PAT-12). |
| Audit record | Append-only audit log of changes with user identity and timestamp. |
| Data residency | Region constraints on hosting and backups (NFR-09); flag for platform team. |
| Regulation named | Map to NFR-09; compliance review before go-live. |
| **Default** | **a**; audit trail anyway if Q3 ≥ c. |

## Q8 — Ownership

> After launch, who would look after it — answer questions, request changes?
> (a) Me / my team · (b) Another team: ___ · (c) Not sure yet

| Answer | Derived requirements |
| --- | --- |
| any | Business owner recorded in README and handoff. Technical owner is an open question for the engineering team unless named. |
| **Default** | **c** — record as open question; ask only when preparing for production. |

## When to ask what

| Moment | Questions |
| --- | --- |
| Starting something new | Q1, Q3 (and Q5 if the request mentions other data) |
| Adding login, roles or sharing | Q1 |
| Adding storage of people's data | Q3 |
| Connecting to anything else | Q5 |
| "Can we go live?" / preparing for production | Q4, Q6, Q7, Q8 and confirm every **Assumed** item in the handoff |
