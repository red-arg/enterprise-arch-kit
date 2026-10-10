## Enterprise Rules for Implementation

These apply throughout implementation and override any step above that has
you write tests and code yourself:

1. **Every task, three agents.** Execute every task with the `tdd` skill,
   no exceptions: `test_writer` writes the failing functional unit tests
   (from spec.md and the plan, calling only public interfaces through the test
   app factory — never internals) or a no-test declaration for work with no
   business behaviour; `implementer` creates stubs, makes them pass and
   refactors (never touching tests); `architecture_reviewer` checks the
   task's changes against enterprise standards, architecture and tech stack
   and must return `VERDICT: PASS` (fix-now items go back to `implementer`).
   Run `verify-red`, `verify-green` and `verify-task` between steps, and
   don't mark a task `[X]` until `verify-task` passes. Don't write tests or
   production code yourself.
2. **Golden path and standards.** The implementer builds per plan.md's
   *Enterprise Alignment* section, checks every new dependency with
   `stack-check`, keeps business code free of infrastructure imports
   (PAT-19) and modules independent (PAT-20).
3. **After each user story:** run `readability_reviewer`; its fixes become
   new tasks through the same three-agent flow; send *record for production*
   items from all reviews to `handoff_scribe`.
4. **Keep the local run working** — the one command in quickstart.md must
   still start the app with sample data.
5. **Save at each step, with trailers:** commit RED with
   `TDD-Step: red` (or put `TDD-No-Test: <reason>` on the green commit),
   GREEN and fixes with `TDD-Step: green`, and the reviewer's PASS in an empty
   commit with `TDD-Review: PASS` — `verify-task` reads these.
6. **Update the production handoff** via `handoff_scribe`: architecture as
   built, port status, test and review results, gaps, readiness verdict.
7. **Tell the builder the outcome in one or two plain sentences** — what
   they can now do and how to try it. No tests, task IDs, file lists or
   standard IDs unless they ask.
