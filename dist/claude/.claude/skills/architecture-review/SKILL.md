---
name: architecture-review
description: Review code, a branch, a PR or a design against enterprise architecture standards and report aligned items, deviations needing an ADR, and recommendations. Use when asked to review architecture, check alignment or compliance, or before merging or shipping a feature.
---

# Architecture review

Review a change against the enterprise standards and tell the developer, in
plain language, what to fix, what needs an ADR and what is fine. You are a
guide, not a gate: explain the *why* behind each finding and always offer the
compliant alternative.

For anything larger than a handful of files, delegate the review to the
`architecture_reviewer` subagent so the exploration stays out of the main
conversation, then relay its report.

## 1. Establish scope

- Default scope is the current branch vs its base: `git diff --stat <base>...HEAD`
  then `git diff <base>...HEAD`. Try `origin/main`, then `main`, then `master`.
- If the developer named files, a PR or a design doc, review that instead.
- If there's no git history, review the working tree.
- Note what kind of change it is (new service, new endpoint, new dependency,
  data model change, UI, infra) — it decides which checks matter.

## 2. Load only the standards you need

From the `enterprise-standards` skill references:

| Change touches… | Read |
| --- | --- |
| Any dependency manifest | run the `stack-check` skill's script with `--since <base>` |
| New service, module boundaries, data ownership | `principles.md`, `patterns.md` PAT-01–04 |
| HTTP APIs, events, external vendors | `patterns.md` PAT-05–09 |
| Auth, secrets, permissions | `patterns.md` PAT-10–12, non-negotiables in `principles.md` |
| Logging, health, retries, config, deploy, migrations | `patterns.md` PAT-13–18 |
| Tests, lint, repo layout, error handling | `coding-standards.md` |
| Data stores, PII, SLAs | `nfr.md` |

## 3. Check

Work through the relevant items. Confirm each finding by reading the actual
code — cite `file:line`. Don't report something you haven't seen.

- **Boundaries** — does the change reach into another service's data or
  share domain models across services? (PAT-03, PAT-04)
- **Layering** — is business logic tangled with HTTP/DB/framework code? (PAT-01)
- **Stack** — any hold/retire/unassessed technologies or packages? (STK, CS-06)
- **APIs and events** — spec present and updated, versioned, errors as problem
  details, consumers idempotent? (PAT-05–07)
- **Security** — hard-coded secrets, unauthenticated endpoints, missing
  authorization checks, custom auth? (NN-01, NN-03, PAT-10–12) Treat any
  non-negotiable breach as the top finding.
- **Operability** — structured logs without PII, tracing, health endpoints,
  timeouts on outbound calls, config externalized? (PAT-13–16)
- **Data** — migrations backward compatible, classification and retention
  considered? (PAT-18, NFR-04, NFR-08)
- **Hygiene** — tests for new logic, README/ADR updated, lint clean? (CS-01–03)
- **Existing ADRs** — check `docs/adr/` before flagging; a deviation that
  already has an accepted ADR is ALIGNED (cite the ADR).

## 4. Report

Use exactly this structure. Lead with the verdict. Omit empty sections.

```markdown
## Architecture review — <scope>

**Verdict:** <Aligned | Aligned with recommendations | Deviations need ADRs | Non-negotiable breached>
<one or two sentences: the most important thing to do next>

### Must fix (non-negotiables)
- **NN-01 — Secret committed** `src/config.ts:12` — <what and why>. **Fix:** <compliant alternative>.

### Deviations — fix or record an ADR
- **PAT-03 — Reads another service's tables** `orders/repo.py:40` — <why it matters>. **Option A (standard):** <…>. **Option B:** keep it and record an ADR (exception to PAT-03).

### Unassessed
- **<tech>** — not in the stack. Closest approved: <…>. Suggest an ADR if you keep it.

### Recommendations
- **PAT-15 — No timeout on payment client** `payments/client.go:88` — <…>.

### Aligned
- <short list of the notable things done right, with IDs>
```

Keep each finding to two or three lines. Group repeats ("missing timeouts in
4 clients: …") instead of listing each one.

## 5. Offer next steps

End with at most three concrete offers, e.g. "fix the two recommendations",
"draft ADR-000N for the MongoDB exception", "run the review again after fixes".
Don't make the fixes unless the developer asks.
