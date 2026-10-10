---
name: tdd
description: Test-first build cycle for every behaviour change - test_writer writes failing tests from the spec without seeing implementation, implementer makes them pass without touching tests, with automatic gates for vacuous tests and test tampering. Use whenever adding or changing behaviour (features, business rules, fixes).
---

# Test-first build cycle

Every behaviour change is built test-first by two separate agents:

- **`test_writer`** turns the spec into failing tests. It works only from the
  spec, plan, contracts and public interfaces — never the implementation —
  so tests describe *what* the business needs, not *how* it was built. Its
  rules, including the tautology ban, are in `references/test-rules.md`.
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

## The cycle (per slice: one user story or a few acceptance scenarios)

Scripts below are in this skill's `scripts/` folder. Test results go in
`.tdd/` (git-ignored). Use JUnit XML output — see *Running the suite*.

**0. Baseline.** Run the whole suite → `.tdd/before/`. It should be green; if
not, fix that first (outside this cycle).

**1. RED — `test_writer`.** Delegate with: the slice (spec path and scenario
IDs, or the request in plain words), the plan's public interfaces (module
entry points, ports, contracts), and where tests live. It returns the test
files and a "catches" note per test. Commit: `Add failing tests: <behaviour>`
and note the commit id (the *red commit*).

**2. STUB — `implementer`** (only if the tests reference interfaces that don't
exist yet). Create the public signatures only — functions, types, ports,
routes — each throwing a "not implemented" error. No logic.

**3. Verify red (gate).** Run the suite → `.tdd/after-red/`, then

```bash
python3 <tdd-skill>/scripts/tdd_guard.py verify-red --before .tdd/before --after .tdd/after-red
```

- **VACUOUS** (a new test passes before implementation): if the stub contains
  logic, have the implementer strip it back to a stub; otherwise send the
  test back to `test_writer` to fix or delete — it's tautological, or the
  behaviour already exists (then it's kept as a regression test, explicitly).
- **WRONG REASON** (test can't load): the implementer adds the missing stub.
- **SKIPPED**: back to `test_writer`.
Repeat until the gate passes. Amend the red commit if tests changed.

**4. GREEN — `implementer`.** Delegate with: the red commit id, the failing
tests, the plan. It writes the simplest code that passes them, on the golden
path (modules, ports, local adapters), running the suite as it goes.

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
| test_writer can't read implementation | Hook blocks reading/searching implementation folders | Agent instructions |
| test_writer writes only tests | Hook blocks writes outside test files | Agent instructions |
| implementer never changes tests | Hook blocks writes/deletes of test files | Agent instructions |
| Tests unchanged during green | `verify-green` git check | `verify-green` git check |
| No vacuous/tautological tests | `verify-red` gate + rules + readability review | same |

Folders treated as tests, implementation and public interface can be tuned
per project in `.tdd-boundary.json` (see the script's header).
