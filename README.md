# Agent Configuration & Tooling

Production-grade instructions and tooling for AI coding agents (Claude Code, Gemini CLI, Antigravity, Codex).

## Quick Start

```bash
# 1. Clone this repo
git clone <repo-url> ~/agents

# 2. Set up global configuration (applies to all projects)
~/agents/scripts/bootstrap.sh

# 3. Done. All agents now use these rules globally.
```

## Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Main instruction set (single source of truth) |
| `CLAUDE.md` | Symlink → AGENTS.md (Claude Code reads this) |
| `GEMINI.md` | Gemini-specific instructions (refs AGENTS.md) |
| `.claudeignore` | Excludes deps, build artifacts from agent context |
| `docs/templates/` | Templates for ARCHITECTURE, ADR, TODO |
| `scripts/bootstrap.sh` | Setup script for global/project config |
| `scripts/context.sh` | Generate project context for any agent |
| `scripts/pre-commit` | Git hook to catch agent mistakes |

## How Agents Read Config

**Claude Code:**
- Reads `~/.claude/CLAUDE.md` (global)
- Or `./CLAUDE.md` in project root (project-specific override)

**Gemini CLI / Antigravity:**
- Reads `~/.gemini/GEMINI.md` (global)
- Or `./GEMINI.md` in project root (project-specific override)

**Codex:**
- No native config; pass via `codex --instructions "$(cat ~/agents/AGENTS.md)"`

## Usage

### Global Setup (Recommended)
```bash
# Install once, applies to all projects
~/agents/scripts/bootstrap.sh
```

Creates:
- `~/.gemini/GEMINI.md`
- `~/.claude/CLAUDE.md`

### Per-Project Setup (Optional)
```bash
# Only if you need project-specific rules
cd ~/myproject
~/agents/scripts/bootstrap.sh .
```

Creates:
- `./AGENTS.md` (edit this for project overrides)
- `./CLAUDE.md` → symlink to AGENTS.md
- `./GEMINI.md` (refs AGENTS.md)
- `./docs/templates/`
- `./.claudeignore`
- `.git/hooks/pre-commit`

### Generate Context
```bash
# Dump project context for any agent
~/agents/scripts/context.sh          # basic
~/agents/scripts/context.sh --full   # includes README + entry points
```

## Updating

```bash
cd ~/agents
git pull
~/agents/scripts/bootstrap.sh --force  # Overwrites global configs
```

## Customization

Edit `~/agents/AGENTS.md`, then re-run bootstrap to sync:
```bash
~/agents/scripts/bootstrap.sh --force
```

## Structure

```
~/agents/
├── AGENTS.md                    # Source of truth
├── CLAUDE.md → AGENTS.md
├── GEMINI.md
├── .claudeignore
├── docs/templates/
│   ├── ARCHITECTURE.template.md
│   ├── ADR.template.md
│   └── TODO.template.md
└── scripts/
    ├── bootstrap.sh
    ├── context.sh
    └── pre-commit
```
