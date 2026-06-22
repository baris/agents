#!/bin/bash
# bootstrap.sh - Install agent configuration globally
#
# Usage:
#   /path/to/agents/scripts/bootstrap.sh         # Install/update global config
#   /path/to/agents/scripts/bootstrap.sh --force # Overwrite without prompting
#
# What it does:
#   - Installs AGENTS.md as ~/.gemini/GEMINI.md and ~/.claude/CLAUDE.md
#   - Copies doc templates to ~/.gemini/templates/ and ~/.claude/templates/
#
# These files are used by all AI coding agents unless overridden at project level.

set -euo pipefail

# Where this script lives (the agents repo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_REPO="$(dirname "$SCRIPT_DIR")"

# Parse arguments
FORCE=false
if [[ "${1:-}" == "--force" ]]; then
    FORCE=true
fi

echo "Installing global agent configuration from: $AGENTS_REPO"
echo ""

# ============================================================================
# HELPER
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
# INSTALL
# ============================================================================

# Create directories
mkdir -p ~/.gemini ~/.claude ~/.gemini/templates ~/.claude/templates

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

# All templates to install
TEMPLATES=(
    "ARCHITECTURE.template.md"
    "ADR.template.md"
    "TODO.template.md"
    "DONE.template.md"
    "pre-commit-config.yaml"
)

# Install templates for Gemini
for template in "${TEMPLATES[@]}"; do
    if [[ -f "$AGENTS_REPO/docs/templates/$template" ]]; then
        if [[ -f ~/.gemini/templates/$template ]]; then
            if confirm_overwrite "~/.gemini/templates/$template"; then
                cp "$AGENTS_REPO/docs/templates/$template" ~/.gemini/templates/
                echo "✓ Overwrote ~/.gemini/templates/$template"
            else
                echo "⊘ Skipped ~/.gemini/templates/$template"
            fi
        else
            cp "$AGENTS_REPO/docs/templates/$template" ~/.gemini/templates/
            echo "✓ Installed ~/.gemini/templates/$template"
        fi
    fi
done

# Install templates for Claude
for template in "${TEMPLATES[@]}"; do
    if [[ -f "$AGENTS_REPO/docs/templates/$template" ]]; then
        if [[ -f ~/.claude/templates/$template ]]; then
            if confirm_overwrite "~/.claude/templates/$template"; then
                cp "$AGENTS_REPO/docs/templates/$template" ~/.claude/templates/
                echo "✓ Overwrote ~/.claude/templates/$template"
            else
                echo "⊘ Skipped ~/.claude/templates/$template"
            fi
        else
            cp "$AGENTS_REPO/docs/templates/$template" ~/.claude/templates/
            echo "✓ Installed ~/.claude/templates/$template"
        fi
    fi
done

echo ""
echo "✓ Global agent configuration installed:"
echo ""
echo "  ~/.gemini/"
echo "    GEMINI.md           - Agent instructions for Gemini CLI & Antigravity"
echo "    templates/          - Doc templates (ARCHITECTURE, ADR, TODO, DONE, pre-commit)"
echo ""
echo "  ~/.claude/"
echo "    CLAUDE.md           - Agent instructions for Claude Code"
echo "    templates/          - Doc templates (ARCHITECTURE, ADR, TODO, DONE, pre-commit)"
echo ""
echo "Templates include:"
echo "  - ARCHITECTURE.template.md  - Project architecture documentation"
echo "  - ADR.template.md           - Architecture Decision Records"
echo "  - TODO.template.md          - Task tracking"
echo "  - DONE.template.md          - Definition of Done checklist"
echo "  - pre-commit-config.yaml    - Pre-commit hooks configuration"
echo ""
echo "These apply to ALL projects unless overridden by project-level AGENTS.md,"
echo "CLAUDE.md, or GEMINI.md files in the project root."
echo ""
