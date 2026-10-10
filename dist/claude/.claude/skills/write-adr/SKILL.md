---
name: write-adr
description: Write an Architecture Decision Record (ADR) in docs/adr/. Use when a significant technical decision is made, when choosing between options, when deviating from an enterprise standard (exception ADR), or when a technology is unassessed and needs an architecture ruling.
---

# Write an ADR

ADRs are short, numbered Markdown files in `docs/adr/` that capture one
decision: the context, the options, what was chosen and the consequences.
They are how a deviation from the enterprise standards becomes legitimate.

## When an ADR is required

- **Exception** — the change deviates from a standard (hold technology in new
  code, unassessed technology of significance, pattern not followed).
- **Significant decision** — new service, new data store, new integration
  style, new external vendor, anything hard to reverse.
- **Not needed** for choices already covered by an `adopt` standard. Don't
  create ADRs for routine work.
- **Can't be waived by ADR** — non-negotiables (`NN-*` in the standards).
  Tell the developer to escalate instead.

## Steps

1. **Find the next number.** List `docs/adr/` and take the highest
   `NNNN-*.md` + 1. Start at `0001` if empty (create the folder, and copy
   `assets/0000-adr-template.md` there as the reference template if it isn't
   there already).
2. **Gather the facts** from the conversation and code. You need: the
   decision, the forces/constraints, at least two options considered (one of
   them is always the standard option for an exception), and the
   consequences. If a key fact is missing (e.g. why the standard option
   doesn't work), ask the developer one focused question rather than inventing it.
3. **Write** `docs/adr/NNNN-<kebab-case-title>.md` from
   `assets/0000-adr-template.md`. Rules:
   - Title is the decision, not the problem: "Use MongoDB for product catalog
     search", not "Database choice".
   - Status is `Proposed`. Only humans change it to `Accepted`.
   - For exceptions, fill **Standards affected** with the IDs (e.g.
     `STK-33`, `PAT-03`) and include a **Review/expiry date** (default: 12
     months) and an **exit plan**.
   - Be honest about negative consequences.
   - Keep it under one page. Link to code, tickets and docs instead of pasting.
4. **Link it from the code.** Where the deviation lives, add a short comment:
   `// ADR-0007: exception to PAT-03 (see docs/adr/0007-…)`.
5. **Tell the developer** in two or three lines: the file path, the status,
   and who should approve it (TODO: name your architecture review forum /
   CODEOWNERS for `docs/adr/`).

## Superseding

To change a past decision, write a new ADR, set its **Supersedes** field, and
change the old ADR's status to `Superseded by ADR-NNNN`. Never rewrite an
accepted ADR's decision in place.
