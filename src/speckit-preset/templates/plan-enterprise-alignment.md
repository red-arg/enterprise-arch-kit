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

### Exceptions

| Off-standard choice | Business need that forces it | Standard affected | ADR |
| --- | --- | --- | --- |

### Production Handoff

Updated: `docs/production-handoff.md` §1–§5 · Open business questions added to §9: [list or "none"]
