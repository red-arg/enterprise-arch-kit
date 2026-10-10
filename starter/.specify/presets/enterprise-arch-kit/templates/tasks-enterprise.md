## Enterprise Task Rules

<!-- Applied to every generated task list. -->

- **Setup phase** starts from the golden path in plan.md (`scaffold-service`
  skill) when the deployable doesn't exist yet, including the one-command
  local run, CI with `stack-check --strict`, and `docs/production-handoff.md`.
- **Foundational phase** creates each port from plan.md's *Ports and
  Adapters* table with its local adapter, its production adapter or
  fail-fast stub, the config switch, and a shared contract test.
- **Tasks are grouped by module** (business capability), and paths follow
  the module layout: `src/modules/<capability>/{domain,application,ports,adapters/local,adapters/production,api}`.
- **Every user story ends with** two review tasks — run
  `architecture_reviewer` and `readability_reviewer` in parallel and apply
  their fix-now items — and a `handoff_scribe` task to update the production
  handoff.
- **No task asks the builder a technical question.** Tasks needing a business
  fact reference the open question in the handoff instead.
