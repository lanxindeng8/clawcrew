#!/bin/bash

# ClawCrew Setup Script
# Sets up the multi-agent development team for OpenClaw

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
OPENCLAW_CONFIG="$OPENCLAW_DIR/openclaw.json"

echo "================================================"
echo "  ClawCrew Setup - Multi-Agent Dev Team"
echo "================================================"
echo ""

# Check if openclaw.json exists
if [ ! -f "$OPENCLAW_CONFIG" ]; then
    echo "Error: OpenClaw config not found at $OPENCLAW_CONFIG"
    echo "Please install and configure OpenClaw first."
    echo "See: https://docs.openclaw.ai"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)"
    exit 1
fi

echo "This script will:"
echo "  1. Add ClawCrew agents (OrcaBot, DesignBot, CodeBot, TestBot)"
echo "  2. Configure Telegram group binding"
echo "  3. Copy agent workspaces to ~/.openclaw/"
echo ""

# Collect user information
echo "--- Telegram Configuration ---"
echo ""
echo "You need a Telegram bot token. If you don't have one:"
echo "  1. Message @BotFather on Telegram"
echo "  2. Send /newbot and follow instructions"
echo "  3. IMPORTANT: Disable privacy mode:"
echo "     /mybots -> Select bot -> Bot Settings -> Group Privacy -> Turn off"
echo ""
read -p "Telegram Bot Token: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "Error: Bot token is required"
    exit 1
fi

echo ""
echo "You need the Telegram group chat ID."
echo "To get it: Add @userinfobot to your group, it will show the chat_id"
echo "(Group IDs are typically negative numbers like -1234567890)"
echo ""
read -p "Telegram Group ID: " GROUP_ID

if [ -z "$GROUP_ID" ]; then
    echo "Error: Group ID is required"
    exit 1
fi

echo ""
echo "Enter Telegram user IDs allowed to interact with the bots."
echo "To get your user ID: Message @userinfobot privately"
echo "(Separate multiple IDs with commas, e.g., 123456789,987654321)"
echo ""
read -p "Allowed User IDs: " ALLOWED_IDS

if [ -z "$ALLOWED_IDS" ]; then
    echo "Error: At least one user ID is required"
    exit 1
fi

echo ""
read -p "Account name (default: clawcrew): " ACCOUNT_NAME
ACCOUNT_NAME=${ACCOUNT_NAME:-clawcrew}

echo ""
echo "--- Configuration Summary ---"
echo "  Bot Token: ${BOT_TOKEN:0:20}..."
echo "  Group ID: $GROUP_ID"
echo "  Allowed Users: $ALLOWED_IDS"
echo "  Account Name: $ACCOUNT_NAME"
echo ""
read -p "Proceed with setup? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo "--- Setting up ClawCrew ---"

# Convert comma-separated IDs to JSON array
ALLOWED_IDS_JSON=$(echo "$ALLOWED_IDS" | tr ',' '\n' | jq -R . | jq -s .)

# Backup the original config
cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
echo "[1/4] Backed up original config"

# Create the agents JSON
AGENTS_JSON=$(cat <<EOF
[
  {
    "id": "orca",
    "name": "OrcaBot",
    "workspace": "$OPENCLAW_DIR/workspace-orca",
    "model": "anthropic/claude-sonnet-4-5",
    "identity": {
      "name": "OrcaBot"
    },
    "groupChat": {
      "mentionPatterns": ["@orca", "@OrcaBot"]
    },
    "subagents": {
      "allowAgents": ["design", "code", "test"]
    }
  },
  {
    "id": "design",
    "name": "DesignBot",
    "workspace": "$OPENCLAW_DIR/workspace-design",
    "model": "anthropic/claude-opus-4-5",
    "identity": {
      "name": "DesignBot"
    },
    "groupChat": {
      "mentionPatterns": ["@design", "@DesignBot"]
    }
  },
  {
    "id": "code",
    "name": "CodeBot",
    "workspace": "$OPENCLAW_DIR/workspace-code",
    "model": "anthropic/claude-opus-4-5",
    "identity": {
      "name": "CodeBot"
    },
    "groupChat": {
      "mentionPatterns": ["@code", "@CodeBot"]
    }
  },
  {
    "id": "test",
    "name": "TestBot",
    "workspace": "$OPENCLAW_DIR/workspace-test",
    "model": "anthropic/claude-sonnet-4-5",
    "identity": {
      "name": "TestBot"
    },
    "groupChat": {
      "mentionPatterns": ["@test", "@TestBot"]
    }
  }
]
EOF
)

# Create the binding JSON
BINDING_JSON=$(cat <<EOF
{
  "agentId": "orca",
  "match": {
    "channel": "telegram",
    "accountId": "$ACCOUNT_NAME",
    "peer": {
      "kind": "group",
      "id": "$GROUP_ID"
    }
  }
}
EOF
)

# Create the account JSON
ACCOUNT_JSON=$(cat <<EOF
{
  "dmPolicy": "pairing",
  "botToken": "$BOT_TOKEN",
  "groups": {
    "$GROUP_ID": {
      "requireMention": false
    }
  },
  "allowFrom": $ALLOWED_IDS_JSON,
  "groupPolicy": "allowlist",
  "streamMode": "partial"
}
EOF
)

# Update the config file using jq
# 1. Add agents to agents.list (filter out existing clawcrew agents first)
# 2. Add binding to bindings array
# 3. Add account to channels.telegram.accounts

jq --argjson agents "$AGENTS_JSON" \
   --argjson binding "$BINDING_JSON" \
   --argjson account "$ACCOUNT_JSON" \
   --arg account_name "$ACCOUNT_NAME" \
   '
   # Remove existing clawcrew agents if any
   .agents.list = [.agents.list[] | select(.id | IN("orca", "design", "code", "test") | not)]
   # Add new agents
   | .agents.list += $agents
   # Initialize bindings if not exists
   | .bindings = (if .bindings then .bindings else [] end)
   # Remove existing orca binding if any
   | .bindings = [.bindings[] | select(.agentId != "orca")]
   # Add new binding
   | .bindings += [$binding]
   # Ensure channels.telegram.accounts exists
   | .channels.telegram.accounts = (if .channels.telegram.accounts then .channels.telegram.accounts else {} end)
   # Add account
   | .channels.telegram.accounts[$account_name] = $account
   # Enable telegram plugin
   | .plugins.entries.telegram.enabled = true
   ' "$OPENCLAW_CONFIG" > "$OPENCLAW_CONFIG.tmp" && mv "$OPENCLAW_CONFIG.tmp" "$OPENCLAW_CONFIG"

echo "[2/4] Updated openclaw.json with agents and bindings"

# Copy workspace folders
echo "[3/4] Copying workspace folders..."

for workspace in workspace-orca workspace-design workspace-code workspace-test; do
    if [ -d "$SCRIPT_DIR/$workspace" ]; then
        cp -r "$SCRIPT_DIR/$workspace" "$OPENCLAW_DIR/"
        echo "  Copied $workspace"
    else
        echo "  Warning: $workspace not found in $SCRIPT_DIR"
    fi
done

echo "[4/4] Setup complete!"

echo ""
echo "================================================"
echo "  ClawCrew is ready!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw gateway:"
echo "     openclaw gateway restart"
echo ""
echo "  2. Send a message in your Telegram group:"
echo "     'Create a Python module to calculate distance between two points'"
echo ""
echo "  3. Watch OrcaBot coordinate the team!"
echo ""
echo "Workspaces installed at:"
echo "  $OPENCLAW_DIR/workspace-orca"
echo "  $OPENCLAW_DIR/workspace-design"
echo "  $OPENCLAW_DIR/workspace-code"
echo "  $OPENCLAW_DIR/workspace-test"
echo ""
echo "Config backup saved. To revert:"
echo "  cp $OPENCLAW_CONFIG.backup.* $OPENCLAW_CONFIG"
echo ""
