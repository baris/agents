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
mkdir -p ~/.gemini ~/.claude ~/.gemini/templates ~/.claude/templates ~/.gemini/config ~/.gemini/config/sidecars

# Initialize venv for telegram-bridge if needed
if [[ -f "$AGENTS_REPO/telegram-bridge/pyproject.toml" ]] && [[ ! -d "$AGENTS_REPO/telegram-bridge/.venv" ]]; then
    echo "Initializing virtual environment for telegram-bridge..."
    if command -v uv >/dev/null 2>&1; then
        (cd "$AGENTS_REPO/telegram-bridge" && uv venv && uv pip install -r pyproject.toml)
    else
        (cd "$AGENTS_REPO/telegram-bridge" && python3 -m venv .venv && .venv/bin/pip install .)
    fi
fi

# Install telegram-bridge sidecar
if [[ -d ~/.gemini/config/sidecars/telegram-bridge ]]; then
    if [[ -L ~/.gemini/config/sidecars/telegram-bridge ]]; then
        ln -sf "$AGENTS_REPO/telegram-bridge" ~/.gemini/config/sidecars/telegram-bridge
        echo "✓ Updated symlink ~/.gemini/config/sidecars/telegram-bridge"
    elif confirm_overwrite "~/.gemini/config/sidecars/telegram-bridge"; then
        mv ~/.gemini/config/sidecars/telegram-bridge ~/.gemini/config/sidecars/telegram-bridge.bak
        ln -sf "$AGENTS_REPO/telegram-bridge" ~/.gemini/config/sidecars/telegram-bridge
        echo "✓ Backed up and symlinked ~/.gemini/config/sidecars/telegram-bridge"
    else
        echo "⊘ Skipped ~/.gemini/config/sidecars/telegram-bridge"
    fi
else
    ln -sf "$AGENTS_REPO/telegram-bridge" ~/.gemini/config/sidecars/telegram-bridge
    echo "✓ Symlinked ~/.gemini/config/sidecars/telegram-bridge"
fi

# Install config.json
if [[ -f ~/.gemini/config/config.json ]]; then
    if [[ -L ~/.gemini/config/config.json ]]; then
        ln -sf "$AGENTS_REPO/config/config.json" ~/.gemini/config/config.json
        echo "✓ Updated symlink ~/.gemini/config/config.json"
    elif confirm_overwrite "~/.gemini/config/config.json"; then
        mv ~/.gemini/config/config.json ~/.gemini/config/config.json.bak
        ln -sf "$AGENTS_REPO/config/config.json" ~/.gemini/config/config.json
        echo "✓ Backed up and symlinked ~/.gemini/config/config.json"
    else
        echo "⊘ Skipped ~/.gemini/config/config.json"
    fi
else
    ln -sf "$AGENTS_REPO/config/config.json" ~/.gemini/config/config.json
    echo "✓ Symlinked ~/.gemini/config/config.json"
fi

# Install mcp_config.json
if [[ -f ~/.gemini/config/mcp_config.json ]]; then
    if [[ -L ~/.gemini/config/mcp_config.json ]]; then
        ln -sf "$AGENTS_REPO/config/mcp_config.json" ~/.gemini/config/mcp_config.json
        echo "✓ Updated symlink ~/.gemini/config/mcp_config.json"
    elif confirm_overwrite "~/.gemini/config/mcp_config.json"; then
        mv ~/.gemini/config/mcp_config.json ~/.gemini/config/mcp_config.json.bak
        ln -sf "$AGENTS_REPO/config/mcp_config.json" ~/.gemini/config/mcp_config.json
        echo "✓ Backed up and symlinked ~/.gemini/config/mcp_config.json"
    else
        echo "⊘ Skipped ~/.gemini/config/mcp_config.json"
    fi
else
    ln -sf "$AGENTS_REPO/config/mcp_config.json" ~/.gemini/config/mcp_config.json
    echo "✓ Symlinked ~/.gemini/config/mcp_config.json"
fi

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
echo "    config/             - Symlinked configurations (config.json, mcp_config.json)"
echo "    sidecars/           - Symlinked sidecars (telegram-bridge)"
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
