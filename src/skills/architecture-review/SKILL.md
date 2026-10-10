---
name: architecture-review
description: Review code against enterprise standards, architecture and tech stack and return a PASS / CHANGES_REQUIRED / BLOCKED verdict with findings sorted into fix now, record for production and business facts needed. Use as the mandatory final step of every implementation task (task mode), before a commit or PR, or when asked to check alignment or production readiness.
---

# Architecture review

Check that what was built is aligned with the enterprise standards and stays
easy to productionize. The report is for the **main agent and the
engineering team**, not the builder: the main agent fixes the "fix now"
items itself, sends the "record for production" items to the production
handoff, and only asks the builder a plain business question if one is
genuinely needed.

{{#claude}}
The mandatory review at the end of every task is always done by the
`architecture_reviewer` subagent (task mode), never by the main agent itself.
For other reviews larger than a handful of files, delegate to it too so the
exploration stays out of the main conversation.
{{/claude}}
{{#codex}}
The mandatory review at the end of every task is always done by the
`architecture_reviewer` agent (task mode), never by the main agent itself —
spawn it and wait. For other reviews larger than a handful of files, spawn it
too so the exploration stays off the main thread.
{{/codex}}

## 1. Establish scope

- **Task mode** (the mandatory last step of every task): you're given the
  task's base commit. Review exactly `git diff <base>..HEAD` — the task's
  changes — plus the immediate code they touch, and end with a verdict line.
  Keep it focused: this runs after every task.
- Otherwise, the current branch vs its base — `git diff --stat <base>...HEAD`
  then `git diff <base>...HEAD` (try `origin/main`, `main`, `master`); if
  nothing is committed yet, `git diff HEAD`. No git: the working tree.
- Read `docs/production-handoff.md` (business context, derived requirements,
  ports) and the design brief — they define what "aligned" means for this
  project (e.g. Restricted data raises the bar).

## 2. Load only the standards you need

From the `enterprise-standards` skill references:

| Change touches… | Read |
| --- | --- |
| Any dependency manifest | run the `stack-check` skill's script with `--since <base>` |
| Structure, modules, infrastructure access | `patterns.md` PAT-01–04, PAT-19, PAT-20 |
| HTTP APIs, events, external systems | `patterns.md` PAT-05–09 |
| Auth, secrets, permissions | `patterns.md` PAT-10–12, non-negotiables in `principles.md` |
| Logging, health, retries, config, deploy, migrations | `patterns.md` PAT-13–18 |
| Tests, lint, repo layout, error handling | `coding-standards.md` |
| Data stores, personal data, availability | `nfr.md` |

## 3. Check

Confirm every finding in the code and cite `file:line` and the standard ID.

- **Non-negotiables** — secrets in code or config, real personal data in
  seed/test data, unauthenticated routes, unapproved package sources (NN-*).
- **Swappable infrastructure (PAT-19)** — does any business or use-case code
  import a database driver, HTTP client, SDK or framework type directly? Is
  every infrastructure need behind a port with a local adapter and a
  production adapter or fail-fast stub? Is adapter selection config-only, in
  one composition file? Do functional tests exist for the new behaviour, and do they call only modules' public interfaces and the test app factory (no imports of internal code)? Is each module's public interface free of logic and of re-exported internal types?
- **Modules (PAT-20)** — organized by business capability? Any module
  reaching into another's internals or tables? Business rules leaking into
  routes, UI or adapters?
- **Stack** — hold/retire/unassessed technologies; `local` packages used
  outside local adapters or tests.
- **APIs and events** — spec present and current, versioned, problem-details
  errors, idempotent consumers (PAT-05–07).
- **Security** — authorization on every route/use case, roles from the
  derived access model (PAT-10–12).
- **Operability** — structured logs without personal data, correlation IDs,
  health endpoints, timeouts, externalized config (PAT-13–16).
- **Data** — migrations versioned and shared by both persistence adapters;
  classification and retention match the handoff (PAT-18, NFR-04, NFR-08).
- **Hygiene** — tests for new use cases, one-command local run still works,
  README current (CS-01–03).
- **Handoff accuracy** — does §5 (ports) and §8 (gaps) of the production
  handoff match the code? Mismatches are "record for production" items.
- **Existing ADRs** — a deviation with an ADR is not a finding; cite the ADR.

## 4. Sort every finding

| Bucket | What goes here | Who acts |
| --- | --- | --- |
| **Fix now** | Anything the main agent can fix safely without business input: direct infrastructure imports, missing port/stub, misplaced business rule, missing auth check, unapproved package with an approved swap, missing test, leaked secret | Main agent, without asking the builder |
| **Record for production** | Needs enterprise access, platform work or a larger effort: production adapters needing credentials, CI/registry setup, security review, load testing, tier-driven ops work | `handoff_scribe` → handoff §8 with owner and effort |
| **Business fact needed** | A decision that depends on something only the builder knows | Main agent asks one plain question from `business-context` |
| **Exception** | Off-standard choice a business need requires | `write-adr` + handoff §7 |

Non-negotiable breaches always go in **Fix now**, at the top.

## 5. Report

```markdown
## Architecture review — <scope>

**Verdict:** <Aligned | Aligned after fixes | Production gaps recorded | Non-negotiable breached>

### Fix now (main agent)
1. **PAT-19 — use case imports `pg` directly** `src/modules/leave-requests/application/approve.ts:3` — move query into the persistence adapter; use `LeaveRequestRepository` port.

### Record for production (handoff §8)
| Gap | Standard | Where | Owner | Effort |
| --- | --- | --- | --- | --- |

### Business fact needed
- <plain-language question with options and default> — or "none"

### Exceptions
- <decision, standard affected, ADR needed> — or "none"

### Aligned
- <notable things done right, with IDs>

### Builder summary
<one plain sentence the main agent can relay, or "nothing to tell the builder">
```

Keep findings to one or two lines each; group repeats. Don't make the fixes
yourself in this skill — the main agent does.

## 6. Verdict (always the last line)

End every report with exactly one of:

```
VERDICT: PASS
VERDICT: CHANGES_REQUIRED
VERDICT: BLOCKED
```

- **PASS** — no *fix now* items and no non-negotiable breach. *Record for
  production* items, open business facts and exceptions with an ADR don't
  block a pass.
- **CHANGES_REQUIRED** — at least one *fix now* item: the task isn't aligned
  with the enterprise standards, architecture or tech stack yet (e.g. a hold
  or unassessed package with an approved replacement, infrastructure imported
  into business code, logic in a public interface file, a missing
  authorization check, a module reaching into another's internals).
- **BLOCKED** — a non-negotiable (`NN-*`) is breached. It's listed first under
  *Fix now*.

Be decisive and consistent: the same finding gets the same verdict every
time, and a re-review after fixes only checks the new changes plus whether the
previous *fix now* items were resolved.
