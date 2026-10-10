## Enterprise Alignment *(mandatory — enterprise)*

<!--
  Filled by the solution_designer agent from the enterprise standards. Every
  technical choice above (Technical Context, Project Structure) must trace to
  a standard ID here or be marked UNASSESSED. No NEEDS CLARIFICATION may be
  left for technical items — decide them from the standards.
-->

### Derived Requirements

| Business fact (spec → Business Context) | Requirement | Standard |
| --- | --- | --- |
| [e.g. Q3: staff personal details — Confirmed] | Confidential + PII: encryption at rest, access logging, retention | NFR-04, NFR-08 |

### Golden Path

**Path**: [GP-n — e.g. GP-5 full stack] · **Language/Framework**: [e.g. TypeScript, NestJS + React] · **Why**: [business reason]

### Modules by Business Capability (PAT-20)

| Module | Business capability | Public interface | Events |
| --- | --- | --- | --- |

### Ports and Adapters (PAT-19)

| Port | Used by | Local adapter (zero setup) | Production adapter | Config switch | Status |
| --- | --- | --- | --- | --- | --- |
| Persistence | | | | `DATA_STORE=` | Ready / Stub |
| Identity | | Dev login | Corporate IdP (OIDC) | `AUTH_MODE=` | |

### Standards Trace

| Decision | Choice | Status (adopt/trial/…) | Standard |
| --- | --- | --- | --- |

### Acceptance Examples (test oracles)

<!-- Concrete, hand-worked values per user story for test_writer. Literal
     inputs and expected outcomes — never formulas. Include at least one
     edge or rule-breaking case per story. -->

| Story / scenario | Given (inputs) | When | Then (expected, literal) |
| --- | --- | --- | --- |
| US1-AS1 | [e.g. 3 days of leave remaining] | [request 5 days] | [rejected: "Not enough leave remaining (3 days)"] |

### Functional Test Boundary

<!-- Everything test_writer may rely on. Tests drive the system only through
     this boundary, so it must be complete for every acceptance scenario. -->

- **External interface:** [e.g. HTTP API in `contracts/openapi.yaml` — every operation the acceptance scenarios need]
- **Start for tests:** [e.g. `npm run start:local` → base URL from `PORT`, fresh embedded data per start]
- **Business roles (dev login):** [e.g. `employee`, `manager`, `hr-admin`]
- **Test controls (local profile only):** [e.g. `FIXED_NOW=2026-03-31T17:00:00+08:00`; fake HR system sample data in `seed/hr/`]
- **UI journeys worth a browser test:** [P1 journeys only, or "none"]

### Exceptions

| Off-standard choice | Business need that forces it | Standard affected | ADR |
| --- | --- | --- | --- |

### Production Handoff

Updated: `docs/production-handoff.md` §1–§5 · Open business questions added to §9: [list or "none"]
