## Enterprise Rules for Tasks

Apply the *Enterprise Task Rules* section of the tasks template. Tests are
**mandatory and first**, regardless of any "tests are optional" wording above:

- Setup from the golden path (`scaffold-service`) for a new deployable,
  ending with a passing smoke test.
- Public interface files, test app factory and ports in the foundational
  phase; ports get no tests of their own.
- Only functional unit test tasks through public interfaces: no tests of
  internal parts, no browser or HTTP tests.
- Every user story as the test-first cycle in order: `[RED] test_writer` →
  `[STUB] implementer` → `[GATE] verify-red` → `[GREEN] implementer` →
  `[GATE] verify-green` → `[REFACTOR] implementer` → `[REVIEW]` →
  `[HANDOFF] handoff_scribe`.
- Tasks grouped by module (business capability) with module-layout paths.
- No task asks the builder a technical question.
