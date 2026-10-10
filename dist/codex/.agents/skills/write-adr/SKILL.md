---
name: write-adr
description: Write an Architecture Decision Record (ADR) in docs/adr/. Use when a significant technical decision is made, when an off-standard option is used because a business need requires it (exception ADR), or when a technology is unassessed and needs an architecture ruling.
---

# Write an ADR

ADRs are short, numbered Markdown files in `docs/adr/` that capture one
decision: the business need, the options, what was chosen and the
consequences. They let the engineering and architecture teams review
decisions the agents made on the builder's behalf. They are written for
engineers, not for the builder.

## When an ADR is required

- **Exception** — something off-standard was used because a business need
  couldn't be met otherwise (hold or unassessed technology, pattern not
  followed).
- **Significant decision** — new deployable, new data store, new
  integration with another system, anything hard to reverse.
- **Not needed** for choices already covered by an `adopt` standard or the
  golden path. Don't create ADRs for routine work.
- **Never for non-negotiables** (`NN-*`). Those can't be waived by an ADR;
  record them as blocking gaps in the production handoff.

## Steps

1. **Find the next number.** List `docs/adr/` and take the highest
   `NNNN-*.md` + 1. Start at `0001` if empty (create the folder).
2. **Gather the facts** from the business context and derived requirements
   in `docs/production-handoff.md`, the design brief and the code. Ground the
   *Context* in business terms ("HR needs approvals within a day; 2,000
   staff; personal data") and the options in technical terms.
3. **Never ask the builder technical questions to fill the ADR.** If a
   business fact is missing, ask the plain business question from the
   `business-context` skill, or write `Assumed: …` and add it to the
   handoff's open questions. If a technical fact is missing, investigate the
   code or write `TODO(engineering): …`.
4. **Write** `docs/adr/NNNN-<kebab-case-title>.md` from
   `assets/0000-adr-template.md`:
   - Title is the decision: "Use MongoDB for product catalog search".
   - Status `Proposed`; Deciders `AI agent on behalf of <builder/team>`.
     Only the architecture team sets `Accepted`.
   - Exceptions: fill **Standards affected**, a **Review/expiry date**
     (default 12 months) and an **exit plan** — usually "swap the adapter
     behind port X" (PAT-19).
   - Be honest about negative consequences. Keep it under one page.
5. **Link it from the code** with a short comment where the deviation lives:
   `// ADR-0007: exception to STK-33 (docs/adr/0007-…)`.
6. **Index it** in §7 of the production handoff (or tell `handoff_scribe`).
   Don't announce ADRs to the builder.

## Superseding

To change a past decision, write a new ADR, set its **Supersedes** field, and
change the old ADR's status to `Superseded by ADR-NNNN`. Never rewrite an
accepted ADR's decision in place.
