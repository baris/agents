# AGENTS.md

These rules define the default operating procedure for coding agents in this workspace. Follow them exactly unless a project explicitly overrides them.

## Documentation First
- At project start, create a `docs/` directory containing:
  - `docs/ARCHITECTURE.md`
  - `docs/TODO.md`
  - `docs/decisions/` for ADRs
- Optional: `docs/DATA-SCHEMAS.md` or other docs as needed
- The only documentation file allowed at repo root is `README.md`.

## Architecture Is the Source of Truth
- Always read and update `docs/ARCHITECTURE.md` before writing code.
- Architecture must reflect both current implementation and the intended clean end state.
- Start with an MVP architecture, then iterate.
- Each concern lives in its own module with clear boundaries.
- Any architectural change must be reflected immediately.
- No architectural drift.

## Decision Records (ADRs)
- Record significant design/architecture choices in `docs/decisions/`.
- Format: context -> decision -> alternatives -> consequences.
- Accepted decisions are immutable; changes require a new ADR.

## Planning Discipline
- Organize by date-based sections.
- Any committed change must appear in the relevant documents.
- Remove implemented sections after completion and architecture updates.

## TODO Execution Queue
- `docs/TODO.md` is the active task list.
- Update it at the start and end of every feature or bugfix.
- Mark completed items as `DONE` with date/time.

## Definition of Done (Mandatory)
A task is complete only when all of the following are true:
- Unit tests (and integration tests when applicable) exist and pass.
- `docs/ARCHITECTURE.md` and `docs/TODO.md` are updated.
- New failure modes have explicit error handling and logging.
- Data format/schema changes include versioning and migration notes.
- Example usage, CLI help, and README updates are included when relevant.

## Git Usage
- Bugfix commits: `bugfix: <single-line message>`
- Feature commits: `feat: <single-line message>`
- Commits must be narrowly scoped; no drive-by refactors.
- Formatting-only/mechanical changes must be isolated.
- If you cannot run git commands, provide the exact commands to run.

## Testing Strategy (TDD)
- Write tests first.
- Unit tests live in `tests/`.
- Integration tests live in `tests/integration/` when applicable.
- Run all relevant tests after each major change.
- No feature is complete without core-logic test coverage.

## External API Usage
- Use external APIs efficiently (cache, batch, limit).
- Paid APIs require explicit frugality strategies.
- All external calls must be behind a clear interface.
- Timeouts, retries, and failure handling are mandatory.
- Never call external APIs directly from core logic.

## Data Contracts & Versioning
- Persisted data must include:
  - `schema_version`
  - `generator_version` (git SHA or semantic version)
  - parameters used to generate the data
- Schemas must be documented and versioned.
- Schema changes require a migration strategy and tests.
- Never silently change file formats.

## Performance & Cost Budgets
- Cache expensive operations by default.
- Analysis loops must expose explicit budget controls (depth, time, samples).
- Document before/after impact for runtime or cost changes.
- Defaults should favor determinism and repeatability.

## Observability & Reliability
- Use structured logging (no `print` statements).
- Log at appropriate levels (debug/info/warn/error).
- Pipelines should be idempotent where possible.
- Be explicit about fail-fast vs continue-on-error.
- Seed randomness unless non-determinism is required.

## Virtual Environments
- Isolate dependencies:
  - Python: `venv`
  - Node: `nvm`
  - Go: go workspace
  - Rust: `cargo`
- Do not install dependencies globally without approval.

## Tooling & Code Quality
- Use standard formatting, linting, and typing tools for the language.
- Do not add tools that will not be enforced.
- Code should be readable, explicit, and boring.
- Avoid cleverness unless justified and documented.

## Guardrails (Hard Constraints)
- Do not refactor unrelated code during a feature.
- Do not change public interfaces without documentation and migration notes.
- Do not introduce heavy dependencies without justification.
- Do not modify data schemas silently.
- Do not optimize prematurely; measure first.

## User Context (Always Assume)
- The user is an experienced professional engineer with extensive coding experience.
- The user has experience developing operating systems, user-level applications, distributed systems, web serving systems, and reliability systems.
- The user is a former OSS developer and former Linux distribution developer.
- The user has managed engineering teams since 2014 and has been in the industry since 1999.
- The user codes in C++, C, Python, Go, and Bash.
- The user prefers concise, high-signal responses without basic explanations.
- The user expects production-grade rigor, explicit tradeoffs, and test-driven changes.
