---
name: readability-review
description: Review implemented code for readability and ease of change using The Pragmatic Programmer principles (ETC, DRY, orthogonality, tell-don't-ask, naming, crash early). Use when asked to review code quality, readability, maintainability or clean code, or after a feature is implemented and before a commit or PR.
---

# Readability review

Review code the way a pragmatic senior colleague would: find the few things
that make it harder to read or change, explain why in a sentence, and give a
small, concrete improvement. The report is for the **main agent**, which
applies the fixes itself — the builder is not a software engineer and is
never asked to make code-quality decisions. The principles and their IDs (`RD-01`–`RD-16`)
are in `references/pragmatic-principles.md` — read it before reviewing.

{{#claude}}
For more than a handful of files, delegate to the `readability_reviewer`
subagent so the reading stays out of the main conversation, then relay its
report.
{{/claude}}
{{#codex}}
For more than a handful of files, spawn the `readability_reviewer` agent so
the reading stays off the main thread, wait for it, then relay its report.
{{/codex}}

## 1. Scope

- Default: the current branch vs its base — `git diff <base>...HEAD`
  (try `origin/main`, then `main`, then `master`); if nothing is committed
  yet, `git diff HEAD` for working-tree changes.
- If specific files or a folder were named, review those instead.
- Review the changed code and its immediate surroundings. Note broken
  windows *next to* the change (RD-16), but don't audit the whole repo.
- Gauge the bar: prototype or production? Tier and lifespan from the README
  if present. Be lighter on throwaway code.

## 2. Read for understanding first

Before judging, make sure you can explain what the change does in two
sentences. If you can't, that itself is the top finding (usually RD-06,
RD-02 or RD-07).

## 3. Check against the principles

Walk the RD rules. For each candidate finding, confirm it in the actual code
and apply the **ETC test**: say concretely how it makes the code harder to
understand or change. Drop anything that fails the test, anything a
formatter or linter would fix, and pure taste.

## 4. Report

Lead with the verdict. Cap at **the 7 most valuable findings**; group
repeats. Omit empty sections.

````markdown
## Readability review — <scope>

**Verdict:** <Clear and easy to change | Readable after small fixes | Hard to change — refactor before building more>

### Fix now (main agent applies, smallest safe steps, tests green between each)
1. **RD-01 DRY — discount rule in three places** `cart.ts:41`, `invoice.ts:88`, `email.ts:12`
   Changing the discount means finding all three; they've already drifted (`>=` vs `>`).
   **Do:** one `discountFor(order)` in the pricing module; call it from each.
   ```ts
   // before
   if (order.total >= 100) price *= 0.9
   // after
   price = applyDiscount(order, price)
   ```
2. **RD-06 Naming** `utils.py:15` `process(d)` → `normalize_address(raw_address)`.

### Record for production (larger refactors → handoff §8)
| Gap | Principle | Where | Effort |
| --- | --- | --- | --- |

### Broken windows nearby
- Commented-out block `api/handler.go:120–140`; unowned TODO `jobs/sync.py:9`.

### Done well
- <one to three specific things worth keeping, with RD IDs>

### Builder summary
<one plain sentence the main agent can relay, or "nothing to tell the builder">
````

Rules for findings:
- Cite `file:line` and the RD ID with its short name.
- One or two sentences of *why*, framed as ease of change or understanding.
- A concrete instruction the main agent can apply without asking anyone;
  include a short before/after snippet only when it makes the fix obvious
  (≤ 8 lines).
- **Fix now** = changes that are safe in one sitting with tests. Anything
  bigger (restructuring several modules) goes to **Record for production**.
- Order by value to the next person changing this code.

## 5. After the review

The main agent applies the "fix now" items, runs the tests, and re-runs the
review once. Record items go to `handoff_scribe`. Don't edit code yourself in
this skill.
