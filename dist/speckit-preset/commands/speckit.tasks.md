## Enterprise Rules for Tasks

Apply the *Enterprise Task Rules* section of the tasks template:

- Setup from the golden path (`scaffold-service`) for a new deployable.
- One foundational task group per port in plan.md's *Ports and Adapters*
  table: local adapter, production adapter or fail-fast stub, config switch,
  contract test.
- Tasks grouped by module (business capability) with module-layout paths.
- Each user story ends with parallel `architecture_reviewer` and
  `readability_reviewer` review tasks (apply fix-now items) and a
  `handoff_scribe` update task.
- No task asks the builder a technical question.
