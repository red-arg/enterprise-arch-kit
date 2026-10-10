---
name: tdd
description: Test-first build cycle for every behaviour change - test_writer writes failing functional tests, in the form of in-process unit tests, from the business requirements and calls only modules' public interfaces; implementer makes them pass without touching tests; automatic gates catch vacuous tests and test tampering. Use whenever adding or changing behaviour (features, business rules, fixes).
---

# Test-first build cycle

Every behaviour change is built test-first by two separate agents:

- **`test_writer`** turns the business requirements into failing
  **functional tests written as unit tests**: in-process, with the project's
  unit test framework, calling only each module's **public interface**
  through the **test app factory** (in-memory local profile). They check
  business outcomes, including functional edge cases. No browser, no
  Playwright, no HTTP, no running server. It never sees anything behind the
  public interface, so everything there can later be refactored onto
  enterprise standards and the same tests prove the business behaviour is
  unchanged. Rules, edge-case checklist and the tautology ban:
  `references/test-rules.md`.
- **`implementer`** makes those tests pass. It never creates, edits or deletes
  tests. If a test seems wrong, it reports back instead.

You (the main agent) run the cycle and the gates. The builder never sees any
of it — they hear about outcomes ("You can now approve requests. Saved.").

## When to use it

- **Yes:** new features, business rules, calculations, permissions,
  validations, integrations, bug fixes (the first test reproduces the bug).
- **No:** purely cosmetic changes (wording, colours, layout, spacing) and
  scaffolding/tooling setup. Make those directly, then run the whole suite —
  it must stay green.
- **Never:** tests of internal parts (classes, use-case internals, ports,
  adapters, storage), and no browser, HTTP or end-to-end tests. Only
  functional unit tests through public interfaces are written in this cycle;
  engineering may add others during production hardening.

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

## The cycle (per slice: one user story or a few acceptance scenarios)

Scripts below are in this skill's `scripts/` folder. Test results go in
`.tdd/` (git-ignored). Use JUnit XML output — see *Running the suite*.

**0. Baseline.** Run the whole suite → `.tdd/before/`. It should be green; if
not, fix that first (outside this cycle).

**1. RED — `test_writer`.** Delegate with: the slice (spec path and scenario
IDs, or the request in plain words), the plan's acceptance examples and
*Functional Test Boundary* (public operations, factory, test controls). It
returns the test files with a scenario ID and "Catches" note per test, plus
any gaps in the public interface or test controls. Commit: `Add failing tests: <behaviour>` and note
the commit id (the *red commit*).

**2. STUB — `implementer`** (only for operations that don't exist yet). Add
each new operation to the module's public interface with its input/output
types and business errors, throwing a "not implemented" error. No logic. The
test app factory must still build.

**3. Verify red (gate).** Run the suite → `.tdd/after-red/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-red --before .tdd/before --after .tdd/after-red
```

- **VACUOUS** (a new test passes before implementation): if the stub contains
  logic, have the implementer strip it back to a stub; otherwise send the
  test back to `test_writer` to fix or delete — it's tautological, or the
  behaviour already exists (then it's kept as a regression test, explicitly).
- **WRONG REASON** (test can't load or the app can't be built): the
  implementer adds the missing stub or fixes the factory.
- **SKIPPED**: back to `test_writer`.
Repeat until the gate passes. Amend the red commit if tests changed.

**4. GREEN — `implementer`.** Delegate with: the red commit id, the failing
tests, the plan. It writes the simplest code that passes them, on the golden
path (modules, ports, local adapters), running the suite as it goes. It doesn't
add tests of its own — test files belong to `test_writer` — it verifies its
work with the functional suite.

**5. Verify green (gate).** Run the suite → `.tdd/after-green/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-green --since <red-commit> --results .tdd/after-green
```

It fails if any test isn't passing **or any test file changed after the red
commit**. If tests were touched, revert those changes
(`git checkout <red-commit> -- <test files>`) and send the implementer back.
If the implementer reported a wrong test, take it to `test_writer` with the
spec reference — the spec decides, never the implementation. Commit:
`Implement <behaviour>`.

**6. REFACTOR — `implementer`.** Improve structure with the suite green and
tests untouched; then verify green again and commit. Then run the reviews
(`architecture_reviewer`, `readability_reviewer`) as usual; fixes they
require go through the implementer and must keep the gate green.

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

Folders treated as tests, implementation and public interface can be tuned
per project in `.tdd-boundary.json` (see the script's header).
