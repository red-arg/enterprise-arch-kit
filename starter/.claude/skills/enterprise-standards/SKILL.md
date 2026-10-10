---
name: enterprise-standards
description: Enterprise architecture standards, approved tech stack, integration patterns and coding standards. Use whenever choosing a language, framework, library, database, cloud service or pattern, designing a component or API, or deciding whether something is allowed.
---

# Enterprise standards

This skill is the single source of truth for how software is built here. Every
other skill and agent in this kit cites it. Read only the reference file you
need — don't load all of them for a narrow question.

| Need to know… | Read |
| --- | --- |
| Guiding principles and non-negotiables | `references/principles.md` |
| Which languages, frameworks, libraries, databases and platforms are approved | `references/tech-stack.md` (generated from `references/stack.json`) |
| How code is structured, integrates, authenticates, logs and deploys | `references/patterns.md` |
| Repo layout, testing, linting, naming, error handling, dependencies | `references/coding-standards.md` |
| Default non-functional requirements (availability, security, data) | `references/nfr.md` |

## Standard IDs

Every rule has a stable ID (`AP-03`, `PAT-07`, `CS-02`, `NFR-04`, `STK-…`).
Cite IDs in technical documents (design briefs, ADRs, the production
handoff, review reports) so engineers can trace every decision. Don't use
them in messages to the builder.

## Tech radar statuses

| Status | Meaning | What you do |
| --- | --- | --- |
| **adopt** | Default choice. | Use it. |
| **trial** | Allowed for new work. | Use it only if no `adopt` option fits; record it in the production handoff (needs an engineering owner). |
| **hold** | No new usage. | Use the `adopt` alternative instead. |
| **retire** | Being removed. | Never add. Record existing usage as a production gap. |
| *(not listed)* | Unassessed. | Use the closest `adopt` option. If nothing approved can meet the business need, use it behind a swappable boundary (PAT-19) and record an exception ADR. |

## How to apply the standards — decide, don't ask

The people building with this kit care about business outcomes, not
technology. You own every technical decision.

1. **Default to the standard, silently.** Pick the `adopt` option and the
   golden-path pattern. Record the choice in technical docs, not in chat.
2. **Never present technical options to the builder.** If a choice depends
   on something you don't know, ask the *business* question behind it (see
   the `business-context` skill) and derive the technical answer yourself.
3. **Off-standard request from the builder** (e.g. "use MongoDB", "put it on
   Vercel"): treat it as a wish for an outcome. Deliver the outcome on the
   approved stack and tell them in one plain sentence ("I've used the
   company's standard database — it does everything you need and makes going
   live easier."). If they insist, keep the approved option underneath and
   note their preference in the production handoff for the engineering team.
4. **Genuine business need that only an off-standard option can meet:**
   decide, isolate it behind a port/adapter (PAT-19) so it can be swapped
   later, write an exception ADR (`write-adr`) and add it to the handoff.
   Don't ask the builder to approve it.
5. **Non-negotiables (`NN-*`) are never bypassed.** Explain the business
   risk plainly and offer the safe route to the same outcome.
6. **Never invent standards.** If the references don't cover something,
   choose consistently with the principles and mark it UNASSESSED in the
   handoff for the architecture team to confirm.

## Keeping this current

The files under `references/` contain illustrative defaults marked `TODO`.
The architecture team owns them. Replace the examples with your real
standards and keep the IDs stable once published — renumbering breaks ADRs.
