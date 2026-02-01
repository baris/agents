# AGENTS.md

These rules define the default operating procedure for coding agents in this workspace. Follow them exactly unless a project explicitly overrides them.

**Before making ANY code changes**: Run `scripts/context.sh` to understand project state, then read `docs/ARCHITECTURE.md`.

## Documentation First
- At project start, create a `docs/` directory containing:
  - `docs/ARCHITECTURE.md` (use template: `docs/templates/ARCHITECTURE.template.md`)
  - `docs/TODO.md` (use template: `docs/templates/TODO.template.md`)
  - `docs/decisions/` for ADRs (use template: `docs/templates/ADR.template.md`)
- Optional: `docs/DATA-SCHEMAS.md` or other docs as needed
- The only documentation file allowed at repo root is `README.md`.
- Templates define the expected format; follow them exactly.

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
A task is complete only when **ALL** of the following are verified:

**Code Quality**
- [ ] Unit tests exist and pass (minimum 80% coverage for core logic, 50% overall)
- [ ] Integration tests exist for cross-module interactions
- [ ] Error paths are explicitly tested
- [ ] Type checking passes (`mypy --strict` for Python, `tsc --strict` for TypeScript)
- [ ] Linting passes (`ruff` for Python, `eslint` for JS/TS)
- [ ] No secrets or API keys in code or config files

**Documentation**
- [ ] `docs/ARCHITECTURE.md` reflects current implementation
- [ ] `docs/TODO.md` is updated (task removed or marked complete)
- [ ] New public APIs have docstrings/JSDoc comments
- [ ] README updated if user-facing behavior changed

**Error Handling**
- [ ] New failure modes have explicit error handling
- [ ] Errors are logged with context (error type, relevant state, stack trace)
- [ ] User-facing operations show appropriate feedback on failure

**Data & Schema**
- [ ] Data format changes include `schema_version` bump
- [ ] Migration strategy documented for breaking changes

**Verification (agent must perform)**
- [ ] Run tests and show output
- [ ] Show `git diff` before committing
- [ ] For UI changes: take screenshot or describe visual result

## Git Usage
- Bugfix commits: `bugfix: <single-line message>`
- Feature commits: `feat: <single-line message>`
- Commits must be narrowly scoped; no drive-by refactors.
- Formatting-only/mechanical changes must be isolated.
- If you cannot run git commands, provide the exact commands to run.

## Testing Strategy

### Coverage Requirements
- **Core logic**: 80% minimum coverage (business logic, data processing, algorithms)
- **Overall project**: 50% minimum coverage
- **Error paths**: Must be explicitly tested (not just happy path)
- No feature is complete without meeting these thresholds.

### Test Types Required
- **Unit tests**: `tests/` — isolated function/class testing
- **Integration tests**: `tests/integration/` — cross-module, API, database interactions
- **Error path tests**: Verify behavior when things fail (network errors, invalid input, etc.)

### Test Tools by Language
- **Python**: `pytest` with `pytest-cov` for coverage. Run: `pytest --cov=src --cov-fail-under=50`
- **TypeScript/JavaScript**: `vitest` (preferred) or `jest`. Run: `vitest --coverage`
- **Go**: Built-in `go test` with `-cover`. Run: `go test -coverprofile=coverage.out ./...`

### Process
- Prefer test-first when feasible, but the hard constraint is coverage at completion.
- Run all relevant tests after each significant change.
- When modifying existing code, ensure existing tests still pass before adding new ones.
- Before implementing a feature, outline the test plan: happy path, error cases, edge cases.

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
- **No `print()` statements** — use structured logging exclusively.
- Log at appropriate levels: `DEBUG` (development), `INFO` (operations), `WARN` (recoverable issues), `ERROR` (failures).
- **All error logs must include**: error type, relevant context/state, stack trace.
- Use JSON logging for production services (enables log aggregation).
- Pipelines should be idempotent where possible.
- Be explicit about fail-fast vs continue-on-error.
- Seed randomness unless non-determinism is required.

### Logging by Language
- **Python**: Use `logging` module, never `print()`. Configure with `logging.basicConfig()` or structured handler.
- **TypeScript/JavaScript**: Use a logger like `pino` or `winston`. No `console.log()` in production code.
- **Go**: Use `log/slog` (structured) or `log` package. No `fmt.Println()` for operational output.

## Dependency Isolation
- Always isolate project dependencies:
  - Python: `venv` or `uv`
  - Node: project-local `node_modules` with lockfile (`package-lock.json` or `pnpm-lock.yaml`)
  - Go: go modules (`go.mod`)
  - Rust: `cargo` (workspace-level `Cargo.lock`)
- Do not install dependencies globally without explicit approval.
- Commit lockfiles; they are source of truth for reproducible builds.

## Secrets Management
- **Never expose API keys or secrets in client-side code.**
- All external API calls must go through backend services or Cloud Functions.
- Use environment variables for secrets; validate they exist at startup.
- **Required `.gitignore` entries**: `.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key`, `credentials.json`
- Create `.env.example` with placeholder values to document required variables.
- For Firebase projects: API keys in client code are okay (they're scoped), but service account keys are NEVER committed.

## Tooling & Code Quality
- Use standard formatting, linting, and typing tools for the language.
- Do not add tools that will not be enforced.
- Code should be readable, explicit, and boring.
- Avoid cleverness unless justified and documented.

### Type Safety Requirements
- **Python**: All code must pass `mypy --strict`. Add type hints to all functions.
  - Use `dataclasses` or `Pydantic` for data structures (not plain dicts).
  - Run `ruff` for linting and formatting.
- **TypeScript**: Use strict mode (`"strict": true` in tsconfig). No `any` types without documented justification.
  - Exception: Third-party library types may require `any` — add `// eslint-disable-next-line @typescript-eslint/no-explicit-any` with reason.
- **JavaScript**: Migrate to TypeScript for any non-trivial project. Pure JS is acceptable only for simple scripts (<100 LOC).
- **Go**: Use `go vet` and `staticcheck`. Enable all linters in `golangci-lint`.

### Pre-commit Hooks (Mandatory for New Projects)
All projects should have pre-commit hooks that run:
1. **Formatting**: `ruff format` (Python), `prettier` (JS/TS), `gofmt` (Go)
2. **Linting**: `ruff check` (Python), `eslint` (JS/TS), `golangci-lint` (Go)
3. **Type checking**: `mypy` (Python), `tsc --noEmit` (TS)
4. **Secrets detection**: `gitleaks` or `trufflehog` (all projects)

See `docs/templates/pre-commit-config.yaml` for standard configuration.

## Guardrails (Hard Constraints)
- Do not refactor unrelated code during a feature.
- Do not change public interfaces without documentation and migration notes.
- Do not introduce heavy dependencies without justification.
- Do not modify data schemas silently.
- Do not optimize prematurely; measure first.
- **Never use bare `except:` or `except Exception:`** — catch specific exceptions only.
- **Never expose API keys or secrets in client-side code** — all external API calls go through backend/Cloud Functions.
- **Never commit `.env` files** — use `.env.example` with placeholder values instead.
- **Split files exceeding 400 LOC** — refactor into focused modules.
- **Split functions exceeding 50 LOC** — extract helper functions.
- **No `print()` statements** — use proper logging (see Observability section).

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

---

## Language-Specific Guidelines

### Python Projects
```
Required setup:
├── pyproject.toml          # Project config with [tool.mypy], [tool.ruff], [tool.pytest]
├── src/                    # Source code
├── tests/                  # Test files
├── .python-version         # Python version (for pyenv/uv)
└── .pre-commit-config.yaml # Pre-commit hooks
```

**Mandatory practices:**
- Use `logging` module, never `print()` for any output
- Add type hints to ALL functions (parameters and return types)
- Use `dataclasses` or `Pydantic` for data structures
- Run `ruff check` and `ruff format` before commits
- Run `mypy --strict` — fix all errors before task complete
- Run `pytest --cov` — meet coverage thresholds

**Error handling:**
```python
# ❌ WRONG - never do this
try:
    result = do_something()
except:
    pass

except Exception as e:
    return None

# ✅ CORRECT - specific exceptions with context
try:
    result = do_something()
except ValueError as e:
    logger.error("Invalid input for do_something", extra={"error": str(e), "input": input_val})
    raise
except ConnectionError as e:
    logger.warning("Connection failed, retrying", extra={"attempt": attempt, "error": str(e)})
    # handle retry logic
```

### TypeScript/JavaScript Projects
```
Required setup:
├── package.json
├── tsconfig.json           # strict: true
├── .eslintrc.js           # or eslint.config.js
├── vitest.config.ts       # or jest.config.js
├── src/
├── tests/
└── .pre-commit-config.yaml
```

**Mandatory practices:**
- Use TypeScript for all non-trivial code (>100 LOC)
- Enable `"strict": true` in tsconfig.json
- No `any` types without documented justification
- Use `vitest` or `jest` for testing
- Run `eslint` and `prettier` before commits

**React-specific requirements:**
- Add Error Boundaries at page/route level
- Implement loading states for all async operations
- Show user feedback (toast/alert) for all mutations
- Use TypeScript strict mode
- Prefer functional components with hooks

### Go Projects
```
Required setup:
├── go.mod
├── go.sum
├── cmd/                   # Entry points
├── internal/              # Private packages
├── pkg/                   # Public packages (if any)
└── .golangci.yml         # Linter config
```

**Mandatory practices:**
- Use `log/slog` for structured logging
- Run `go vet` and `golangci-lint` before commits
- Run `go test -cover` — meet coverage thresholds
- Handle all errors explicitly (no `_` for errors unless justified)

---

## Quick Reference: Common Violations

| Violation | Fix |
|-----------|-----|
| `print()` in Python | Replace with `logging.info()` / `logger.info()` |
| `console.log()` in production | Replace with proper logger or remove |
| `except:` or `except Exception:` | Catch specific exception types |
| API key in source code | Move to environment variable |
| `.env` committed | Add to `.gitignore`, create `.env.example` |
| File >400 LOC | Split into focused modules |
| Function >50 LOC | Extract helper functions |
| No type hints | Add types to all function signatures |
| `any` in TypeScript | Replace with proper type or document why |
| No tests | Write tests before marking task complete |
