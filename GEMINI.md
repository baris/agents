# Gemini CLI Instructions

This file provides instructions for Gemini CLI. It mirrors AGENTS.md with minor Gemini-specific adjustments.

## Include Base Rules

Read and follow all rules in `AGENTS.md` in this directory. Those are the canonical operating procedures.

## Gemini-Specific Notes

### Tool Usage
- When running shell commands, prefer explicit paths over relative paths.
- Always confirm destructive operations before executing.
- If a command fails, show the full error output before retrying.

### Output Format
- Keep responses concise; the user is an experienced engineer.
- Use code blocks with language tags for all code.
- When showing file changes, use unified diff format when helpful.

### Context Management
- At session start, read `docs/ARCHITECTURE.md` and `docs/TODO.md` if they exist.
- Reference the architecture doc before proposing structural changes.
- If you need more context about a file, ask or read it rather than assuming.

### Limitations Acknowledgment
- If you cannot perform an action (file write, command execution), provide the exact commands/content for the user to run manually.
- Be explicit about what you can and cannot verify.
