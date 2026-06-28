# ADR-0001: Telegram Remote Control Bridge Design using Antigravity SDK

**Date:** 2026-06-28
**Status:** Accepted
**Deciders:** Agent, User

## Context

The user requires a local Telegram Remote Control Bridge for their Antigravity 2.0 instance. The primary goal is to support remote prompt execution (`/ask`), status updates (`/status`), automated tool approvals (`/autoaccept`), and topic-based directory routing.

Initially, a Chrome DevTools Protocol (CDP) WebSocket-scraping approach was planned to connect to the active Electron window. However, this is brittle, relies on DOM structure, has no visual feedback without screenscraping, and depends heavily on browser-level debugging flags. Integrating directly with the Google Antigravity SDK provides a cleaner programmatic model for headless execution, but requires running the agent session inside the bridge daemon itself.

## Decision

We will build the bridge daemon as a Python application using:
1. The `google-antigravity` Python SDK to run the underlying agent and conversation sessions.
2. `python-telegram-bot` to manage the Telegram interface.
3. The SDK's native `workspace_only` policy to enforce strict topic-based directory routing.
4. The SDK's native `ask_user` hook policy to intercept command/file modifications and prompt the whitelisted user for approvals using inline keyboards.

## Alternatives Considered

### Option A: CDP WebSocket Mirroring
- **Pros:** Can control the already-running Electron IDE window visually.
- **Cons:** DOM queries can break on UI changes. CDP is not standard across platforms. Headless log capture requires hooking complex Chromium APIs.

### Option B: Python Antigravity SDK Integration (Chosen)
- **Pros:** Highly robust, uses official APIs, supports native safety policy decorators, handles environment variables easily, allows clean Python-based unit/integration tests, and supports clean folder scoping natively.
- **Cons:** Requires running the agent process in the daemon rather than remote controlling the Electron UI, though this is preferred for headless control.

## Consequences

### Positive
- Strict folder boundaries using the SDK's native `workspace_only` policy.
- Simplified testing via mock agents and pytest.
- Secure, type-safe implementation using Pydantic configurations and strict typing.

### Negative
- The agent session is detached from the Electron IDE UI (running headlessly in the background daemon process), but this is acceptable and expected for a remote control bridge daemon.

## Implementation Notes

We will package the application inside the `telegram-bridge/` folder, utilizing `uv` to manage the virtual environment and package installations.

## References

- [google-antigravity SDK Documentation](file:///Users/tbmetin/.gemini/config/plugins/google-antigravity-sdk/skills/google-antigravity-sdk/SKILL.md)
