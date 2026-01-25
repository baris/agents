#!/bin/bash
# bootstrap.sh - Initialize agent tooling globally and/or per-project
#
# Usage:
#   /path/to/agents/scripts/bootstrap.sh                    # Set up global config
#   /path/to/agents/scripts/bootstrap.sh --global           # Set up global config only
#   /path/to/agents/scripts/bootstrap.sh /some/project      # Set up project (and global if not done)
#   /path/to/agents/scripts/bootstrap.sh --force --global   # Overwrite without prompting
#
# What it does:
#   Global setup (~/.gemini/, ~/.claude/):
#     - Installs AGENTS.md as GEMINI.md and CLAUDE.md
#   Project setup (when path provided):
#     - Copies AGENTS.md, creates symlinks
#     - Copies doc templates to docs/templates/
#     - Copies .claudeignore
#     - Installs pre-commit hook (if .git exists)
#
# Options:
#   --force    Overwrite existing files without prompting

set -euo pipefail

# Where this script lives (the agents repo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_REPO="$(dirname "$SCRIPT_DIR")"

# Parse arguments
MODE="global"
TARGET=""
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --global)
            MODE="global"
            ;;
        --force)
            FORCE=true
            ;;
        *)
            if [[ -d "$arg" ]] || [[ "$arg" == "." ]]; then
                MODE="both"
                TARGET="$(cd "$arg" && pwd)"
            else
                echo "Error: Invalid argument '$arg'. Use --global, --force, or a valid directory path."
                exit 1
            fi
            ;;
    esac
done

echo "Using agents repo: $AGENTS_REPO"
echo ""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
confirm_overwrite() {
    local file="$1"
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    read -p "File $file already exists. Overwrite? [y/N] " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# ============================================================================
# GLOBAL SETUP
# ============================================================================
setup_global() {
    echo "=== Setting up global agent configuration ==="

    # Create directories
    mkdir -p ~/.gemini ~/.claude

    # Install GEMINI.md
    if [[ -f ~/.gemini/GEMINI.md ]]; then
        if confirm_overwrite "~/.gemini/GEMINI.md"; then
            cp "$AGENTS_REPO/AGENTS.md" ~/.gemini/GEMINI.md
            echo "✓ Overwrote ~/.gemini/GEMINI.md"
        else
            echo "⊘ Skipped ~/.gemini/GEMINI.md"
        fi
    else
        cp "$AGENTS_REPO/AGENTS.md" ~/.gemini/GEMINI.md
        echo "✓ Installed ~/.gemini/GEMINI.md"
    fi

    # Install CLAUDE.md
    if [[ -f ~/.claude/CLAUDE.md ]]; then
        if confirm_overwrite "~/.claude/CLAUDE.md"; then
            cp "$AGENTS_REPO/AGENTS.md" ~/.claude/CLAUDE.md
            echo "✓ Overwrote ~/.claude/CLAUDE.md"
        else
            echo "⊘ Skipped ~/.claude/CLAUDE.md"
        fi
    else
        cp "$AGENTS_REPO/AGENTS.md" ~/.claude/CLAUDE.md
        echo "✓ Installed ~/.claude/CLAUDE.md"
    fi

    echo ""
    echo "Global configuration installed."
    echo "  ~/.gemini/GEMINI.md - Used by Gemini CLI & Antigravity"
    echo "  ~/.claude/CLAUDE.md - Used by Claude Code"
    echo ""
    echo "These apply to ALL projects unless overridden at project level."
    echo ""
}

setup_global

# ============================================================================
# PROJECT SETUP (if target specified)
# ============================================================================
if [[ "$MODE" == "both" ]]; then
    echo "=== Setting up project agent configuration ==="
    echo "Project: $TARGET"
    echo ""

    # 1. Copy AGENTS.md as the canonical file, symlink CLAUDE.md to it
    if [[ -f "$TARGET/AGENTS.md" ]]; then
        if confirm_overwrite "$TARGET/AGENTS.md"; then
            cp "$AGENTS_REPO/AGENTS.md" "$TARGET/AGENTS.md"
            echo "✓ Overwrote AGENTS.md"
        else
            echo "⊘ Skipped AGENTS.md"
        fi
    else
        cp "$AGENTS_REPO/AGENTS.md" "$TARGET/AGENTS.md"
        echo "✓ Copied AGENTS.md"
    fi

    # CLAUDE.md -> symlink to AGENTS.md (so you maintain one file)
    if [[ -e "$TARGET/CLAUDE.md" ]]; then
        if confirm_overwrite "$TARGET/CLAUDE.md"; then
            rm -f "$TARGET/CLAUDE.md"
            ln -s AGENTS.md "$TARGET/CLAUDE.md"
            echo "✓ Created CLAUDE.md -> AGENTS.md symlink"
        else
            echo "⊘ Skipped CLAUDE.md"
        fi
    else
        ln -s AGENTS.md "$TARGET/CLAUDE.md"
        echo "✓ Created CLAUDE.md -> AGENTS.md symlink"
    fi

    # 2. Create GEMINI.md (refs AGENTS.md but allows Gemini-specific overrides)
    if [[ -f "$TARGET/GEMINI.md" ]]; then
        if confirm_overwrite "$TARGET/GEMINI.md"; then
            cat > "$TARGET/GEMINI.md" << 'EOF'
# Gemini CLI Instructions

Read and follow all rules in `AGENTS.md`. This file contains Gemini-specific overrides only.

## Gemini-Specific Notes
- At session start, read `docs/ARCHITECTURE.md` and `docs/TODO.md` if they exist.
- Keep responses concise; the user is an experienced engineer.
- If you cannot perform an action, provide exact commands for manual execution.
EOF
            echo "✓ Created GEMINI.md"
        else
            echo "⊘ Skipped GEMINI.md"
        fi
    else
        cat > "$TARGET/GEMINI.md" << 'EOF'
# Gemini CLI Instructions

Read and follow all rules in `AGENTS.md`. This file contains Gemini-specific overrides only.

## Gemini-Specific Notes
- At session start, read `docs/ARCHITECTURE.md` and `docs/TODO.md` if they exist.
- Keep responses concise; the user is an experienced engineer.
- If you cannot perform an action, provide exact commands for manual execution.
EOF
        echo "✓ Created GEMINI.md"
    fi

    # 3. Copy templates
    mkdir -p "$TARGET/docs/templates"
    for template in ARCHITECTURE.template.md ADR.template.md TODO.template.md; do
        if [[ -f "$TARGET/docs/templates/$template" ]]; then
            if confirm_overwrite "$TARGET/docs/templates/$template"; then
                cp "$AGENTS_REPO/docs/templates/$template" "$TARGET/docs/templates/"
                echo "✓ Copied docs/templates/$template"
            else
                echo "⊘ Skipped docs/templates/$template"
            fi
        else
            cp "$AGENTS_REPO/docs/templates/$template" "$TARGET/docs/templates/"
            echo "✓ Copied docs/templates/$template"
        fi
    done

    # 4. Copy .claudeignore
    if [[ -f "$TARGET/.claudeignore" ]]; then
        if confirm_overwrite "$TARGET/.claudeignore"; then
            cp "$AGENTS_REPO/.claudeignore" "$TARGET/.claudeignore"
            echo "✓ Copied .claudeignore"
        else
            echo "⊘ Skipped .claudeignore"
        fi
    else
        cp "$AGENTS_REPO/.claudeignore" "$TARGET/.claudeignore"
        echo "✓ Copied .claudeignore"
    fi

    # 5. Install pre-commit hook (if git repo)
    if [[ -d "$TARGET/.git" ]]; then
        if [[ -f "$TARGET/.git/hooks/pre-commit" ]]; then
            if confirm_overwrite "$TARGET/.git/hooks/pre-commit"; then
                cp "$AGENTS_REPO/scripts/pre-commit" "$TARGET/.git/hooks/pre-commit"
                chmod +x "$TARGET/.git/hooks/pre-commit"
                echo "✓ Installed pre-commit hook"
            else
                echo "⊘ Skipped pre-commit hook"
            fi
        else
            cp "$AGENTS_REPO/scripts/pre-commit" "$TARGET/.git/hooks/pre-commit"
            chmod +x "$TARGET/.git/hooks/pre-commit"
            echo "✓ Installed pre-commit hook"
        fi
    else
        echo "⚠ Not a git repo, skipping pre-commit hook"
    fi

    echo ""
    echo "Done. Project files created:"
    echo "  AGENTS.md      - Main instructions (edit this one)"
    echo "  CLAUDE.md      - Symlink to AGENTS.md (Claude Code reads this)"
    echo "  GEMINI.md      - Gemini instructions (refs AGENTS.md)"
    echo "  .claudeignore  - Excludes noise from Claude context"
    echo "  docs/templates/- Doc templates for ARCHITECTURE, ADR, TODO"
    echo ""
    echo "Next steps:"
    echo "  1. Edit AGENTS.md to customize for this project"
    echo "  2. Create docs/ARCHITECTURE.md using the template"
    echo "  3. For Codex: codex --instructions \"\$(cat AGENTS.md)\""
fi
