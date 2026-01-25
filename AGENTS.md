# AGENTS.md

These rules define the default operating procedure for coding agents in this workspace. Follow them exactly unless a project explicitly overrides them.

## Documentation First
- At project start, create a `docs/` directory containing:
  - `docs/ARCHITECTURE.md`
  - `docs/TODO.md`
  - `docs/decisions/` for ADRs
- Optional: `docs/DATA-SCHEMAS.md` or other docs as needed
- The only documentation file allowed at repo root is `README.md`.

## Prototype Mode (Explicit Opt-In)
- When the user explicitly requests a prototype or spike:
  - Skip `docs/` scaffolding and ADRs.
  - Minimize tests to sanity checks only.
  - Prefix all created files/directories with `prototype_` or place in `_prototype/`.
  - At prototype end, the user decides: discard, or promote to production (which triggers full documentation and test requirements).
- Prototype mode must be explicitly requested; never assume it.

## Architecture Is the Source of Truth
- Always read and update `docs/ARCHITECTURE.md` before writing code.
- Architecture must reflect both current implementation and the intended clean end state.
- Start with an MVP architecture, then iterate.
- Each concern lives in its own module with clear boundaries.
- Any architectural change must be reflected immediately.
- No architectural drift.
- For a new project, do not touch code until the user explicitly confirms the architecture is ready.
- If architecture changes are needed after coding has started, stop and request explicit user confirmation before proceeding.

## Existing Codebase Handling
- If `docs/ARCHITECTURE.md` does not exist:
  - For small tasks (bug fixes, minor changes): proceed without it, but note its absence.
  - For significant work: ask the user whether to create it first or proceed without.
- If existing architecture docs are outdated or contradict the code:
  - Flag the discrepancy explicitly.
  - Ask whether to update docs to match code, refactor code to match docs, or proceed as-is.
- Never silently ignore architectural contradictions.

## Decision Records (ADRs)
- Record significant design/architecture choices in `docs/decisions/`.
- Format: context -> decision -> alternatives -> consequences.
- Accepted decisions are immutable; changes require a new ADR.

## Planning & TODO Management
- `docs/TODO.md` is the active task list, organized by priority.
- Update it at the start and end of every feature or bugfix.
- Completed items are removed or moved to a `## Completed` section with date stamps.
- ADRs in `docs/decisions/` use date-prefixed filenames: `YYYY-MM-DD-<slug>.md`.
- Any committed change must be reflected in the relevant docs before the task is complete.
- Keep planning docs current; stale docs are worse than no docs.

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

## Testing Strategy
- Tests must exist and pass before a task is considered complete.
- Prefer test-first when feasible, but the hard constraint is coverage at completion, not test-first process.
- Unit tests live in `tests/`.
- Integration tests live in `tests/integration/` when applicable.
- Run all relevant tests after each significant change.
- No feature is complete without core-logic test coverage.
- When modifying existing code, ensure existing tests still pass before adding new ones.

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

## Dependency Isolation
- Always isolate project dependencies:
  - Python: `venv` or `uv`
  - Node: project-local `node_modules` with lockfile (`package-lock.json` or `pnpm-lock.yaml`)
  - Go: go modules (`go.mod`)
  - Rust: `cargo` (workspace-level `Cargo.lock`)
- Do not install dependencies globally without explicit approval.
- Commit lockfiles; they are source of truth for reproducible builds.

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

## Ambiguity and Conflict Resolution
- When instructions conflict or are ambiguous:
  - Explicit user instructions override these defaults.
  - Ask for clarification before proceeding if the ambiguity affects correctness or architecture.
  - For low-risk ambiguity, state your assumption and proceed.
- When in doubt between action and inaction:
  - For destructive or irreversible operations: ask first.
  - For additive or easily-reversible operations: proceed, but explain what you did.
- If you encounter a situation these rules don't cover, apply the principle: "minimize surprise, maximize reversibility."

## User Context (Always Assume)
- The user is an experienced professional engineer with extensive coding experience.
- The user has experience developing operating systems, user-level applications, distributed systems, web serving systems, and reliability systems.
- The user is a former OSS developer and former Linux distribution developer.
- The user has managed engineering teams since 2014 and has been in the industry since 1999.
- The user codes in C++, C, Python, Go, and Bash.
- The user prefers concise, high-signal responses without basic explanations.
- The user expects production-grade rigor, explicit tradeoffs, and test-driven changes.
