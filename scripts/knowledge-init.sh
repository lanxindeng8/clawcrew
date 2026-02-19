#!/bin/bash
# knowledge-init.sh — Initialize team-knowledge directory from templates
# Usage: knowledge-init.sh [target-dir]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/team-knowledge"
TARGET_DIR="${1:-$HOME/.openclaw/team-knowledge}"

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory not found at $TEMPLATE_DIR"
    exit 1
fi

if [ -d "$TARGET_DIR" ]; then
    echo "team-knowledge already exists at $TARGET_DIR"
    echo ""
    echo "Options:"
    echo "  1. Remove existing: rm -rf \"$TARGET_DIR\""
    echo "  2. Use different location: $0 /path/to/new/location"
    exit 0
fi

# Create parent directory if needed
mkdir -p "$(dirname "$TARGET_DIR")"

# Copy templates
cp -r "$TEMPLATE_DIR" "$TARGET_DIR"

# Remove .gitkeep files in target (they're just for git)
find "$TARGET_DIR" -name ".gitkeep" -delete 2>/dev/null || true

echo "✓ Initialized team-knowledge at $TARGET_DIR"
echo ""
echo "Structure created:"
echo "  $TARGET_DIR/"
echo "  ├── INDEX.md              # Master manifest"
echo "  ├── architecture/         # System architecture docs"
echo "  ├── runbooks/             # Operational procedures"
echo "  │   └── deploy.md         # Deployment runbook"
echo "  ├── conventions/          # Team standards"
echo "  │   └── agent-workflow.md # OrcaBot delegation conventions"
echo "  ├── lessons/              # Post-mortems & learnings"
echo "  └── context/              # Project-specific context"
echo ""
echo "Next steps:"
echo "  1. Review and customize INDEX.md"
echo "  2. Add project-specific architecture docs"
echo "  3. Update runbooks with your deploy procedures"
echo ""
echo "Use with: orca-delegate.sh <agent> \"<task>\""
