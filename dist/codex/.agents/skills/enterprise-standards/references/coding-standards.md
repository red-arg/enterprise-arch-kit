# Coding standards

> TODO(architecture-team): Illustrative defaults. Link to language-specific
> style guides and lint configs where you have them. Keep IDs stable.

| ID | Standard | Rule |
| --- | --- | --- |
| CS-01 | **Repository layout** | Each repo has `README.md` (purpose, how to run, how to test, owners), `docs/adr/`, `CODEOWNERS`, and a CI pipeline definition. Golden-path layouts are in the `scaffold-service` skill. |
| CS-02 | **Formatting and linting** | Use the standard formatter and linter for the language (see tech stack), run in CI, zero warnings on new code. |
| CS-03 | **Testing** | Unit tests for business logic, integration tests for adapters (DB, messaging, HTTP clients), contract tests for public APIs. TODO: set coverage threshold (e.g. 80% on new code). |
| CS-04 | **Error handling** | Don't swallow exceptions. Translate infrastructure errors at the boundary. Return problem-details responses for API errors (PAT-05). |
| CS-05 | **Logging** | Use the standard logging library, structured output, appropriate levels. Never log secrets, tokens or PII (PAT-13). |
| CS-06 | **Dependencies** | Only `adopt`/`trial` packages (see tech stack). Pin versions via lockfiles. Lockfiles are committed. Dependency and licence scanning runs in CI. |
| CS-07 | **Naming** | Language-idiomatic naming. Services and repos use `kebab-case` (`<domain>-<capability>-service`). |
| CS-08 | **Configuration and secrets** | No hard-coded URLs, credentials or environment-specific values (PAT-11, PAT-16). Provide `.env.example` with placeholder values only. |
| CS-09 | **Comments and docs** | Public APIs documented (OpenAPI, docstrings). Comments explain *why*, not *what*. Deviations reference their ADR. |
| CS-10 | **Generated and AI-assisted code** | Treat AI-generated code like any other contribution: it must pass review, tests and scans. Don't commit code you can't explain. |
| CS-11 | **Branching and commits** | Trunk-based with short-lived branches, PRs require review and green CI. TODO: commit message convention (e.g. Conventional Commits). |
