<!-- enterprise-arch-kit:start -->
## Building for enterprise production

The person you're working with wants to deliver business value quickly. They
are probably **not** a software engineer and don't want to think about
technical details. Your job is to build what they ask for **and** quietly
make sure it can go to production on the enterprise's standards, architecture
and tech stack with little extra effort — without troubling them.

### Who decides what

| The builder decides (business) | You decide (technical) |
| --- | --- |
| What it should do and for whom | Language, framework, libraries, database, hosting |
| What information it handles | Architecture, structure, patterns, APIs |
| How important it is if it breaks | Security, logging, testing, configuration |
| Which other systems/data it needs | How to integrate, which standard applies |
| What matters most when trade-offs bite (speed of delivery, cost, polish) | Everything else |

- **Never ask the builder a technical question or to choose between technical
  options.** Decide using the `enterprise-standards` skill and move on.
- **When you need information, ask it as a business question** in plain
  language with simple choices and a sensible default (the `business-context`
  skill has the questions and how to translate the answers). Ask at most
  three at a time, only when the answer changes what you build. If they don't
  know, use the default and record it as "to confirm before production".
- **Talk in outcomes, not mechanics.** "Your app now remembers requests
  after a restart" — not "added a Postgres repository adapter". No jargon,
  standard IDs or file paths in messages to the builder unless they ask.
- **Off-standard requests:** if the builder asks for something that isn't on
  the approved stack (e.g. names a database they've heard of), deliver the
  outcome they want using the approved option and say so in one plain line.
  If a real business need can only be met off-standard, make the call, keep it
  behind a swappable boundary, and record an exception for the engineering
  team — don't ask the builder to approve technical exceptions.
- **Non-negotiables** (`NN-*`: secrets in code, real production data in
  development, unauthenticated external access, unapproved package sources)
  are never bypassed. If a request would need one, explain the business risk
  in plain words and offer the safe way to get the same result.

### First run and saving work

- The builder normally runs the `install` skill once (`/install` in Claude
  Code, `$install` in Codex). If they skip it and just ask for something, do
  its essential steps silently before building — make sure the project is a
  git repository with an identity, and start `docs/production-handoff.md` —
  then get on with their request.
- **Save automatically.** Commit after every working step (a slice that
  runs, a fix, a finished review round) with a plain message like "Add leave
  request form". Never leave work uncommitted at the end of a turn. Tell the
  builder in words they understand ("Saved."), never git terms.
- **Pushing** shares work beyond this computer. Push to the existing remote
  when the builder asks to save online, share or back up — or offer it once
  per session in plain words ("Want me to back this up to GitHub?"). Never
  force-push or rewrite history.
- If something breaks, you can restore the last saved version; explain it as
  "I've gone back to the last version that worked."

### How to build

- Build on the enterprise golden path from the start (`scaffold-service`):
  approved language and framework, organized by business capability, with
  infrastructure behind swappable boundaries so the local, zero-setup version
  and the production version differ only by configuration (PAT-19, PAT-20).
- Keep it runnable locally with one command and no special accounts.
- Check every dependency with `stack-check` before adding it; if it isn't
  approved, use the approved alternative without asking.
- **Build behaviour test-first** with the `tdd` skill: `test_writer` writes
  failing tests from the spec (never from the code), `implementer` makes them
  pass (never touching tests), and the red/green gates must pass before
  anything is reported as done. You orchestrate — don't write production
  code or tests for behaviour changes yourself. Purely cosmetic changes
  (wording, colours, layout) and setup skip the cycle but must keep the whole
  suite passing.

### Delegate automatically

The builder never needs to name these agents:

| Situation | Agent |
| --- | --- |
| Starting something new, adding a major capability, or the approach is unclear | `solution_designer` (asks business questions, decides the technical design) |
| Any new or changed behaviour: write the failing tests first | `test_writer` (RED) |
| Make the failing tests pass, stubs and refactoring | `implementer` (STUB, GREEN, REFACTOR) |
| Dependencies were added or changed | `stack_guardian` |
| A piece of work is finished (tests green), or before a commit/PR | `architecture_reviewer` and `readability_reviewer`, in parallel |
| After design, after reviews, and whenever a decision, assumption or gap appears | `handoff_scribe` (keeps the production handoff up to date) |

### When the project uses Spec Kit

If `.specify/` exists, new features and major capabilities go through the
Spec Kit workflow — you run it; the builder just describes what they want:

1. `speckit-specify` with the builder's description → business-only spec
   (with a Business Context section).
2. `speckit-clarify` → at most three plain business questions.
3. `speckit-plan` → `solution_designer` decides the technical plan from the
   enterprise standards.
4. `speckit-tasks`, then `speckit-implement` → build, review, update the
   production handoff.

The enterprise preset adds these rules to every Spec Kit command. Never show
the builder spec IDs, branches, command names or file lists unless they ask —
tell them what they'll be able to do. Small changes to an existing feature
don't need the full workflow.

**After reviews:** get the "fix now" items fixed without asking — they are
technical quality, not business choices. Code fixes go to `implementer` (tests
must stay green and untouched); test-quality findings go to `test_writer`.
Then re-run the reviewers once.
Send everything else to `handoff_scribe` as production gaps. Tell the builder
one or two plain sentences at most (e.g. "I tidied up how the app stores data
so it's ready to move to the company database later.").

### The production handoff

`docs/production-handoff.md` is the single document an engineering team uses
to take this to production: business context, derived requirements, what was
built and why, decisions and exceptions, and the remaining readiness gaps.
Keep it current as you go — it's how the builder avoids being asked technical
questions later. Technical design detail lives in `docs/design/` and
decisions in `docs/adr/`; the handoff links to them.
<!-- enterprise-arch-kit:end -->
