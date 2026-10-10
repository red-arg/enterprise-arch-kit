# Test-writing rules — functional, black-box, requirement-driven

> For the `test_writer` agent. Tests are written **before** the behaviour
> exists, from the business requirements, and exercise the **running
> system through its external interface only**. They must not know how the
> system is built — not its modules, classes, functions, ports, database or
> even its language — so the implementation can be refactored or re-platformed
> onto enterprise standards and the same tests prove nothing changed for the
> business.
> TODO(engineering): add your conventions for the functional test runner,
> folders and naming per golden path.

## Only functional tests

Every test answers: *"Does the system do what the business asked, as a user
or calling system would observe it?"*

| Write | Don't write (engineering adds these later, if at all) |
| --- | --- |
| Acceptance scenarios from the spec | Unit tests of functions, classes or components |
| Business rules and their functional edge cases | Tests of ports, adapters, repositories or the database |
| User-visible errors and refusals | Tests that call internal module entry points |
| Permissions as the business defines them (who may do what) | Mocks or spies of any internal part |
| Behaviour across steps (create → approve → report) | Architecture, layering, performance, load or security-scan tests |

## The external interface (your only way in)

| Deployable | Drive it through | Observe outcomes through |
| --- | --- | --- |
| API / back-end / full stack | HTTP requests defined in `contracts/` (OpenAPI) | HTTP responses: status, body fields, follow-up queries via the API |
| User interface (critical journeys only) | A real browser, by visible labels and roles (never CSS selectors or test IDs tied to markup) | What the user sees: text, lists, messages |
| Event worker | The input events defined in `contracts/` | Output events and state visible through the API |
| Scheduled job | Its documented run command and input files | Output files, messages and state visible through the API |

- Start the system the way `quickstart.md` says, with the **local profile**
  (embedded storage, dev login, fake external systems). The shared harness in
  `test/functional/support/` does this; extend it, don't bypass it.
- **Set up data through the external interface** (create a request via the
  API), or through the local profile's documented seed data. Never write to
  the database or call internal code to arrange a test.
- **Log in as business roles** using the local profile's dev login (e.g.
  "employee", "manager"), as documented in the plan.
- **Control time and outside systems only through documented test
  controls** of the local profile (e.g. a fixed-clock setting, a fake HR
  system's sample data). If a rule depends on time or an outside system and
  no control is documented, report it — don't reach inside.

## What you may look at

- The spec: user stories, acceptance scenarios, requirements, edge cases,
  Business Context.
- The plan's *Acceptance Examples* (hand-worked values) and test controls.
- `contracts/` / OpenAPI / AsyncAPI, `quickstart.md`, `data-model.md` as a
  description of business concepts (not storage).
- Existing functional tests and the harness under `test/functional/`.
- **Nothing under the source folders.** If the contract doesn't tell you
  enough to write a test, the contract is incomplete — report what's missing.

## Functional edge cases — work through this list for every rule

| Category | Examples to consider |
| --- | --- |
| Boundaries | exactly at a limit, one below, one above; zero; maximum length |
| Missing or invalid input | required field empty, wrong format, negative numbers, dates in the past |
| Permissions | each role allowed/forbidden; acting on someone else's record |
| State transitions | actions not allowed in the current state (approve an already-approved request; edit after submission) |
| Duplicates and repeats | submitting the same thing twice; retrying after a failure (idempotency the business expects) |
| Not found | referring to something that doesn't exist or was deleted |
| Empty and many | no records yet; one record; several records with ordering and totals |
| Time and calendar | end of day/month/year, weekends and holidays if the rule cares, time zones the business operates in |
| Concurrency as the business sees it | two people acting on the same item; the second sees a clear outcome |
| Outside systems | the other system has no data, or is unavailable — what the user should see |

Only write the edge cases the spec or business context makes meaningful;
each must still cite the rule it protects. If the spec is silent on an
important edge case, list it as a question rather than inventing the answer.

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
| **Asserting what you just sent** | POST a request with `days: 3`, assert the response echoes `days: 3`, nothing else | Proves the API echoes input, not that any rule ran. Assert the business outcome (status `pending`, remaining balance `12`). |
| **Same-logic oracle** | `expect(balance).toBe(start - requested)` | Re-implements the rule; wrong in the same way the code is. Use the hand-worked literal: `toBe(12)`. |
| **Always-true assertions** | only `status < 500`, only `body` is defined, `assert True` | Pass for almost any wrong behaviour. Assert the exact status, fields and message the spec requires. |
| **Status-only checks** | assert 200 and stop | A wrong body passes. Check the business fields that matter. |
| **Snapshot of everything** | snapshot a whole response or page | Approves whatever exists first. Assert the specific fields or visible text. |
| **Testing the framework** | unknown route returns 404, JSON is parsed | Not a business behaviour. |
| **Conditional or looping assertions** | `if (res.ok) expect(...)`; asserting inside a loop over the response itself | Can silently assert nothing. |
| **Catch-all failures** | expecting "any 4xx" or "some error" | Passes on the not-implemented stub. Assert the specific status and the user-facing message from the spec. |

## How to write them

- **Literal oracles** from the spec's examples or the plan's acceptance
  examples — never computed in the test.
- **One business behaviour per test**, Arrange–Act–Assert, named as the
  business would say it: `"<role> can/cannot <action> when <condition>"`,
  prefixed with the scenario ID.
- **Independent tests**: each creates its own data through the interface;
  no reliance on order or on other tests' data.
- **Deterministic**: fixed clock via the documented control; no real
  external systems; no sleeps — poll the interface for an eventual outcome
  with a short timeout if the spec says "eventually".
- **No real or production data** — invented, realistic values (NN-02).

## Self-check before handing over

For every test, answer yes to all:

1. Does it trace to a scenario, rule or edge case in the spec (cite it)?
2. Does it use only the external interface and documented test controls?
3. Would it fail for the wrong behaviour named in its "Catches" note?
4. Would it still pass if the whole implementation were rewritten — any
   language, any structure — with the same business behaviour?
5. Are expected values literals or hand-worked examples, not recomputed?
6. Does it avoid every tautology above?

## The vacuous-test gate (automatic)

After your tests are written, the implementer adds the operations from the
contract as stubs that answer "not implemented" (HTTP 501), and the suite is
run. **Every new test must fail, and fail on an assertion** — not because the
system couldn't start or the test couldn't load. A new test that passes
against the stubs is vacuous and comes back to you to fix or remove, unless
the behaviour already exists (then keep it as a regression test and say so).
