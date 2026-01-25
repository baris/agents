#!/bin/bash
# context.sh - Generate project context for any AI coding agent
# Usage: ./scripts/context.sh [--full]
#
# Output can be piped or copied into any agent (Claude, Gemini, Codex, etc.)

set -euo pipefail

FULL_MODE="${1:-}"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"

echo "## Project: $PROJECT_NAME"
echo "## Root: $PROJECT_ROOT"
echo ""

# Detect primary language
detect_language() {
    if [[ -f "$PROJECT_ROOT/go.mod" ]]; then echo "Go"
    elif [[ -f "$PROJECT_ROOT/Cargo.toml" ]]; then echo "Rust"
    elif [[ -f "$PROJECT_ROOT/pyproject.toml" ]] || [[ -f "$PROJECT_ROOT/setup.py" ]]; then echo "Python"
    elif [[ -f "$PROJECT_ROOT/package.json" ]]; then echo "Node/TypeScript"
    elif [[ -f "$PROJECT_ROOT/Makefile" ]]; then echo "Make-based"
    else echo "Unknown"
    fi
}

echo "## Language: $(detect_language)"
echo ""

# Git info
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "## Branch: $(git branch --show-current)"
    echo "## Last 5 commits:"
    git log --oneline -5 | sed 's/^/  /'
    echo ""
fi

# Architecture doc (if exists)
if [[ -f "$PROJECT_ROOT/docs/ARCHITECTURE.md" ]]; then
    echo "## Architecture (docs/ARCHITECTURE.md):"
    head -50 "$PROJECT_ROOT/docs/ARCHITECTURE.md" | sed 's/^/  /'
    echo "  [... truncated, see full file]"
    echo ""
fi

# TODO doc (if exists)
if [[ -f "$PROJECT_ROOT/docs/TODO.md" ]]; then
    echo "## Active TODOs (docs/TODO.md):"
    head -30 "$PROJECT_ROOT/docs/TODO.md" | sed 's/^/  /'
    echo ""
fi

# Project structure
echo "## Structure (depth=2):"
if command -v tree > /dev/null 2>&1; then
    tree -L 2 -I 'node_modules|vendor|.git|__pycache__|.venv|dist|build|target' "$PROJECT_ROOT" | head -40
else
    find "$PROJECT_ROOT" -maxdepth 2 -type f \
        ! -path '*/.git/*' \
        ! -path '*/node_modules/*' \
        ! -path '*/.venv/*' \
        ! -path '*/vendor/*' \
        ! -path '*/__pycache__/*' \
        | head -40 | sed "s|$PROJECT_ROOT/||"
fi
echo ""

# Full mode: include more detail
if [[ "$FULL_MODE" == "--full" ]]; then
    echo "## Key files content:"

    # README
    if [[ -f "$PROJECT_ROOT/README.md" ]]; then
        echo "### README.md:"
        head -40 "$PROJECT_ROOT/README.md" | sed 's/^/  /'
        echo ""
    fi

    # Main entry points
    for entry in main.go main.py index.ts index.js cmd/main.go src/main.rs; do
        if [[ -f "$PROJECT_ROOT/$entry" ]]; then
            echo "### $entry:"
            head -50 "$PROJECT_ROOT/$entry" | sed 's/^/  /'
            echo ""
        fi
    done
fi

echo "---"
echo "Generated: $(date -Iseconds)"
