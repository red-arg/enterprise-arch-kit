---
name: stack-check
description: Check whether a technology, library or dependency is on the approved enterprise tech stack. Use before adding a dependency, when asked "can I use X?", when reviewing package.json/requirements/pom/go.mod changes, or to audit a repo's dependencies.
---

# Stack check

Classify technologies and dependencies against the approved stack and steer
the developer to compliant choices. Statuses and their meaning are defined in
the `enterprise-standards` skill (adopt / trial / hold / retire / unassessed).

## A. Single question ("can I use X?")

1. Look X up in `../enterprise-standards/references/stack.json`
   (`technologies` for languages, frameworks, databases and platforms;
   `packages` for libraries — names support `*` wildcards).
2. Answer in this shape:

   ```
   X — <STATUS> (<STK-id or ecosystem>)
   <one sentence on what the status means for this request>
   Use instead: <adopt alternative>, if the status is hold/retire/unassessed
   Next step: <none | note owner in PR | write an ADR (write-adr skill)>
   ```

3. If X is unlisted, say it's UNASSESSED, suggest the closest `adopt` option,
   and offer an ADR so the architecture team can rule on it. Don't guess a status.

## B. Repository audit

Run the bundled checker from the repository root. The script lives in this
skill's `scripts/` folder and uses only the Python standard library:

```bash
python3 <this-skill-dir>/scripts/check_stack.py . --since origin/main
```

- Drop `--since` if there's no git history or base branch; then every
  dependency is treated as existing.
- `--json` gives machine-readable output; `--strict` exits non-zero on
  retire dependencies or new hold dependencies (useful in CI).
- It reads package.json, requirements*.txt, pyproject.toml, go.mod, pom.xml,
  build.gradle(.kts) and *.csproj.

Then report:

1. **Must address** — RETIRE (any), HOLD that is new. Give the adopt alternative for each.
2. **Needs a decision** — UNASSESSED packages. Group trivial ones (type stubs,
   small utilities) and call out significant ones (frameworks, DB drivers,
   SDKs for external services). Suggest an ADR for the significant ones.
3. **Note** — TRIAL packages (should have an owner named in the PR/README),
   existing HOLD usage (fine to keep, don't expand).

Keep the report short; the developer wants the list of actions, not the
full dependency table.

## C. While writing code

Before adding any dependency yourself, check it here first. If it isn't
`adopt` or `trial`, choose an approved alternative and tell the developer in
one line which one and why.
