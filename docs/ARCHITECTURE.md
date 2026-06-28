# Architecture: Telegram Remote Control Bridge

> Last updated: 2026-06-28

## Overview

The Telegram Remote Control Bridge is a lightweight background daemon written in Python that allows remote execution, monitoring, and interactive control of autonomous software engineering agent loops directly via a Telegram Bot. It uses the `google-antigravity` SDK and exposes whitelisted command evaluation, real-time log streaming, and topic-based folder scoping.

## System Context

```
                   +------------------------+
                   |  Telegram Client (User) |
                   +-----------+------------+
                               |
                               | (HTTPS / WebSockets)
                               v
                   +-----------+------------+
                   |      Telegram Bot      |
                   +-----------+------------+
                               |
                               v
            +------------------+-------------------+
            |  Telegram Bridge Daemon (Python)      |
            |                                      |
            |  +--------------------------------+  |
            |  |  Agent Manager                 |  |
            |  |  (Wraps google-antigravity SDK) |  |
            |  +---------------+----------------+  |
            |                  |                   |
            +------------------+-------------------+
                               |
                               v (Local Tool Calls)
                   +-----------+------------+
                   |    Local File System   |
                   |    & Shell Executor    |
                   +------------------------+
```

## Core Components

| Component | Responsibility | Location |
|-----------|---------------|----------|
| `config` | Parses and validates environment variables and mappings | `telegram-bridge/src/config.py` |
| `logger` | Handles structured JSON logging for observability | `telegram-bridge/src/logger.py` |
| `agent_manager` | Orchestrates the `google-antigravity` agent sessions, workspaces, and safety policies | `telegram-bridge/src/agent_manager.py` |
| `bot` | Manages Telegram command routing, whitelisting, and inline confirmations | `telegram-bridge/src/bot.py` |
| `main` | Entrypoint bootstrap coordinating lifecycle startup and teardown | `telegram-bridge/src/main.py` |

## Data Flow

1. Telegram Bot receives `/ask <prompt>` inside a specific Telegram group topic.
2. The bot controller parses the message thread (Topic ID), checks the whitelisted sender ID, and fetches the mapped path.
3. The prompt is passed to the topic-isolated `AgentSession` run by `AgentManager`.
4. The `Agent` processes the prompt, requesting tool executions (e.g. `run_command` or file modifications).
5. The `ask_user` policy handler intercepts the tool request and sends an interactive confirmation card with "Approve" and "Reject" buttons back to Telegram.
6. The user clicks "Approve", the callback resolves the pending future, and the tool is executed. The output is streamed back to Telegram.

## Key Design Decisions

| Decision | Rationale | ADR |
|----------|-----------|-----|
| Google Antigravity SDK | Direct integration with agent capabilities, native safety policies, and simple headless execution. | [ADR-0001](file:///Users/tbmetin/repos/agents/docs/decisions/2026-06-28-telegram-bridge-design.md) |
| python-telegram-bot | Asynchronous, well-typed Python framework for building robust Telegram bots. | [ADR-0001](file:///Users/tbmetin/repos/agents/docs/decisions/2026-06-28-telegram-bridge-design.md) |

## Module Boundaries

```
telegram-bridge/
├── src/
│   ├── __init__.py
│   ├── config.py       # Configuration models
│   ├── logger.py       # Structured logs
│   ├── agent_manager.py # SDK wrappers and policies
│   ├── bot.py          # Telegram handlers
│   └── main.py         # Entrypoint
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_agent_manager.py
│   └── test_bot.py
├── pyproject.toml      # Dependency & lint config
└── .python-version     # Python runtime constraint
```

## Dependencies

| Dependency | Purpose | Justification |
|------------|---------|---------------|
| `google-antigravity` | Agent engine | Built-in capabilities, session management, and safety boundaries. |
| `python-telegram-bot` | Bot framework | High-quality async support for Telegram Bot APIs. |
| `pydantic-settings` | Configuration | Strict validation of env configs and JSON schemas. |
| `python-json-logger` | Logging | Production structured JSON output formatting. |

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | API Token for the bot | (Required) |
| `WHITELISTED_USER_ID` | Telegram user ID allowed to execute commands | (Required) |
| `USE_TOPICS` | Flag to enable topic-to-workspace mapping | `true` |
| `TOPIC_MAPPINGS_FILE` | Path to JSON file declaring Topic ID to path maps | `topic_mappings.json` |
| `DEFAULT_WORKSPACE_DIR` | Fallback workspace path for unmapped topics | `/Users/tbmetin/repos/agents` |

## Error Handling Strategy

- All exceptions raised in tool executions or communication handlers are caught within asynchronous boundaries.
- Fatal errors during initialization fail-fast with clean stack traces and context logged.
- User-facing failures (e.g. command errors, invalid directories) are reported back to the whitelisted Telegram user instead of crashing the daemon.
- Unhandled model outputs are encapsulated in logging and session contexts for troubleshooting.

## Testing Strategy

- Unit tests: Configuration loading, environment checks, and whitelisting.
- Integration tests: Topic workspace mapping resolution, safety policy isolation, and callback query futures resolution.
- Mocks: Simulated Telegram bot context and mocked Antigravity agent loops.

## Future Considerations

- Session persistence across daemon restarts.
- Auto-recovery of bot polling loops in case of network drops.
- Periodic heartbeat checks.

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-06-28 | Initial architecture | Antigravity |
