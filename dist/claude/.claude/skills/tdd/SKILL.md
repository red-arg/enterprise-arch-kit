---
name: tdd
description: Mandatory three-agent flow for every implementation task - test_writer writes failing functional tests (in-process unit tests through modules' public interfaces) from the business requirements, implementer makes them pass without touching tests, and architecture_reviewer checks the result against enterprise standards, architecture and tech stack before the task is done. Gates catch vacuous tests, test tampering and skipped steps. Use for every task that changes the project.
---

# Every task: test_writer → implementer → architecture_reviewer

**Every single implementation task** — a feature, a business rule, a fix, a
setup step, even a one-line cosmetic change — goes through three separate
agents, in this order, with no exceptions:

1. **`test_writer`** turns the business requirements into failing
   **functional tests written as unit tests**: in-process, with the project's
   unit test framework, calling only each module's **public interface**
   through the **test app factory**. They check business outcomes, including
   functional edge cases. No browser, no Playwright, no HTTP, no running
   server. It never sees anything behind the public interface, so everything
   there can later be refactored onto enterprise standards and the same tests
   prove the business behaviour is unchanged. Rules, edge-case checklist and
   the tautology ban: `references/test-rules.md`.
2. **`implementer`** makes those tests pass and refactors. It never creates,
   edits or deletes tests. If a test seems wrong, it reports back instead.
3. **`architecture_reviewer`** reviews the task's changes against the
   enterprise standards, architecture and tech stack. The task is done only
   when its verdict is **PASS**.

You (the main agent) orchestrate and run the gates — you never write tests
or production code yourself. The builder never sees any of it; they hear
about outcomes ("You can now approve requests. Saved.").

## What counts as a task

The smallest unit of work you'd describe as one change: a Spec Kit task, one
acceptance scenario or rule, one fix, one cosmetic tweak, one setup step.
Several tiny related changes requested together may be one task. Never batch
unrelated changes to save reviews.

## Tasks with no business behaviour

For wording, colours, layout, tooling or setup, `test_writer` still runs
first. It checks whether any business behaviour is affected; if not, it
returns a **no-test declaration** with the reason (e.g. "colour only — no
business behaviour"), and confirms the existing suite still describes the
behaviour. Record it as a `TDD-No-Test: <reason>` trailer, skip STUB and
verify-red, and continue with GREEN and the review. A no-test declaration is
never acceptable for anything a user could observe as different behaviour.

## The public interface and the test app factory

- **Public interface:** each module (business capability) declares its
  operations, input/output types and business errors in one public file —
  `src/modules/<capability>/index.ts`, `.../__init__.py`, or the module's
  `public/` package. It's business-named ("submit leave request"), contains
  no logic, and doesn't re-export internal types.
- **Test app factory** (`src/app/test-app.*` or `app/test_app.py`):
  scaffolding creates it. It wires the application in memory with the local
  adapters (in-memory storage, fake outside systems with sample data) and
  exposes the documented **test controls** — fixed clock, acting business
  user/role, outside-system data. Each test builds a fresh app with it.
- Functional tests live in `test/functional/<capability>/` and run with the
  normal unit test command. They're fast — run them constantly.

## The flow for one task

Scripts are in this skill's `scripts/` folder; results go in `.tdd/`
(git-ignored); use JUnit XML output (see *Running the suite*). Note the
commit before you start — the task's **base**.

**0. Baseline.** Run the whole suite → `.tdd/before/`. It must be green; if
not, fix that first as its own task.

**1. RED — `test_writer`.** Delegate with: the task (spec path and scenario
IDs, or the request in plain words), the plan's acceptance examples and
*Functional Test Boundary*. It returns failing tests with a scenario ID and
`Catches:` note per test — or a no-test declaration. Commit the tests:
`Add failing tests: <behaviour>` with trailer `TDD-Step: red`, and note it as
the *red commit*.

**2. STUB — `implementer`** (only for operations that don't exist yet). Add
each new operation to the module's public interface with its types and
business errors, throwing "not implemented". No logic.

**3. Verify red (gate).** Run the suite → `.tdd/after-red/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-red --before .tdd/before --after .tdd/after-red
```

- **VACUOUS** (a new test passes before implementation): if the stub contains
  logic, have the implementer strip it back; otherwise send the test back to
  `test_writer` to fix or delete (or keep it explicitly as a regression test).
- **WRONG REASON** (test can't load or the app can't be built): the
  implementer adds the missing stub or fixes the factory.
- **SKIPPED**: back to `test_writer`.
Repeat until it passes; amend the red commit if tests changed.

**4. GREEN — `implementer`.** Delegate with: the red commit, the failing
tests, the plan. It writes the simplest code that passes them on the golden
path, then refactors with the suite green.

**5. Verify green (gate).** Run the suite → `.tdd/after-green/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-green --since <red-commit> --results .tdd/after-green
```

It fails if any test isn't passing **or any test file changed after the red
commit** (revert test changes with `git checkout <red-commit> -- <files>` and
send the implementer back). If the implementer reported a wrong test, take it
to `test_writer` with the spec reference — the spec decides. Commit:
`Implement <behaviour>` with trailer `TDD-Step: green` (no-test tasks: add
`TDD-No-Test: <reason>` to this commit).

**6. REVIEW — `architecture_reviewer` (mandatory).** Delegate in *task
mode* with the task's base commit and a one-line description. It reviews the
task's diff against the enterprise standards, architecture and tech stack
(running `stack-check`) and ends with `VERDICT: PASS`, `CHANGES_REQUIRED` or
`BLOCKED`.

- **PASS** → record it in an **empty** commit:
  `git commit --allow-empty -m "Review: <task>" -m "TDD-Review: PASS"`.
- **CHANGES_REQUIRED** → optionally record `TDD-Review: CHANGES_REQUIRED` in
  an empty commit, send the *fix now* items to `implementer` (tests untouched,
  verify-green again, commit with `TDD-Step: green`), then review again.
  Findings about test quality go to `test_writer`. After two rounds, record
  what's left as production gaps via `handoff_scribe` only if the reviewer
  marked them *record for production*; *fix now* items must be fixed.
- **BLOCKED** (non-negotiable breached) → fix before anything else; the task
  can't close until a later review passes.

**7. Close the task (gate).**

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-task --base <task-base-commit>
```

It checks the commit trail since the base: a `TDD-Step: red` (or
`TDD-No-Test`) commit, a `TDD-Step: green` commit after it, and the **last**
commit carrying `TDD-Review: PASS` with no file changes — so nothing changed
after the review. Only then is the task done. Then tell the builder the
outcome in plain words.

**Per user story (in addition):** when all its tasks are closed, run
`readability_reviewer` and have `handoff_scribe` update the production
handoff; readability fixes go through the same flow as a new task.

## Functional tests and productionization

Because the suite only uses public interfaces and the factory, it keeps
passing through any refactor behind them — that's how engineers prove a
restructure onto enterprise standards changed nothing for the business. In an
integration environment the factory can also be configured with the
production adapters (real database, corporate login in a test tenant) to run
the same suite as a readiness check. Record results in the production
handoff. (A rewrite in a different language would need the tests ported —
they're specifications, so that's a translation, not a redesign.)

## Running the suite with JUnit XML

| Stack | Command |
| --- | --- |
| TypeScript (Vitest) | `npx vitest run --reporter=default --reporter=junit --outputFile.junit=.tdd/<step>/junit.xml` |
| Python (pytest) | `pytest --junitxml=.tdd/<step>/junit.xml` |
| Java (Gradle) | `./gradlew test` then copy `build/test-results/test/*.xml` to `.tdd/<step>/` |
| Java (Maven) | `mvn test` then copy `target/surefire-reports/*.xml` to `.tdd/<step>/` |
| Go | `gotestsum --junitfile .tdd/<step>/junit.xml ./...` |

Make sure `.tdd/` is in `.gitignore`.

## Enforcement — what's guaranteed and how

| Rule | Claude Code | Codex |
| --- | --- | --- |
| test_writer sees only public interfaces and the factory | Hook blocks reading/searching anything else in source folders | Agent instructions |
| test_writer writes only tests | Hook blocks writes outside test files | Agent instructions |
| implementer never changes tests | Hook blocks writes/deletes of test files | Agent instructions |
| Tests unchanged during green | `verify-green` git check | `verify-green` git check |
| No vacuous/tautological tests | `verify-red` gate + rules + readability review | same |
| Every task went test_writer → implementer → reviewer PASS | `verify-task` (commit trail) | `verify-task` (commit trail) |

Folders treated as tests, implementation and public interface can be tuned
per project in `.tdd-boundary.json` (see the script's header).
