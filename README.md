# Agent Configuration & Tooling

Production-grade instructions and tooling for AI coding agents (Claude Code, Gemini CLI, Antigravity, Codex).

## What's Enforced

- **Testing**: 80% coverage for core logic, 50% overall, error paths tested
- **Type Safety**: `mypy --strict` for Python, `strict: true` for TypeScript
- **Error Handling**: No bare `except:`, specific exceptions with logging
- **Secrets**: Never in code, environment variables only, gitleaks detection
- **Code Size**: Files <400 LOC, functions <50 LOC
- **Pre-commit Hooks**: Linting, type checking, secrets detection

## Quick Start

```bash
# 1. Clone this repo
git clone <repo-url> ~/agents

# 2. Install global configuration (applies to all projects)
~/agents/scripts/bootstrap.sh

# 3. Done. All agents now use these rules globally.
```

## What You Get

**Global configuration:**
- `~/.gemini/GEMINI.md` - Instructions for Gemini CLI & Antigravity
- `~/.claude/CLAUDE.md` - Instructions for Claude Code
- `~/.gemini/templates/` - Doc templates
- `~/.claude/templates/` - Doc templates

**Templates included:**
- `ARCHITECTURE.template.md` - Project architecture documentation
- `ADR.template.md` - Architecture Decision Records
- `TODO.template.md` - Task tracking
- `DONE.template.md` - Definition of Done checklist
- `pre-commit-config.yaml` - Pre-commit hooks configuration

**Utilities:**
- `scripts/context.sh` - Generate project context for any agent
- `scripts/bootstrap.sh` - Install/update global configuration

## Files in This Repo

| File | Purpose |
|------|---------|
| `AGENTS.md` | Main instruction set (single source of truth) |
| `CLAUDE.md` | Symlink → AGENTS.md (demonstrates pattern) |
| `GEMINI.md` | Symlink → AGENTS.md (demonstrates pattern) |
| `.claudeignore` | Example excludes for Claude Code context |
| `docs/templates/` | Templates for ARCHITECTURE, ADR, TODO |
| `scripts/bootstrap.sh` | Installer for global configuration |
| `scripts/context.sh` | Project context generator |

## How Agents Read Config

**Claude Code:**
- Reads `~/.claude/CLAUDE.md` (global)
- Or `./CLAUDE.md` in project root (project-specific override)

**Gemini CLI / Antigravity:**
- Reads `~/.gemini/GEMINI.md` (global)
- Or `./GEMINI.md` in project root (project-specific override)

**Codex:**
- No native config; pass via `codex --instructions "$(cat ~/agents/AGENTS.md)"`

## Per-Project Overrides (Optional)

To customize rules for a specific project:

```bash
cd ~/myproject

# Copy the base config
cp ~/agents/AGENTS.md ./AGENTS.md

# Create agent-specific symlinks or files
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md

# Copy templates if needed
mkdir -p docs/templates
cp ~/.claude/templates/*.md docs/templates/

# Edit AGENTS.md to customize for this project
```

Now agents will use `./AGENTS.md` (or `./CLAUDE.md` / `./GEMINI.md`) instead of the global config when working in this project.

## Utilities

### Generate Project Context

```bash
# Dump project context for any agent
~/agents/scripts/context.sh          # basic
~/agents/scripts/context.sh --full   # includes README + entry points
```

Useful for giving agents a quick overview of your project.

## Updating

```bash
cd ~/agents
git pull
~/agents/scripts/bootstrap.sh --force  # Overwrites global configs
```

## Customization

Edit `~/agents/AGENTS.md` (the canonical source), then re-run bootstrap:

```bash
~/agents/scripts/bootstrap.sh --force
```

Or edit the installed copies directly:
- `~/.gemini/GEMINI.md`
- `~/.claude/CLAUDE.md`

## Repository Structure

```
~/agents/
├── AGENTS.md                    # Source of truth
├── CLAUDE.md → AGENTS.md        # Symlink (pattern demonstration)
├── GEMINI.md → AGENTS.md        # Symlink (pattern demonstration)
├── .claudeignore                # Example excludes
├── docs/templates/
│   ├── ARCHITECTURE.template.md # Project architecture
│   ├── ADR.template.md          # Decision records
│   ├── TODO.template.md         # Task tracking
│   ├── DONE.template.md         # Definition of Done checklist
│   └── pre-commit-config.yaml   # Pre-commit hooks
└── scripts/
    ├── bootstrap.sh             # Global installer
    └── context.sh               # Context generator
```

## New Project Setup

```bash
# 1. Initialize project structure
mkdir -p docs/decisions tests

# 2. Copy templates
cp ~/.claude/templates/ARCHITECTURE.template.md docs/ARCHITECTURE.md
cp ~/.claude/templates/TODO.template.md docs/TODO.md

# 3. Set up pre-commit hooks
cp ~/.claude/templates/pre-commit-config.yaml .pre-commit-config.yaml
pip install pre-commit && pre-commit install

# 4. Edit pre-commit config to remove sections for languages you don't use
```
