## Enterprise Rules for Implementation

These apply throughout implementation and after the last task:

1. **Golden path and standards.** Build per plan.md's *Enterprise Alignment*
   section. Check every new dependency with the `stack-check` skill and use
   the approved alternative without asking. Keep business code free of
   infrastructure imports (PAT-19) and modules independent (PAT-20).
2. **After each user story** (or the whole run, if small): run
   `architecture_reviewer` and `readability_reviewer` in parallel, apply
   their *fix now* items yourself, re-run them once, and send *record for
   production* items to `handoff_scribe`.
3. **Keep the local run working** — the one command in quickstart.md must
   still start the app with sample data.
4. **Update the production handoff** via `handoff_scribe`: architecture as
   built, port status, review results, gaps, readiness verdict.
5. **Tell the builder the outcome in one or two plain sentences** — what
   they can now do and how to try it. No task IDs, file lists or standard
   IDs unless they ask.
