## Enterprise Task Rules

<!-- Applied to every generated task list. These override the template's
     "tests are optional" notes: tests are mandatory and always come first. -->

- **Every task — setup, foundational, story, polish — runs through three
  agents, in order:** `test_writer` (failing functional unit tests, or a
  no-test declaration for work with no business behaviour) → `implementer`
  → `architecture_reviewer` (must return `VERDICT: PASS`), closed with
  `verify-task`. Write each task's description so all three steps are
  implied; don't create tasks that bypass them.
- **Setup phase** starts from the golden path in plan.md (`scaffold-service`
  skill) when the deployable doesn't exist yet: one-command local run, test
  runner with JUnit XML output, `.tdd/` git-ignored, CI with
  `stack-check --strict`, and `docs/production-handoff.md`. `test_writer`
  writes the smoke test (the app builds from the factory).
- **Foundational phase** creates the modules' public interface files, the
  test app factory (in-memory local adapters, documented test controls) and
  the ports from plan.md's *Ports and Adapters* table (local adapter,
  production adapter or fail-fast stub, config switch). Ports get no tests of
  their own — the functional unit tests exercise them through the factory.
- **Within a user story, each task follows the `tdd` flow:**
  1. `[RED] test_writer`: failing functional unit tests for the task's
     acceptance scenarios, rules and functional edge cases — from spec.md
     and the plan, calling only public interfaces via the test app factory.
  2. `[STUB] implementer`: new public operations throw "not implemented".
  3. `[GATE] verify-red`: every new test fails for the right reason.
  4. `[GREEN] implementer`: make the tests pass and refactor; tests untouched.
  5. `[GATE] verify-green`: suite passes, tests unchanged since RED.
  6. `[REVIEW] architecture_reviewer`: standards, architecture and tech
     stack; fix-now items back to `implementer` until `VERDICT: PASS`.
  7. `[GATE] verify-task`: red/no-test → green → review PASS as last commit.
- **When a user story's tasks are all closed:** `[REVIEW] readability_reviewer`
  (fixes become new tasks through the same flow) and `[HANDOFF]
  handoff_scribe` to update the production handoff.
- **Tasks are grouped by module** (business capability), and paths follow
  the module layout: `src/modules/<capability>/{domain,application,ports,adapters/local,adapters/production,api}`,
  functional tests under `test/functional/<capability>/`. No tests of
  internal parts, and no browser or HTTP tests.
- **No task asks the builder a technical question.** Tasks needing a business
  fact reference the open question in the handoff instead.
