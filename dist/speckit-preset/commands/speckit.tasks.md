## Enterprise Rules for Tasks

Apply the *Enterprise Task Rules* section of the tasks template. Tests are
**mandatory and first**, regardless of any "tests are optional" wording above:

- Setup from the golden path (`scaffold-service`) for a new deployable,
  ending with a passing smoke test.
- Public interface files, test app factory and ports in the foundational
  phase; ports get no tests of their own.
- Only functional unit test tasks through public interfaces: no tests of
  internal parts, no browser or HTTP tests.
- **Every task** (setup, foundational, story, polish) runs through
  `test_writer` → `implementer` → `architecture_reviewer` (must PASS), as in
  the template: `[RED]` → `[STUB]` → `[GATE] verify-red` → `[GREEN]` →
  `[GATE] verify-green` → `[REVIEW] architecture_reviewer` →
  `[GATE] verify-task`. No-behaviour tasks get a no-test declaration from
  `test_writer` instead of tests, never a skipped step.
- Per completed user story: `[REVIEW] readability_reviewer` and
  `[HANDOFF] handoff_scribe`.
- Tasks grouped by module (business capability) with module-layout paths.
- No task asks the builder a technical question.
