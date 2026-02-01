# Definition of Done Checklist

Use this checklist before marking any task complete. Copy to your PR description or task comment.

## Code Quality
- [ ] Unit tests exist and pass
- [ ] Test coverage meets thresholds (80% core logic, 50% overall)
- [ ] Error paths are explicitly tested
- [ ] Type checking passes (`mypy --strict` / `tsc --strict`)
- [ ] Linting passes (`ruff` / `eslint` / `golangci-lint`)
- [ ] No secrets or API keys in code

## Documentation
- [ ] `docs/ARCHITECTURE.md` updated (if architecture changed)
- [ ] `docs/TODO.md` updated (task marked complete)
- [ ] New public APIs have docstrings/JSDoc
- [ ] README updated (if user-facing changes)

## Error Handling
- [ ] New failure modes have explicit handling
- [ ] Errors logged with context (type, state, stack trace)
- [ ] User-facing operations show feedback on failure

## Data & Schema
- [ ] Schema version bumped (if data format changed)
- [ ] Migration strategy documented (if breaking changes)

## Verification (agent must show evidence)
- [ ] Test output shown
- [ ] `git diff` reviewed
- [ ] UI screenshot provided (if applicable)

---

## Quick Commands

```bash
# Python
pytest --cov=src --cov-fail-under=50 --cov-report=term-missing
mypy --strict src/
ruff check src/ tests/

# TypeScript
npm run test -- --coverage
npx tsc --noEmit
npm run lint

# Go
go test -cover ./...
go vet ./...
golangci-lint run

# Show diff before commit
git diff --staged
```
