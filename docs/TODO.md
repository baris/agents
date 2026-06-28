# TODO

> Active task queue. Organized by priority. Update at start/end of every task.

## In Progress

- [ ] **Scaffolding & Setup** — Set up initial project config, workspace layout, and ADRs.
  - Assignee: agent
  - Started: 2026-06-28
  - Notes: Currently setting up documentation first, followed by packaging files.

## High Priority

- [ ] Core implementation of configuration parser (`src/config.py`)
- [ ] Core implementation of structured logger (`src/logger.py`)
- [ ] Core implementation of agent manager (`src/agent_manager.py`)
- [ ] Core implementation of Telegram Bot handlers (`src/bot.py`)

## Medium Priority

- [ ] Add unit and integration tests using pytest
- [ ] Configure linting and typechecking (mypy, ruff)

## Low Priority / Nice to Have

- [ ] Expose an interactive local web server logging dashboard mapped via localhost.run
- [ ] Setup persistence for active agent turns

## Blocked

- None

---

## Completed

- [x] Initial architecture documentation (`docs/ARCHITECTURE.md`) — 2026-06-28
