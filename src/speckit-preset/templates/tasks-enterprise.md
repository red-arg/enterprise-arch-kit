## Enterprise Task Rules

<!-- Applied to every generated task list. These override the template's
     "tests are optional" notes: tests are mandatory and always come first. -->

- **Setup phase** starts from the golden path in plan.md (`scaffold-service`
  skill) when the deployable doesn't exist yet: one-command local run, test
  runner with JUnit XML output, `.tdd/` git-ignored, CI with
  `stack-check --strict`, and `docs/production-handoff.md`. Setup is not
  behaviour, so it has no RED step — but it ends with one passing smoke test.
- **Foundational phase** creates the functional test harness
  (`test/functional/support/`: start with local profile, base URL, role
  logins, documented test controls) and the ports from plan.md's *Ports and
  Adapters* table (local adapter, production adapter or fail-fast stub,
  config switch). Ports get no tests of their own — the functional suite
  verifies them.
- **Every user story follows the test-first cycle (`tdd` skill), as separate
  tasks in this order:**
  1. `[RED] test_writer`: failing functional tests for the story's
     acceptance scenarios, rules and functional edge cases — from spec.md,
     acceptance examples and contracts only, through the external interface.
  2. `[STUB] implementer`: new contract operations answer 501 (if any).
  3. `[GATE] verify-red`: every new test fails for the right reason.
  4. `[GREEN] implementer`: make the tests pass; tests untouched.
  5. `[GATE] verify-green`: suite passes, tests unchanged since RED.
  6. `[REFACTOR] implementer`: tidy with the suite green.
  7. `[REVIEW]` `architecture_reviewer` and `readability_reviewer` in
     parallel; apply fix-now items through the same agents.
  8. `[HANDOFF] handoff_scribe`: update the production handoff.
- **Tasks are grouped by module** (business capability), and paths follow
  the module layout: `src/modules/<capability>/{domain,application,ports,adapters/local,adapters/production,api}`,
  functional tests under `test/functional/<capability>/`. No unit, port or
  adapter test tasks.
- **No task asks the builder a technical question.** Tasks needing a business
  fact reference the open question in the handoff instead.
