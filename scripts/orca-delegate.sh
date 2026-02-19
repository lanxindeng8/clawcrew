#!/bin/bash
# orca-delegate.sh — Knowledge-aware task delegation for OrcaBot
# Usage: orca-delegate.sh <agent> "<task>"
# Automatically includes relevant knowledge files based on agent type and task keywords

set -e

AGENT=$1
TASK=$2
KNOWLEDGE_DIR="${CLAWCREW_KNOWLEDGE_DIR:-$HOME/.openclaw/team-knowledge}"
MAX_CONTEXT="${CLAWCREW_MAX_CONTEXT:-5}"
MAX_SIZE="${CLAWCREW_MAX_CONTEXT_SIZE:-15000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$AGENT" ] || [ -z "$TASK" ]; then
    echo "Usage: orca-delegate.sh <agent> \"<task>\""
    echo ""
    echo "Agents: code, test, design, orca"
    echo ""
    echo "Examples:"
    echo "  orca-delegate.sh code \"Implement the BTC monitor\""
    echo "  orca-delegate.sh test \"Write tests for the API client\""
    echo "  orca-delegate.sh design \"Design the caching layer\""
    exit 1
fi

if [ ! -f "$KNOWLEDGE_DIR/INDEX.md" ]; then
    echo "Warning: No knowledge base found at $KNOWLEDGE_DIR"
    echo "Run knowledge-init.sh to initialize."
    echo "Delegating without context..."
    exec "$SCRIPT_DIR/agent-cli.py" "$AGENT" "$TASK"
fi

# Select knowledge files based on agent type and task keywords
select_knowledge() {
    local agent=$1
    local task=$2
    local files=()
    local count=0
    
    # Agent-specific auto-include tags
    case $agent in
        code)   tags="code|arch|api" ;;
        test)   tags="test|api|code" ;;
        design) tags="arch|api|design" ;;
        *)      tags="onboarding" ;;
    esac
    
    # Add task-specific tags based on keywords
    if echo "$task" | grep -qi "deploy"; then
        tags="$tags|deploy|ops"
    fi
    if echo "$task" | grep -qi "test"; then
        tags="$tags|test"
    fi
    if echo "$task" | grep -qi "api"; then
        tags="$tags|api"
    fi
    if echo "$task" | grep -qi "database\|db\|migration"; then
        tags="$tags|db|migration"
    fi
    
    # Always include onboarding
    tags="$tags|onboarding"
    
    # Find matching files from INDEX.md table
    # Format: | Topic | File | Tags | Updated |
    while IFS='|' read -r _ topic file tag_col _; do
        # Skip header and separator lines
        [[ "$file" =~ ^[[:space:]]*File[[:space:]]*$ ]] && continue
        [[ "$file" =~ ^[[:space:]]*-+[[:space:]]*$ ]] && continue
        [[ -z "$file" ]] && continue
        
        # Clean whitespace
        file=$(echo "$file" | tr -d ' ')
        tag_col=$(echo "$tag_col" | tr -d ' ')
        
        # Skip if file doesn't exist
        [ ! -f "$KNOWLEDGE_DIR/$file" ] && continue
        
        # Check if any tag matches
        if echo "$tag_col" | grep -qiE "$tags"; then
            # Check file size
            local size=$(wc -c < "$KNOWLEDGE_DIR/$file" 2>/dev/null || echo "999999")
            if [ "$size" -lt "$MAX_SIZE" ]; then
                echo "-c"
                echo "$KNOWLEDGE_DIR/$file"
                count=$((count + 1))
                [ "$count" -ge "$MAX_CONTEXT" ] && break
            fi
        fi
    done < <(grep "^|" "$KNOWLEDGE_DIR/INDEX.md" 2>/dev/null || true)
}

# Collect context flags
CONTEXT_FLAGS=()
while IFS= read -r line; do
    [ -n "$line" ] && CONTEXT_FLAGS+=("$line")
done < <(select_knowledge "$AGENT" "$TASK")

# Report what we're including
if [ ${#CONTEXT_FLAGS[@]} -gt 0 ]; then
    echo "Including knowledge context:"
    for ((i=1; i<${#CONTEXT_FLAGS[@]}; i+=2)); do
        echo "  - ${CONTEXT_FLAGS[$i]}"
    done
    echo ""
fi

# Execute delegation
exec "$SCRIPT_DIR/agent-cli.py" "$AGENT" "${CONTEXT_FLAGS[@]}" "$TASK"
