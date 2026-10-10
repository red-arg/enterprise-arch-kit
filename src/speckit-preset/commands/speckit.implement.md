## Enterprise Rules for Implementation

These apply throughout implementation and override any step above that has
you write tests and code yourself:

1. **Test-first, two agents.** Execute each user story's tasks with the
   `tdd` skill: `test_writer` writes the failing functional unit tests
   (from spec.md and the plan, calling only public interfaces through the test
   app factory — never internals), `implementer`
   creates stubs, makes them pass and refactors (never touching tests). You
   run the `verify-red` and `verify-green` gates between steps and don't
   mark a task done until its gate passes. Don't write tests or production
   code for behaviour yourself.
2. **Golden path and standards.** The implementer builds per plan.md's
   *Enterprise Alignment* section, checks every new dependency with
   `stack-check`, keeps business code free of infrastructure imports
   (PAT-19) and modules independent (PAT-20).
3. **After each user story:** run `architecture_reviewer` and
   `readability_reviewer` in parallel; send code fixes to `implementer` and
   test-quality findings to `test_writer`, with the gates still passing;
   re-run the reviews once; send *record for production* items to
   `handoff_scribe`.
4. **Keep the local run working** — the one command in quickstart.md must
   still start the app with sample data.
5. **Save at each step:** commit after RED (tests), GREEN and REFACTOR with
   plain messages.
6. **Update the production handoff** via `handoff_scribe`: architecture as
   built, port status, test and review results, gaps, readiness verdict.
7. **Tell the builder the outcome in one or two plain sentences** — what
   they can now do and how to try it. No tests, task IDs, file lists or
   standard IDs unless they ask.
