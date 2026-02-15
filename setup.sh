#!/bin/bash

# ClawCrew Setup Script
# Sets up the multi-agent development team for OpenClaw

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
OPENCLAW_CONFIG="$OPENCLAW_DIR/openclaw.json"

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

# ============================================================
# HELP
# ============================================================
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "ClawCrew Setup - Multi-Agent Dev Team for OpenClaw"
    echo ""
    echo "Usage: ./setup.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  (no args)       Install ClawCrew agents and configure Telegram"
    echo "  -u, --uninstall Remove ClawCrew agents, bindings, and workspaces"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Install will:"
    echo "  - Register 4 agents: orca (orchestrator), design, code, test"
    echo "  - Configure Telegram binding for OrcaBot"
    echo "  - Set required OpenClaw settings"
    echo "  - Copy workspace folders to ~/.openclaw/"
    echo ""
    echo "Uninstall will:"
    echo "  - Remove all ClawCrew agents from config"
    echo "  - Remove OrcaBot Telegram binding"
    echo "  - Remove broadcast entries"
    echo "  - Optionally remove Telegram account"
    echo "  - Optionally remove workspace folders"
    echo ""
    echo "More info: https://github.com/lanxindeng8/clawcrew"
    exit 0
fi

# ============================================================
# UNINSTALL MODE
# ============================================================
if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    echo "================================================"
    echo "  ClawCrew Uninstall"
    echo "================================================"
    echo ""
    echo "This will remove:"
    echo "  - ClawCrew agents (orca, design, code, test)"
    echo "  - OrcaBot Telegram binding"
    echo "  - Broadcast entries"
    echo "  - Telegram account (optional)"
    echo "  - Workspace folders (optional)"
    echo ""

    # Show current ClawCrew accounts
    echo "--- Current ClawCrew Configuration ---"
    CLAWCREW_AGENTS=$(jq -r '.agents.list | map(select(.id | IN("orca", "design", "code", "test"))) | length' "$OPENCLAW_CONFIG")
    echo "  ClawCrew agents installed: $CLAWCREW_AGENTS"

    ORCA_BINDINGS=$(jq -r '.bindings | map(select(.agentId == "orca")) | length' "$OPENCLAW_CONFIG")
    echo "  OrcaBot bindings: $ORCA_BINDINGS"

    # List telegram accounts that might be ClawCrew related
    echo ""
    echo "  Telegram accounts:"
    jq -r '.channels.telegram.accounts // {} | keys[]' "$OPENCLAW_CONFIG" 2>/dev/null | while read -r acc; do
        echo "    - $acc"
    done

    echo ""
    read -p "Account name to remove (leave empty to skip): " REMOVE_ACCOUNT

    echo ""
    read -p "Also remove workspace folders? (y/n): " REMOVE_WORKSPACES

    echo ""
    read -p "Proceed with uninstall? (y/n): " CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Uninstall cancelled."
        exit 0
    fi

    echo ""
    echo "--- Uninstalling ClawCrew ---"

    # Backup config
    cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
    echo "[1/4] Backed up config"

    # Remove all ClawCrew agents, bindings, broadcast, and optionally account
    if [ -n "$REMOVE_ACCOUNT" ]; then
        jq --arg acc "$REMOVE_ACCOUNT" '
        # Remove all ClawCrew agents
        .agents.list = [.agents.list[] | select(.id | IN("orca", "design", "code", "test") | not)]
        # Remove ClawCrew bindings
        | .bindings = [.bindings[] | select(.agentId | IN("orca", "design", "code", "test") | not)]
        # Remove broadcast entries containing ClawCrew agents
        | if .broadcast then
            .broadcast = (.broadcast | with_entries(
              if .key == "strategy" then .
              else .value = [.value[] | select(. | IN("orca", "design", "code", "test") | not)] | select(.value | length > 0)
              end
            ))
          else . end
        # Remove specified account
        | del(.channels.telegram.accounts[$acc])
        ' "$OPENCLAW_CONFIG" > "$OPENCLAW_CONFIG.tmp" && mv "$OPENCLAW_CONFIG.tmp" "$OPENCLAW_CONFIG"
        echo "[2/4] Removed ClawCrew agents, bindings, broadcast, and account '$REMOVE_ACCOUNT'"
    else
        jq '
        # Remove all ClawCrew agents
        .agents.list = [.agents.list[] | select(.id | IN("orca", "design", "code", "test") | not)]
        # Remove ClawCrew bindings
        | .bindings = [.bindings[] | select(.agentId | IN("orca", "design", "code", "test") | not)]
        # Remove broadcast entries containing ClawCrew agents
        | if .broadcast then
            .broadcast = (.broadcast | with_entries(
              if .key == "strategy" then .
              else .value = [.value[] | select(. | IN("orca", "design", "code", "test") | not)] | select(.value | length > 0)
              end
            ))
          else . end
        ' "$OPENCLAW_CONFIG" > "$OPENCLAW_CONFIG.tmp" && mv "$OPENCLAW_CONFIG.tmp" "$OPENCLAW_CONFIG"
        echo "[2/4] Removed ClawCrew agents, bindings, and broadcast (account kept)"
    fi

    # Remove workspace folders
    if [ "$REMOVE_WORKSPACES" = "y" ] || [ "$REMOVE_WORKSPACES" = "Y" ]; then
        for workspace in workspace-orca workspace-design workspace-code workspace-test; do
            if [ -d "$OPENCLAW_DIR/$workspace" ]; then
                rm -rf "$OPENCLAW_DIR/$workspace"
                echo "[3/4] Removed $OPENCLAW_DIR/$workspace"
            fi
        done
    else
        echo "[3/4] Workspace folders kept"
    fi

    # Verify
    echo "[4/4] Verifying..."
    REMAINING_ORCA=$(jq -r '.agents.list | map(select(.id == "orca")) | length' "$OPENCLAW_CONFIG")
    REMAINING_BINDINGS=$(jq -r '.bindings | map(select(.agentId == "orca")) | length' "$OPENCLAW_CONFIG")

    if [ "$REMAINING_ORCA" -eq 0 ] && [ "$REMAINING_BINDINGS" -eq 0 ]; then
        echo "  ✓  OrcaBot removed successfully"
    else
        echo "  ⚠️  Some components may remain (agent: $REMAINING_ORCA, bindings: $REMAINING_BINDINGS)"
    fi

    echo ""
    echo "================================================"
    echo "  ClawCrew uninstalled!"
    echo "================================================"
    echo ""
    echo "Don't forget to restart OpenClaw gateway:"
    echo "  openclaw gateway restart"
    echo ""
    exit 0
fi

# ============================================================
# INSTALL MODE
# ============================================================
echo "================================================"
echo "  ClawCrew Setup - Multi-Agent Dev Team"
echo "================================================"
echo ""
echo "This script will:"
echo "  1. Register 4 agents: orca, design, code, test"
echo "  2. Configure Telegram binding for OrcaBot"
echo "  3. Copy agent workspaces to ~/.openclaw/"
echo ""

# Check for saved credentials
CLAWCREW_ENV="$OPENCLAW_DIR/.clawcrew.env"
USE_SAVED=false

if [ -f "$CLAWCREW_ENV" ]; then
    echo "Found saved credentials at $CLAWCREW_ENV"
    source "$CLAWCREW_ENV"

    if [ -n "$CLAWCREW_BOT_TOKEN" ] && [ -n "$CLAWCREW_GROUP_ID" ] && [ -n "$CLAWCREW_ALLOWED_IDS" ]; then
        echo ""
        echo "Saved configuration:"
        echo "  Bot Token: ${CLAWCREW_BOT_TOKEN:0:20}..."
        echo "  Group ID: $CLAWCREW_GROUP_ID"
        echo "  Allowed Users: $CLAWCREW_ALLOWED_IDS"
        echo "  Account Name: ${CLAWCREW_ACCOUNT_NAME:-clawcrew}"
        echo ""
        read -p "Use saved credentials? (Y/n): " USE_SAVED_ANSWER
        if [ "$USE_SAVED_ANSWER" != "n" ] && [ "$USE_SAVED_ANSWER" != "N" ]; then
            USE_SAVED=true
            BOT_TOKEN="$CLAWCREW_BOT_TOKEN"
            GROUP_ID="$CLAWCREW_GROUP_ID"
            ALLOWED_IDS="$CLAWCREW_ALLOWED_IDS"
            ACCOUNT_NAME="${CLAWCREW_ACCOUNT_NAME:-clawcrew}"
            echo "Using saved credentials."
        fi
    fi
fi

if [ "$USE_SAVED" = false ]; then
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

    # Save credentials for future use
    echo "# ClawCrew saved credentials" > "$CLAWCREW_ENV"
    echo "CLAWCREW_BOT_TOKEN=\"$BOT_TOKEN\"" >> "$CLAWCREW_ENV"
    echo "CLAWCREW_GROUP_ID=\"$GROUP_ID\"" >> "$CLAWCREW_ENV"
    echo "CLAWCREW_ALLOWED_IDS=\"$ALLOWED_IDS\"" >> "$CLAWCREW_ENV"
    echo "CLAWCREW_ACCOUNT_NAME=\"$ACCOUNT_NAME\"" >> "$CLAWCREW_ENV"
    chmod 600 "$CLAWCREW_ENV"
    echo ""
    echo "Credentials saved to $CLAWCREW_ENV"
fi

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
echo "--- Checking Current Configuration ---"

# Check required settings
ISSUES=()

# Check agents.defaults.subagents.maxConcurrent
SUBAGENT_MAX=$(jq -r '.agents.defaults.subagents.maxConcurrent // 0' "$OPENCLAW_CONFIG")
if [ "$SUBAGENT_MAX" -lt 8 ]; then
    echo "  ⚠️  agents.defaults.subagents.maxConcurrent = $SUBAGENT_MAX (need >= 8)"
    ISSUES+=("subagents_max")
else
    echo "  ✓  agents.defaults.subagents.maxConcurrent = $SUBAGENT_MAX"
fi

# Check channels.telegram.enabled
TG_ENABLED=$(jq -r '.channels.telegram.enabled // false' "$OPENCLAW_CONFIG")
if [ "$TG_ENABLED" != "true" ]; then
    echo "  ⚠️  channels.telegram.enabled = $TG_ENABLED (need true)"
    ISSUES+=("telegram_enabled")
else
    echo "  ✓  channels.telegram.enabled = true"
fi

# Check channels.telegram.groupPolicy
TG_GROUP_POLICY=$(jq -r '.channels.telegram.groupPolicy // "none"' "$OPENCLAW_CONFIG")
if [ "$TG_GROUP_POLICY" != "allowlist" ]; then
    echo "  ⚠️  channels.telegram.groupPolicy = $TG_GROUP_POLICY (need allowlist)"
    ISSUES+=("telegram_group_policy")
else
    echo "  ✓  channels.telegram.groupPolicy = allowlist"
fi

# Check plugins.entries.telegram.enabled
TG_PLUGIN=$(jq -r '.plugins.entries.telegram.enabled // false' "$OPENCLAW_CONFIG")
if [ "$TG_PLUGIN" != "true" ]; then
    echo "  ⚠️  plugins.entries.telegram.enabled = $TG_PLUGIN (need true)"
    ISSUES+=("telegram_plugin")
else
    echo "  ✓  plugins.entries.telegram.enabled = true"
fi

# Check if bot token is already used by another account
EXISTING_ACCOUNT=$(jq -r --arg token "$BOT_TOKEN" '.channels.telegram.accounts // {} | to_entries[] | select(.value.botToken == $token) | .key' "$OPENCLAW_CONFIG" 2>/dev/null || echo "")
if [ -n "$EXISTING_ACCOUNT" ] && [ "$EXISTING_ACCOUNT" != "$ACCOUNT_NAME" ]; then
    echo "  ⚠️  Bot token already used by account: $EXISTING_ACCOUNT (will be removed)"
    ISSUES+=("duplicate_token")
else
    echo "  ✓  Bot token not in use by other accounts"
fi

echo ""
if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "Found ${#ISSUES[@]} setting(s) that need to be updated."
    echo "These will be automatically fixed during setup."
fi

echo ""
echo "--- Setting up ClawCrew ---"

# Convert comma-separated IDs to JSON array
ALLOWED_IDS_JSON=$(echo "$ALLOWED_IDS" | tr ',' '\n' | jq -R . | jq -s .)

# Backup the original config
cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
echo "[1/5] Backed up original config"

# Create the agents JSON array (all 4 agents)
AGENTS_JSON=$(cat <<EOF
[
  {
    "id": "orca",
    "name": "OrcaBot",
    "workspace": "$OPENCLAW_DIR/workspace-orca",
    "model": "anthropic/claude-sonnet-4-5",
    "identity": { "name": "OrcaBot" },
    "groupChat": { "mentionPatterns": ["@orca", "@OrcaBot"] },
    "subagents": { "allowAgents": ["design", "code", "test"] }
  },
  {
    "id": "design",
    "name": "DesignBot",
    "workspace": "$OPENCLAW_DIR/workspace-design",
    "model": "anthropic/claude-opus-4-5",
    "identity": { "name": "DesignBot" }
  },
  {
    "id": "code",
    "name": "CodeBot",
    "workspace": "$OPENCLAW_DIR/workspace-code",
    "model": "anthropic/claude-opus-4-5",
    "identity": { "name": "CodeBot" }
  },
  {
    "id": "test",
    "name": "TestBot",
    "workspace": "$OPENCLAW_DIR/workspace-test",
    "model": "anthropic/claude-sonnet-4-5",
    "identity": { "name": "TestBot" }
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
# 1. Add orca agent to agents.list
# 2. Add binding to bindings array
# 3. Add account to channels.telegram.accounts

jq --argjson agents "$AGENTS_JSON" \
   --argjson binding "$BINDING_JSON" \
   --argjson account "$ACCOUNT_JSON" \
   --arg account_name "$ACCOUNT_NAME" \
   '
   # === Required Settings ===
   # Ensure agents.defaults exists
   .agents.defaults = (if .agents.defaults then .agents.defaults else {} end)
   # Ensure agents.defaults.subagents exists
   | .agents.defaults.subagents = (if .agents.defaults.subagents then .agents.defaults.subagents else {} end)
   # Set subagents.maxConcurrent to at least 8
   | .agents.defaults.subagents.maxConcurrent = (if (.agents.defaults.subagents.maxConcurrent // 0) < 8 then 8 else .agents.defaults.subagents.maxConcurrent end)

   # Ensure channels.telegram exists
   | .channels = (if .channels then .channels else {} end)
   | .channels.telegram = (if .channels.telegram then .channels.telegram else {} end)
   # Enable telegram channel
   | .channels.telegram.enabled = true
   # Set groupPolicy to allowlist
   | .channels.telegram.groupPolicy = "allowlist"

   # Ensure plugins.entries exists
   | .plugins = (if .plugins then .plugins else {} end)
   | .plugins.entries = (if .plugins.entries then .plugins.entries else {} end)
   | .plugins.entries.telegram = (if .plugins.entries.telegram then .plugins.entries.telegram else {} end)
   # Enable telegram plugin
   | .plugins.entries.telegram.enabled = true

   # === ClawCrew Agents (orca, design, code, test) ===
   # Ensure agents.list exists
   | .agents.list = (if .agents.list then .agents.list else [] end)
   # Remove existing ClawCrew agents if any
   | .agents.list = [.agents.list[] | select(.id | IN("orca", "design", "code", "test") | not)]
   # Add all ClawCrew agents
   | .agents.list += $agents

   # === Bindings (only orca needs binding for Telegram) ===
   # Initialize bindings if not exists
   | .bindings = (if .bindings then .bindings else [] end)
   # Remove existing orca binding if any
   | .bindings = [.bindings[] | select(.agentId != "orca")]
   # Add new binding
   | .bindings += [$binding]

   # === Telegram Account ===
   # Ensure channels.telegram.accounts exists
   | .channels.telegram.accounts = (if .channels.telegram.accounts then .channels.telegram.accounts else {} end)
   # Remove any existing account using the same bot token
   | .channels.telegram.accounts = (.channels.telegram.accounts | with_entries(select(.value.botToken != $account.botToken)))
   # Add account
   | .channels.telegram.accounts[$account_name] = $account
   ' "$OPENCLAW_CONFIG" > "$OPENCLAW_CONFIG.tmp" && mv "$OPENCLAW_CONFIG.tmp" "$OPENCLAW_CONFIG"

echo "[2/5] Updated openclaw.json with required settings"

echo "[3/5] Added ClawCrew agents (orca, design, code, test) and Telegram binding"

# Copy workspace folders and bin
echo "[4/5] Copying files..."

for workspace in workspace-orca workspace-design workspace-code workspace-test; do
    if [ -d "$SCRIPT_DIR/$workspace" ]; then
        cp -r "$SCRIPT_DIR/$workspace" "$OPENCLAW_DIR/"
        echo "  Copied $workspace"
    else
        echo "  Warning: $workspace not found in $SCRIPT_DIR"
    fi
done

# Copy bin folder
if [ -d "$SCRIPT_DIR/bin" ]; then
    cp -r "$SCRIPT_DIR/bin" "$OPENCLAW_DIR/"
    chmod +x "$OPENCLAW_DIR/bin/"*.py 2>/dev/null
    echo "  Copied bin/"
fi

# Create artifacts folder
mkdir -p "$OPENCLAW_DIR/artifacts"
echo "  Created artifacts/"

# Install Python dependencies
echo "  Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install --quiet typer 2>/dev/null || pip3 install typer
    echo "  Installed typer"
elif command -v pip &> /dev/null; then
    pip install --quiet typer 2>/dev/null || pip install typer
    echo "  Installed typer"
else
    echo "  ⚠️  pip not found. Please install manually: pip install typer"
fi

# Verify settings
echo "[5/5] Verifying configuration..."
VERIFY_ERRORS=0

VERIFY_SUBAGENT=$(jq -r '.agents.defaults.subagents.maxConcurrent' "$OPENCLAW_CONFIG")
if [ "$VERIFY_SUBAGENT" -ge 8 ]; then
    echo "  ✓  subagents.maxConcurrent = $VERIFY_SUBAGENT"
else
    echo "  ✗  subagents.maxConcurrent = $VERIFY_SUBAGENT (expected >= 8)"
    VERIFY_ERRORS=$((VERIFY_ERRORS + 1))
fi

VERIFY_TG=$(jq -r '.channels.telegram.enabled' "$OPENCLAW_CONFIG")
if [ "$VERIFY_TG" = "true" ]; then
    echo "  ✓  telegram.enabled = true"
else
    echo "  ✗  telegram.enabled = $VERIFY_TG"
    VERIFY_ERRORS=$((VERIFY_ERRORS + 1))
fi

VERIFY_AGENTS=$(jq -r '.agents.list | map(select(.id | IN("orca", "design", "code", "test"))) | length' "$OPENCLAW_CONFIG")
if [ "$VERIFY_AGENTS" -eq 4 ]; then
    echo "  ✓  All ClawCrew agents added (orca, design, code, test)"
else
    echo "  ✗  Expected 4 ClawCrew agents, found $VERIFY_AGENTS"
    VERIFY_ERRORS=$((VERIFY_ERRORS + 1))
fi

VERIFY_BINDING=$(jq -r '.bindings | map(select(.agentId == "orca")) | length' "$OPENCLAW_CONFIG")
if [ "$VERIFY_BINDING" -ge 1 ]; then
    echo "  ✓  OrcaBot Telegram binding configured"
else
    echo "  ✗  OrcaBot Telegram binding missing"
    VERIFY_ERRORS=$((VERIFY_ERRORS + 1))
fi

if [ $VERIFY_ERRORS -gt 0 ]; then
    echo ""
    echo "⚠️  Setup completed with $VERIFY_ERRORS warning(s). Please check the config manually."
else
    echo ""
    echo "✓  All settings verified successfully!"
fi

echo ""
echo "================================================"
echo "  ClawCrew is ready!"
echo "================================================"
echo ""

# Restart OpenClaw gateway
echo "Restarting OpenClaw gateway..."
if command -v openclaw &> /dev/null; then
    openclaw gateway restart && echo "  ✓  Gateway restarted"
else
    echo "  ⚠️  openclaw command not found. Please restart manually:"
    echo "     openclaw gateway restart"
fi

echo ""
echo "Try it out:"
echo "  Send a message in your Telegram group:"
echo "  'Create a Python function to validate email addresses'"
echo ""
echo "Installed at $OPENCLAW_DIR/:"
echo "  workspace-orca/    — Orchestrator"
echo "  workspace-design/  — Design agent"
echo "  workspace-code/    — Code agent"
echo "  workspace-test/    — Test agent"
echo "  bin/               — CLI tool"
echo "  artifacts/         — Task outputs"
echo ""
echo "Config backup saved. To revert:"
echo "  cp $OPENCLAW_CONFIG.backup.* $OPENCLAW_CONFIG"
echo ""
