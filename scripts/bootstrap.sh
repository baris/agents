#!/bin/bash
# bootstrap.sh - Initialize a project with agent tooling
#
# Usage:
#   /path/to/agents/scripts/bootstrap.sh           # Run from target project root
#   /path/to/agents/scripts/bootstrap.sh /some/project  # Or specify project path
#
# What it does:
#   1. Copies AGENTS.md → CLAUDE.md (Claude Code reads this)
#   2. Creates GEMINI.md that references AGENTS.md
#   3. Copies doc templates to docs/templates/
#   4. Copies .claudeignore
#   5. Installs pre-commit hook (if .git exists)

set -euo pipefail

# Where this script lives (the agents repo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_REPO="$(dirname "$SCRIPT_DIR")"

# Target project (current dir or first arg)
TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

echo "Bootstrapping agent tooling in: $TARGET"
echo "Using agents repo: $AGENTS_REPO"
echo ""

# 1. Copy AGENTS.md as the canonical file, symlink CLAUDE.md to it
if [[ -f "$TARGET/AGENTS.md" ]]; then
    echo "AGENTS.md already exists, skipping (won't overwrite)"
else
    cp "$AGENTS_REPO/AGENTS.md" "$TARGET/AGENTS.md"
    echo "✓ Copied AGENTS.md"
fi

# CLAUDE.md -> symlink to AGENTS.md (so you maintain one file)
if [[ -e "$TARGET/CLAUDE.md" ]]; then
    echo "CLAUDE.md already exists, skipping"
else
    ln -s AGENTS.md "$TARGET/CLAUDE.md"
    echo "✓ Created CLAUDE.md -> AGENTS.md symlink"
fi

# 2. Create GEMINI.md (refs AGENTS.md but allows Gemini-specific overrides)
if [[ -f "$TARGET/GEMINI.md" ]]; then
    echo "GEMINI.md already exists, skipping"
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
        echo "docs/templates/$template already exists, skipping"
    else
        cp "$AGENTS_REPO/docs/templates/$template" "$TARGET/docs/templates/"
        echo "✓ Copied docs/templates/$template"
    fi
done

# 4. Copy .claudeignore
if [[ -f "$TARGET/.claudeignore" ]]; then
    echo ".claudeignore already exists, skipping"
else
    cp "$AGENTS_REPO/.claudeignore" "$TARGET/.claudeignore"
    echo "✓ Copied .claudeignore"
fi

# 5. Install pre-commit hook (if git repo)
if [[ -d "$TARGET/.git" ]]; then
    if [[ -f "$TARGET/.git/hooks/pre-commit" ]]; then
        echo "pre-commit hook already exists, skipping"
    else
        cp "$AGENTS_REPO/scripts/pre-commit" "$TARGET/.git/hooks/pre-commit"
        chmod +x "$TARGET/.git/hooks/pre-commit"
        echo "✓ Installed pre-commit hook"
    fi
else
    echo "⚠ Not a git repo, skipping pre-commit hook"
fi

echo ""
echo "Done. Files created:"
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
