# Project Constitution

> Generated from the enterprise standards (`enterprise-standards` skill).
> The standards are the source of truth; this constitution is the
> project-level summary that Spec Kit gates check against. Amend only to add
> project-specific rules — never to weaken an enterprise standard.

## Core Principles

### I. Business decides what, agents decide how

The builder describes the outcome, the users and the information involved.
Every technical decision — language, framework, data store, architecture,
patterns, security, operations — is made by the agents from the enterprise
standards. Specs contain no technology. The builder is never asked a
technical question or to weigh a technical trade-off; missing facts are
asked as plain business questions (`business-context` skill) or assumed with
safe defaults and recorded for confirmation.

### II. Approved stack only (STK, CS-06)

Only `adopt` technologies and packages are used by default; `trial` only when
no `adopt` option fits; `local` packages only in local adapters and tests.
`hold`, `retire` and unassessed technologies are replaced with approved
equivalents. A genuine business need that only an off-standard option can
meet is isolated behind a port and recorded as an exception ADR.

### III. Golden path, modules by business capability (PAT-20)

Every deployable starts from an enterprise golden path. Code is organized by
business capability; each module owns its domain, use cases and adapters and
exposes a small public interface. Modules never reach into each other's
internals or data.

### IV. Swappable infrastructure (PAT-19) — NON-NEGOTIABLE

Persistence, identity, secrets/config, messaging, file storage,
notifications and every external system sit behind ports with a zero-setup
local adapter and an enterprise production adapter (or fail-fast stub),
selected by configuration only and verified by shared contract tests.
Business code never imports infrastructure.

### V. Secure and observable by default (AP-04, AP-05)

Authentication on every entry point, authorization in every use case, no
secrets in code (NN-01), no real personal data outside production (NN-02),
structured logs without personal data, tracing and health endpoints from the
first slice.

### VI. Recorded for production (AP-10)

`docs/production-handoff.md` is kept current with business context, derived
requirements, architecture as built, port status, decisions, exceptions and
readiness gaps. Significant and off-standard decisions have ADRs in
`docs/adr/`. An engineering team must be able to take the project to
production from these records without going back to the builder.

### VII. Easy to change (Pragmatic Programmer, RD-01–RD-16)

Every finished slice is reviewed for standards alignment and readability.
Fixes that need no business input are applied immediately; larger gaps are
recorded in the handoff.

### VIII. Test-first, written independently

Every behaviour change starts with failing tests written by `test_writer`
from the spec and public interfaces — never from the implementation — and is
made to pass by `implementer`, who never changes tests. Every new test must
fail before implementation (no vacuous or tautological tests), and tests must
be unchanged between red and green. Tests are the executable specification.

## Enterprise Constraints

- Non-negotiables `NN-01`–`NN-04` (principles.md) can't be waived by any ADR.
- Derived requirements (service tier, data classification, access model,
  scale, compliance) come from the business context and follow `nfr.md`.
- Integrations use official APIs or events (PAT-05–PAT-09), never another
  system's database (PAT-03).

## Development Workflow and Quality Gates

- **Spec gate:** no technology in `spec.md`; Business Context section filled
  (Confirmed or Assumed for each fact).
- **Plan gate:** every technical choice in `plan.md` cites a standard ID or is
  marked UNASSESSED; every infrastructure need has a port; any violation of
  these principles is listed under Complexity Tracking with an ADR.
- **Test gates:** `verify-red` passes before implementation starts and
  `verify-green` passes before a story is done (`tdd` skill).
- **Implementation gate:** one-command local run works; `stack-check --strict`
  passes; architecture and readability reviews run; handoff updated.

## Governance

The enterprise standards (owned by the architecture team) supersede this
constitution. Amendments that add project rules are allowed; amendments that
relax enterprise standards require an exception ADR approved by the
architecture team.

**Version**: 1.1.0 | **Ratified**: on project initialization | **Last Amended**: on project initialization
