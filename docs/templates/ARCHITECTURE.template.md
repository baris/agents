# Architecture: [Project Name]

> Last updated: YYYY-MM-DD

## Overview

[2-3 sentence description of what this project does and its primary use case.]

## System Context

```
[ASCII diagram or description of how this system fits into the broader environment]
```

## Core Components

| Component | Responsibility | Location |
|-----------|---------------|----------|
| [name] | [what it does] | `path/to/` |

## Data Flow

1. [Entry point] receives [input]
2. [Component] processes [what]
3. [Output] is [delivered how]

## Key Design Decisions

| Decision | Rationale | ADR |
|----------|-----------|-----|
| [choice] | [why] | [link or "inline"] |

## Module Boundaries

```
project/
├── cmd/          # Entry points (CLI, server)
├── internal/     # Private application code
│   ├── domain/   # Core business logic (no external deps)
│   ├── service/  # Application services
│   └── infra/    # External integrations (DB, APIs)
├── pkg/          # Public libraries (if any)
└── tests/        # Test suites
```

## Dependencies

| Dependency | Purpose | Justification |
|------------|---------|---------------|
| [name] | [what for] | [why this one] |

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENV_VAR` | [what] | [value] |

## Error Handling Strategy

- [How errors propagate]
- [What gets logged vs returned]
- [Retry/fallback behavior]

## Testing Strategy

- Unit tests: [what they cover]
- Integration tests: [what they cover]
- [Any special testing considerations]

## Future Considerations

- [Known limitations]
- [Planned improvements]
- [Technical debt to address]

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial architecture | [name] |
