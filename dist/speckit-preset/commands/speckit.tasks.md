## Enterprise Rules for Tasks

Apply the *Enterprise Task Rules* section of the tasks template. Tests are
**mandatory and first**, regardless of any "tests are optional" wording above:

- Setup from the golden path (`scaffold-service`) for a new deployable,
  ending with a passing smoke test.
- Ports built test-first: contract tests by `test_writer`, then adapters by
  `implementer`.
- Every user story as the test-first cycle in order: `[RED] test_writer` →
  `[STUB] implementer` → `[GATE] verify-red` → `[GREEN] implementer` →
  `[GATE] verify-green` → `[REFACTOR] implementer` → `[REVIEW]` →
  `[HANDOFF] handoff_scribe`.
- Tasks grouped by module (business capability) with module-layout paths.
- No task asks the builder a technical question.
