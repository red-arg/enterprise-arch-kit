---
name: stack-check
description: Check whether a technology, library or dependency is on the approved enterprise tech stack. Use before adding a dependency, when asked whether X can be used, when reviewing package.json/requirements/pom/go.mod changes, or to audit a repo's dependencies.
---

# Stack check

Classify technologies and dependencies against the approved stack and pick
the compliant option yourself. Statuses and their meaning are defined in
the `enterprise-standards` skill (adopt / trial / local / hold / retire /
unassessed). The builder is not technical: never hand them a library choice.

## A. Single question ("can we use X?")

1. Look X up in `../enterprise-standards/references/stack.json`
   (`technologies` for languages, frameworks, databases and platforms;
   `packages` for libraries — names support `*` wildcards).
2. Answer in this shape:

   ```
   X — <STATUS> (<STK-id or ecosystem>)
   Decision: <use X | use <adopt alternative> instead | X only in local adapters/tests>
   Record: <nothing | trial owner needed (handoff §8) | exception ADR (write-adr)>
   ```

3. If X is unlisted, it's UNASSESSED: use the closest `adopt` option. Only if
   nothing approved meets the business need, use X behind a port (PAT-19) and
   record an exception ADR. Don't guess a status.
4. If the *builder* asked for X by name, tell them in one plain sentence what
   you used and that it gives them the same result — no status names or IDs.

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

Then report (to the main agent, not the builder):

1. **Swap now** — RETIRE (any) and new HOLD packages, plus significant
   UNASSESSED ones (frameworks, DB drivers, SDKs) that have an approved
   replacement: package → replacement, and where it's imported.
2. **Local only** — `local` packages imported outside local adapters or tests.
3. **Record for production** — existing HOLD usage, TRIAL packages (need an
   engineering owner), UNASSESSED packages with no approved replacement
   (exception ADR). These go to the production handoff.

Group trivial unassessed packages (type stubs, tiny utilities) in one line.
Keep it short: actions, not the full dependency table.

## C. While writing code

Before adding any dependency yourself, check it here first. If it isn't
`adopt` or `trial` (or `local` for a local adapter/test), use an approved
alternative. Don't mention it to the builder unless they asked for the
original by name.
