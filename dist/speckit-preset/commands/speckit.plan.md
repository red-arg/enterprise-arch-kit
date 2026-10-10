## Enterprise Rules for Planning (read first — these override the steps below where they conflict)

The technical plan is decided by the agents from the enterprise standards.
The builder is never asked for a tech stack, architecture or trade-off.

1. **Delegate the design to the `solution_designer` agent.** In Claude Code,
   use the `solution_designer` subagent; in Codex, spawn the
   `solution_designer` agent and wait for it. Pass it: the paths of
   `FEATURE_SPEC`, `IMPL_PLAN` (the copied plan template) and
   `FEATURE_DIR`, the constitution, and any user input above. It fills
   `plan.md` — including the *Enterprise Alignment* section — and produces
   `research.md`, `data-model.md`, `contracts/` and `quickstart.md` as
   described below. If delegation isn't available, do the same work yourself
   following the `solution_designer` instructions and the
   `enterprise-standards`, `scaffold-service` (golden paths) and
   `stack-check` skills.
2. **Technical Context is decided, not asked.** Fill every field from the
   enterprise standards and the spec's Business Context (derived via the
   `business-context` mapping). `NEEDS CLARIFICATION` is allowed only for a
   missing *business* fact; resolve it by asking the builder that plain
   business question (at most 3), or by using the default and marking it
   Assumed in the spec and the handoff §9.
3. **research.md records decisions with standard IDs.** For each decision:
   Decision, Rationale (business need + standard ID), Alternatives
   considered (including the standard option when an exception is taken).
4. **Project Structure follows the golden path**: modules by business
   capability (PAT-20) and ports with local and production adapters
   (PAT-19). Replace the template's generic options with that layout.
5. **Constitution Check uses the enterprise constitution.** Any violation
   goes in Complexity Tracking with an exception ADR (`write-adr`).
6. **quickstart.md** starts with the one-command local run.
7. **After planning,** have `handoff_scribe` update
   `docs/production-handoff.md` §3–§5 and §7 from the plan, and link it.
8. **Report to the builder in plain language** (what will be built and what
   they'll be able to do). Branch names, file paths and standard IDs are for
   the agents; include them only if the builder asks.
