---
name: tdd
description: Test-first build cycle for every behaviour change - test_writer writes failing functional (black-box) tests from the business requirements without seeing any source code, implementer makes them pass without touching tests, with automatic gates for vacuous tests and test tampering. Use whenever adding or changing behaviour (features, business rules, fixes).
---

# Test-first build cycle

Every behaviour change is built test-first by two separate agents:

- **`test_writer`** turns the business requirements into failing
  **functional tests** that drive the running system from outside — through
  its API, a browser for critical journeys, or a job's inputs and outputs —
  and check business outcomes, including functional edge cases. It never
  sees source code. Because the tests know nothing about how the system is
  built, the code can later be refactored or re-platformed onto enterprise
  standards and the same tests prove the business behaviour is unchanged.
  Rules, edge-case checklist and the tautology ban: `references/test-rules.md`.
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
- **Never:** unit, port, adapter or integration tests of internal parts.
  Only functional tests are written in this cycle; engineering may add
  others during production hardening.

## The functional harness

Scaffolding (`scaffold-service`) creates `test/functional/support/`: it
starts the system with the **local profile** exactly as `quickstart.md`
describes (fresh embedded data per run), exposes its base URL, a client for
the contract, a dev-login helper per business role, and any test controls the
plan documents (e.g. a fixed clock). After scaffolding, the harness belongs to
`test_writer`. Functional tests live in `test/functional/<capability>/`.

## The cycle (per slice: one user story or a few acceptance scenarios)

Scripts below are in this skill's `scripts/` folder. Test results go in
`.tdd/` (git-ignored). Use JUnit XML output — see *Running the suite*.

**0. Baseline.** Run the whole suite → `.tdd/before/`. It should be green; if
not, fix that first (outside this cycle).

**1. RED — `test_writer`.** Delegate with: the slice (spec path and scenario
IDs, or the request in plain words), the plan's acceptance examples and test
controls, the contract (`contracts/` / OpenAPI) and the harness location. It
returns the test files with a scenario ID and "Catches" note per test, plus
any gaps in the contract. Commit: `Add failing tests: <behaviour>` and note
the commit id (the *red commit*).

**2. STUB — `implementer`** (only for operations the system doesn't expose
yet). Add each operation from the contract so it exists and answers "not
implemented" (HTTP 501, or the job/worker equivalent). No logic. The system
must start with the local profile.

**3. Verify red (gate).** Run the suite → `.tdd/after-red/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-red --before .tdd/before --after .tdd/after-red
```

- **VACUOUS** (a new test passes before implementation): if the stub contains
  logic, have the implementer strip it back to a stub; otherwise send the
  test back to `test_writer` to fix or delete — it's tautological, or the
  behaviour already exists (then it's kept as a regression test, explicitly).
- **WRONG REASON** (test can't load or the system didn't start): the
  implementer adds the missing stub or fixes startup.
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

Because the suite only uses the external interface and test controls, the
same tests verify the production setup: run it with the production profile
(production adapters, real database, corporate login in a test tenant) as a
readiness check, and after any refactor or re-platforming onto enterprise
standards. Record the result in the production handoff.

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
| test_writer can't read source code | Hook blocks reading/searching source folders | Agent instructions |
| test_writer writes only tests | Hook blocks writes outside test files | Agent instructions |
| implementer never changes tests | Hook blocks writes/deletes of test files | Agent instructions |
| Tests unchanged during green | `verify-green` git check | `verify-green` git check |
| No vacuous/tautological tests | `verify-red` gate + rules + readability review | same |

Folders treated as tests, implementation and public interface can be tuned
per project in `.tdd-boundary.json` (see the script's header).
