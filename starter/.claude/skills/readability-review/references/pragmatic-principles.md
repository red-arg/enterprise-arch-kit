# Readability principles — The Pragmatic Programmer

> Paraphrased from *The Pragmatic Programmer*, 20th Anniversary Edition
> (David Thomas & Andrew Hunt, 2019). This is a review checklist, not a
> substitute for the book — read the named topic for the full reasoning.
> TODO(architecture-team): add or drop rules to match your engineering culture.
> Keep IDs stable once published.

## The lens: ETC — Easier To Change

The book's core design value: good code is code that is easier to change.
Every finding in a readability review must answer *"how does this make the
code harder to understand or change?"* If you can't answer that, it isn't a
finding — it's a preference. *(Topic: The Essence of Good Design)*

## Rules

| ID | Principle | What to look for in code | Book topic |
| --- | --- | --- | --- |
| RD-01 | **DRY — one authoritative place for each piece of knowledge** | The same business rule, constant, validation or mapping expressed in several places; parallel `if/switch` chains that must change together; comments or docs that restate what the code says (they will drift). Not every textual similarity is duplication — two pieces of code that look alike but represent *different* knowledge may legitimately stay separate. | DRY — The Evils of Duplication |
| RD-02 | **Orthogonality — unrelated things stay independent** | Functions that do several unrelated jobs; a change in one feature forcing edits in unrelated modules; hidden side effects (a "get" that writes, a formatter that logs and mutates). | Orthogonality |
| RD-03 | **Tell, don't ask** | Code that pulls state out of an object, decides, then pushes it back, instead of asking the object to do the work. Logic about a thing living far from that thing. | Decoupling |
| RD-04 | **Don't chain method calls (Law of Demeter)** | Train wrecks like `order.getCustomer().getAccount().getAddress().getCity()` that couple the caller to a whole object graph. (Fluent APIs and pipelines over plain data are fine.) | Decoupling |
| RD-05 | **Avoid global and shared mutable data** | Module-level mutable state, singletons used as hidden parameters, functions whose result depends on something not passed in. | Decoupling |
| RD-06 | **Name well; rename when needed** | Names that describe type or mechanics instead of role (`data`, `list2`, `handle`, `doStuff`, `tmp`); misleading names after behaviour changed; inconsistent words for the same concept across the codebase (`client`/`customer`/`user`); unexplained abbreviations. Names should match the domain's vocabulary. | Naming Things |
| RD-07 | **Don't program by coincidence** | Code that works for reasons the author can't state: unexplained sleeps/retries, magic ordering, copied snippets with unused parts, reliance on undocumented behaviour, conditions that "fixed it" without a reason. | Programming by Coincidence |
| RD-08 | **Crash early — don't hide failure** | Swallowed exceptions, empty `catch`, returning `null`/defaults on impossible states, logging-and-continuing when the program can no longer be correct. | Dead Programs Tell No Lies |
| RD-09 | **Make assumptions explicit** | Preconditions only implied by comments; inputs validated deep inside instead of at the boundary; states that "can't happen" with no assertion. | Design by Contract; Assertive Programming |
| RD-10 | **Finish what you start** | Resources (files, connections, locks, subscriptions) acquired in one place and released somewhere else, or not on every path. Prefer scoped constructs (`with`, `using`, try-with-resources, `defer`). | How to Balance Resources |
| RD-11 | **Think in transformations** | Long procedures that mutate shared state step by step where a clear pipeline of small transformations (input → step → step → output) would show the flow. | Transforming Programming |
| RD-12 | **Don't pay inheritance tax** | Deep or wide inheritance used for code sharing; subclasses overriding to "turn off" behaviour. Prefer interfaces/protocols, delegation or composition. | Inheritance Tax |
| RD-13 | **Parameterize with external configuration** | Magic numbers and strings for things that vary by environment or business decision (URLs, limits, rates, feature switches) hard-coded in logic. Unnamed literals in logic generally. | Configuration |
| RD-14 | **Small steps, no speculative generality** | Abstractions, extension points, options or layers built "for later" with one caller; frameworks inside the app. Design for what is known now and keep it easy to change. | Don't Outrun Your Headlights; Good-Enough Software |
| RD-15 | **Testable code is readable code** | Logic that can't be tested without heavy setup is usually tangled. Missing tests for the new logic, or tests that don't read as examples of how to use the code. | Test to Code |
| RD-16 | **Don't live with broken windows** | Small rot left in or near the change: commented-out code, dead code, TODOs without owners, misleading comments, inconsistent formatting the formatter would fix. Flag it so it gets fixed now while it's cheap. | Software Entropy |

## Calibration — be pragmatic

- **Good enough is a feature.** Don't demand perfection on throwaway or
  prototype code; scale the bar to the code's lifespan and tier.
  *(Topic: Good-Enough Software)*
- **Refactor early, in small steps** — suggest changes that can be done
  safely now, with tests, rather than rewrites. *(Topic: Refactoring)*
- **Leave formatting to tools.** Don't report what a formatter or linter
  would fix automatically; recommend running it instead (CS-02).
