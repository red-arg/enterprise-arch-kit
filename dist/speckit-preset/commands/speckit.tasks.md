## Enterprise Rules for Tasks

Apply the *Enterprise Task Rules* section of the tasks template. Tests are
**mandatory and first**, regardless of any "tests are optional" wording above:

- Setup from the golden path (`scaffold-service`) for a new deployable,
  ending with a passing smoke test.
- Functional test harness and ports in the foundational phase; ports get no
  tests of their own — the functional suite verifies them.
- Only functional (black-box) test tasks: no unit, port or adapter tests.
- Every user story as the test-first cycle in order: `[RED] test_writer` →
  `[STUB] implementer` → `[GATE] verify-red` → `[GREEN] implementer` →
  `[GATE] verify-green` → `[REFACTOR] implementer` → `[REVIEW]` →
  `[HANDOFF] handoff_scribe`.
- Tasks grouped by module (business capability) with module-layout paths.
- No task asks the builder a technical question.
