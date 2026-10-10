# Test-writing rules — functional tests, written as unit tests

> For the `test_writer` agent. Tests are written **before** the behaviour
> exists and are **functional**: each one checks a business requirement —
> an acceptance scenario, a business rule or a functional edge case. They are
> written in the form of **unit tests**: in-process, with the project's
> standard unit test framework (Vitest, pytest, JUnit), fast and
> deterministic. No browser, no Playwright, no running server, no HTTP.
>
> They call only each business capability's **public interface** — the
> small, business-named set of operations a module exposes — through the
> **test app factory**. Everything behind that interface (domain classes,
> use-case internals, repositories, adapters, database) is invisible to the
> tests, so it can be refactored onto enterprise standards and the same tests
> prove the business behaviour is unchanged.
> TODO(engineering): add your naming and folder conventions per golden path.

## Only functional tests

Every test answers: *"Does the system do what the business asked?"*

| Write | Don't write (engineering adds these later, if at all) |
| --- | --- |
| Acceptance scenarios from the spec | Tests of individual classes, functions or components behind the public interface |
| Business rules and their functional edge cases | Tests of ports, adapters, repositories, queries or the database |
| Business errors and refusals the user would see | Tests through HTTP, a browser or a UI (no Playwright, no Selenium, no HTTP clients) |
| Permissions as the business defines them (who may do what) | Mocks or spies of internal parts |
| Behaviour across operations (submit → approve → balance) | Architecture, performance, load or security-scan tests |

## The boundary — your only way in

- **Module public interfaces.** Each business capability exposes its
  operations, input/output types and business errors in its public interface
  file (e.g. `src/modules/<capability>/index.ts`, `.../__init__.py`, or the
  module's `public/` package). Call only what's declared there.
- **The test app factory** (path given in the plan, e.g.
  `src/app/test-app.ts`) builds the application in memory with the local
  profile: in-memory storage, fake outside systems with sample data, and the
  documented **test controls** (e.g. a fixed clock, which business user is
  acting). Every test gets a fresh app from the factory.
- **Arrange through operations**, not storage: create an employee with the
  module's "add employee" operation, then submit the request. Never insert
  data directly or construct internal objects.
- **Act as business users** the way the plan defines (e.g.
  `app.as("manager")` or an `actor` argument).
- **Control time and outside systems only through factory options** the
  plan documents. If a rule depends on time or an outside system and no
  control exists, report it — don't reach inside.

## What you may look at

- The spec: user stories, acceptance scenarios, requirements, edge cases,
  Business Context.
- The plan: *Acceptance Examples* (hand-worked values) and *Functional Test
  Boundary* (public interfaces, factory, test controls).
- The modules' **public interface files** and the **test app factory**.
- `contracts/`, `data-model.md` as a description of business concepts.
- Existing tests under `test/functional/`.
- **Nothing else in the source folders.** If the public interface doesn't
  tell you enough to write a test, it's incomplete — report what's missing.

## Functional edge cases — work through this list for every rule

| Category | Examples to consider |
| --- | --- |
| Boundaries | exactly at a limit, one below, one above; zero; maximum length |
| Missing or invalid input | required value empty, wrong format, negative numbers, dates in the past |
| Permissions | each role allowed/forbidden; acting on someone else's record |
| State transitions | actions not allowed in the current state (approve an already-approved request; edit after submission) |
| Duplicates and repeats | submitting the same thing twice; retrying after a failure (idempotency the business expects) |
| Not found | referring to something that doesn't exist or was deleted |
| Empty and many | no records yet; one; several, with ordering and totals |
| Time and calendar | end of day/month/year, weekends and holidays if the rule cares, the business's time zone |
| Concurrency as the business sees it | two people acting on the same item; the second gets a clear outcome |
| Outside systems | the other system has no data or is unavailable — what the user should see |

Write the edge cases the spec or business context makes meaningful; each
cites the rule it protects. If the spec is silent on an important one, list
it as a business question rather than inventing the answer.

## Every test must be able to fail

Each test names a plausible wrong behaviour it would catch:

```ts
// US2-AS3 · Catches: a manager approving their own leave request
test("a manager cannot approve their own request", ...)
```

If you can't name a realistic wrong behaviour the business would care
about, delete the test.

## Tautologies — never write these

| Tautology | Example | Why it's worthless |
| --- | --- | --- |
| **Asserting what you just passed in** | submit `days: 3`, assert the result's `days` is 3, nothing else | Proves values are copied, not that a rule ran. Assert the business outcome (status `pending`, remaining balance `12`). |
| **Same-logic oracle** | `expect(balance).toBe(start - requested)` | Re-implements the rule; wrong in the same way the code is. Use the hand-worked literal: `toBe(12)`. |
| **Always-true assertions** | only `toBeDefined()`, `is not None`, `assertTrue(true)` | Pass for almost any wrong result. Assert the exact business values. |
| **Catch-all errors** | `toThrow()` with no type, `pytest.raises(Exception)` | Passes on the "not implemented" stub. Assert the specific business error and its user-facing message. |
| **Asserting a mock** | stub something to return X, assert X comes back | Tests the stub. Don't mock — use the factory's in-memory app. |
| **Interaction-only checks** | assert an internal method was called | Pins *how*, not *what*. Assert the outcome visible through the public interface (or a notification captured by the factory's fake outside system). |
| **Snapshot of everything** | snapshot a whole result object | Approves whatever exists first. Assert the fields that matter. |
| **Conditional or looping assertions** | `if (result) expect(...)`; asserting inside a loop over the result itself | Can silently assert nothing. |

## How to write them

- **Literal oracles** from the spec's examples or the plan's acceptance
  examples — never computed in the test.
- **One business behaviour per test**, Arrange–Act–Assert, named as the
  business would say it: `"<role> can/cannot <action> when <condition>"`,
  prefixed with the scenario ID.
- **Independent**: a fresh app from the factory per test; no shared state,
  no dependence on order.
- **Deterministic**: fixed clock via the factory; no real network, files or
  external systems; no sleeps.
- **Invented, realistic data** — never real or production data (NN-02).

## Self-check before handing over

For every test, answer yes to all:

1. Does it trace to a scenario, rule or edge case in the spec (cite it)?
2. Does it use only the public interfaces, the test app factory and documented
   test controls?
3. Would it fail for the wrong behaviour named in its "Catches" note?
4. Would it still pass if everything behind the public interface were
   restructured, with the same business behaviour?
5. Are expected values literals or hand-worked examples, not recomputed?
6. Does it avoid every tautology above?

## The vacuous-test gate (automatic)

After your tests are written, the implementer adds any missing operations to
the public interfaces as stubs that throw "not implemented", and the suite is
run. **Every new test must fail, and fail on an assertion or a business
expectation** — not because a test file couldn't load. A new test that
passes against the stubs (a catch-all error check, for example) is vacuous
and comes back to you, unless the behaviour already exists (then keep it as a
regression test and say so).
