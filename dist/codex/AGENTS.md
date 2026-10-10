## Enterprise architecture alignment

This project follows the enterprise architecture standards, approved tech
stack and patterns in the `enterprise-standards` skill. Your job is to help
the developer move fast **and** stay aligned: default to the standard, explain
deviations briefly, and record exceptions as ADRs. Guide — don't block.

### Defaults

- Choose `adopt` technologies and golden-path patterns unless told otherwise,
  and say in one line which standard you followed (cite the ID, e.g. PAT-05).
- Before adding any dependency, check it with the `stack-check` skill.
- If the developer asks for something off-standard: explain the standard and
  why it exists in a sentence or two, offer the compliant option, and if they
  still want it, proceed and offer an exception ADR (`write-adr` skill).
- Non-negotiables (`NN-*`: secrets in code, prod data in non-prod,
  unauthenticated external endpoints, unapproved registries) are never
  bypassed. Explain and stop.

### When to delegate to the architecture agents

Delegate these automatically — the developer doesn't need to ask:

| Situation | Agent |
| --- | --- |
| Starting something new: an app, service, data store, integration, or a feature whose approach is unclear | `solution_designer` — then build with the `scaffold-service` skill |
| Dependencies were added or changed | `stack_guardian` |
| A feature is finished, before a commit/PR, or the developer asks "is this OK?" | `architecture_reviewer` and `readability_reviewer`, in parallel |
| The developer asks about readability, clean code or maintainability | `readability_reviewer` |
| A deviation or significant decision was agreed | `adr_scribe` |

Relay each agent's summary to the developer in plain language. Don't paste
raw reports when a three-line summary will do; offer the full report.

### Records

- Design briefs live in `docs/design/`. ADRs live in `docs/adr/`.
- Code that implements an exception carries a comment pointing at its ADR.
