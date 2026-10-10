# Test-writing rules

> For the `test_writer` agent. Tests are written **before** the behaviour
> exists, from the specification and the public interface — never from the
> implementation. A good test is a precise, executable statement of a
> business rule that a plausible wrong implementation would fail.
> TODO(engineering): add language-specific conventions (naming, folders,
> runner) for your golden paths.

## What to test (sources, in priority order)

1. **Acceptance scenarios** from the spec (Given/When/Then), one or more
   tests each, named after the scenario (e.g. `US1-AS2`).
2. **Business rules and edge cases** in the requirements: limits, states,
   permissions, invalid inputs, empty results, duplicates, time boundaries.
3. **Contracts:** for each port in the plan (PAT-19), a contract test suite
   that any adapter must pass — run against the local adapter now and the
   production adapter later. For each external API in `contracts/`, request
   and response behaviour at the HTTP boundary.
4. **Error behaviour** the user would notice: validation messages, refusal
   of unauthorized actions, problem-details responses (CS-04).

## What you may look at

- The spec, plan, `data-model.md`, `contracts/`, `quickstart.md`.
- Public interfaces: module public entry points (`index.*`), `ports/`,
  OpenAPI specs, existing tests.
- **Not** implementation: `domain/`, `application/`, `adapters/`,
  `infrastructure/`, `api/` route handlers, migrations. If you can't write a
  test without knowing how something is built, the interface is unclear —
  report that instead of looking.

## Every test must be able to fail

Each test must fail for at least one **plausible wrong implementation**. Put
that in the test as a one-line comment or in its name:

```ts
// Catches: approving a request that exceeds the remaining balance
it("rejects a 5-day request when only 3 days remain", ...)
```

If you can't name a realistic bug the test would catch, delete the test.

## Tautologies — never write these

| Tautology | Example | Why it's worthless |
| --- | --- | --- |
| **Asserting the mock** | stub `repo.find()` to return X, call `service.get()`, assert X | Tests the stub, not the behaviour; passes for any implementation that forwards the call. |
| **Same-logic oracle** | `expect(total).toBe(items.reduce((s,i)=>s+i.price*i.qty,0))` | Re-implements the code under test; wrong in the same way the code is. Use a hand-worked number: `toBe(42.50)`. |
| **Echo tests** | set a field, assert the getter returns it; construct an object, assert its fields | Tests the language, not a business rule. |
| **Always-true assertions** | `expect(result).toBeDefined()`, `assert x is not None` as the only check, `assertTrue(true)` | Passes for almost any wrong result. Assert the specific expected value. |
| **Interaction-only tests** | assert `repo.save` was called once with `any()` | Pins *how* not *what*. Assert the observable outcome (the request can now be found with status `approved`). Only assert an interaction when the interaction *is* the behaviour (an email is sent) — and then check it through the port's fake, with the meaningful content. |
| **Snapshot of everything** | snapshot a whole response or component with no specific assertion | Approves whatever the code produces first. Assert the fields that matter. |
| **Testing the framework** | assert that the HTTP library returns 404 for unknown routes, that the ORM saves | Not our behaviour. |
| **Conditional or looping assertions** | `if (result) expect(...)`, assertions in a loop over the result itself | Can silently assert nothing. |
| **Catch-all exceptions** | `expect(() => f()).toThrow()` with no type or message | Passes on any crash, including the not-implemented stub. Assert the specific error and message. |

## How to write them

- **Concrete examples as oracles.** Use the spec's examples or hand-worked
  values. Inputs and expected outputs are literals, not computed.
- **Test through the public interface**, at the level the business sees:
  module entry points, ports, HTTP contracts. Never private functions.
- **Prefer real local adapters over mocks.** The local adapters (embedded
  database, in-process bus, fake external systems) are real implementations
  of the ports — use them via the normal wiring. Use a hand-written fake
  only for things you must control (clock, IDs, external failures).
- **Assert outcomes**: return values, state visible through public queries,
  events/notifications captured by a port's fake, HTTP status and body.
- **Deterministic**: inject time, IDs and randomness; no real network; no
  sleeps; no dependence on test order.
- **One behaviour per test**, Arrange–Act–Assert, readable as documentation:
  `"<does what> when <condition>"`.
- **Specific failures**: assert the exact error type/code and the
  user-visible message from the spec.
- **No test data copied from production**; use invented, realistic data (NN-02).

## Self-check before handing over

For every test, answer yes to all:

1. Does it trace to a scenario, rule, contract or error case (cite it)?
2. Would it fail for the bug named in its "Catches" note?
3. Would it still pass after a correct refactor of the implementation?
4. Is the expected value a literal or hand-worked example, not recomputed?
5. Does it avoid every tautology in the table above?

## The vacuous-test gate (automatic)

After your tests are written, the implementer creates stubs (signatures that
throw "not implemented"), and the suite is run. **Every new test must fail.**
A new test that passes against a stub, or against the existing code before
the change, is vacuous or tautological and comes back to you to fix or
remove — unless you can show the behaviour already exists, in which case
keep it as a regression test and say so.
