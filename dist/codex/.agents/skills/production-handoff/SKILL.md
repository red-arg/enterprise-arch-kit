---
name: production-handoff
description: Create and maintain docs/production-handoff.md, the living document an engineering team uses to take a vibe-coded project to production on enterprise standards - business context, derived requirements, architecture as built, swappable infrastructure status, decisions, and readiness gaps. Use after design, after reviews, whenever an assumption, decision or production gap appears, and when asked "can this go live?".
---

# Production handoff

The builder delivers business value; an engineering team later takes it to
production. This document is the bridge: it captures everything the
engineers need so they never have to reverse-engineer the code or go back to
the builder with technical questions.

Audience: engineers and architects. Write technically, cite standard IDs,
link to files. The builder doesn't need to read it.

## Location and shape

- `docs/production-handoff.md`, created from `assets/production-handoff-template.md`.
- Keep the template's section order and headings so every project's handoff
  reads the same way.
- One document per deployable project. A monorepo with several deployables
  gets one handoff per deployable, linked from a short index at
  `docs/production-handoff.md`.

## When to update and what

| Trigger | Update |
| --- | --- |
| Business question answered or default used (`business-context`) | §2 Business context, §3 Derived requirements (Confirmed/Assumed) |
| Design created or changed (`solution_designer`) | §1 Summary, §4 Architecture, §5 Infrastructure ports, link design brief |
| New dependency, integration or capability built | §4, §5 and the change log |
| Architecture or readability review finished | §6 Standards alignment (date, verdict), §8 gaps from "record for production" findings |
| Decision or exception recorded (`write-adr`) | §7 Decisions and exceptions |
| Builder expressed a technical preference that wasn't followed | §7 note ("Builder preferred X; standard Y used because …") |
| "Can this go live?" | Walk §8 and §9, confirm Assumed items with business questions, set the readiness verdict in §1 |

## Writing rules

- **Facts over prose.** Tables and short bullets. Each item states what,
  where (`file:line` or path), which standard, and status.
- **Status vocabulary:** `Ready` · `Dev only` (works locally, production
  adapter/config missing) · `Gap` (needs work) · `Exception` (ADR) ·
  `Assumed` (business fact not yet confirmed) · `N/A`.
- **Owner on every gap:** `Engineering`, `Platform`, `Security`,
  `Architecture` or `Business` (for confirmations). Never the builder for
  technical work.
- **Estimate effort coarsely** for each gap: `S` (hours), `M` (days),
  `L` (weeks). It tells the receiving team how close to production this is.
- **Update in place.** Replace stale content; don't append contradictory
  versions. Add one line to the change log per update.
- **No secrets, real personal data or credentials** in the document.

## Readiness verdict (§1)

- **Prototype** — runs locally; major gaps or Assumed business facts remain.
- **Ready for engineering hardening** — business facts confirmed, structure
  aligned, only `S`/`M` gaps with clear owners.
- **Ready for production review** — no open gaps except those owned by
  Platform/Security for go-live, all exceptions have ADRs.
