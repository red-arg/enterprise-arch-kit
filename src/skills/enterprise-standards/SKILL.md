---
name: enterprise-standards
description: Enterprise architecture standards, approved tech stack, integration patterns and coding standards. Use whenever choosing a language, framework, library, database, cloud service or pattern, designing a component or API, or answering "are we allowed to use X?".
---

# Enterprise standards

This skill is the single source of truth for how software is built here. Every
other skill and agent in this kit cites it. Read only the reference file you
need — don't load all of them for a narrow question.

| Need to know… | Read |
| --- | --- |
| Guiding principles and non-negotiables | `references/principles.md` |
| Which languages, frameworks, libraries, databases and platforms are approved | `references/tech-stack.md` (generated from `references/stack.json`) |
| How services talk to each other, own data, authenticate, log and deploy | `references/patterns.md` |
| Repo layout, testing, linting, naming, error handling, dependencies | `references/coding-standards.md` |
| Default non-functional requirements (availability, security, data) | `references/nfr.md` |

## Standard IDs

Every rule has a stable ID (`AP-03`, `PAT-07`, `CS-02`, `NFR-04`, `STK-…`).
Always cite the ID when you point at a rule, so the developer can look it up
and so an ADR can name exactly which standard it is an exception to.

## Tech radar statuses

| Status | Meaning | What you do |
| --- | --- | --- |
| **adopt** | Default choice. | Use it without asking. |
| **trial** | Allowed for new work with a named owner. | Use it, and note it in the design or PR. |
| **hold** | Don't start new usage. Existing usage may continue. | Pick an `adopt` alternative. Using it in new code is a deviation that needs an ADR. |
| **retire** | Being removed. | Never add. Flag existing usage for migration. |
| *(not listed)* | Unassessed. | Prefer an `adopt` alternative. If none fits, flag it as UNASSESSED and suggest an ADR so the architecture team can rule on it. |

## How to apply the standards (guide, don't block)

1. **Default to the standard.** When the developer hasn't specified something,
   choose the `adopt` option and say which standard you followed in one line.
2. **When the developer asks for something off-standard, don't silently comply
   and don't refuse.** Explain the standard and why it exists in a sentence or
   two, offer the compliant alternative, and let them choose.
3. **If they still want the deviation, it needs an ADR.** Proceed only after
   offering to write one with the `write-adr` skill (status `Proposed`,
   type `Exception`, citing the standard ID). Mark the code with a comment
   pointing at the ADR, e.g. `// ADR-0007: exception to PAT-04`.
4. **Never invent standards.** If the references don't cover something, say so,
   make a reasonable choice consistent with the principles, and mark it
   UNASSESSED.

## Keeping this current

The files under `references/` contain illustrative defaults marked `TODO`.
The architecture team owns them. Replace the examples with your real
standards and keep the IDs stable once published — renumbering breaks ADRs.
