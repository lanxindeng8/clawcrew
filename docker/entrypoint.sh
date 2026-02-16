#!/bin/bash
#
# ClawCrew Docker Entrypoint
#
set -e

echo "==============================="
echo "ClawCrew Docker Container"
echo "==============================="

# Check required environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN is required"
    echo "Set it via: docker run -e TELEGRAM_BOT_TOKEN=..."
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "Error: TELEGRAM_CHAT_ID is required"
    echo "Set it via: docker run -e TELEGRAM_CHAT_ID=..."
    exit 1
fi

if [ -z "$TELEGRAM_ALLOWED_USERS" ]; then
    echo "Error: TELEGRAM_ALLOWED_USERS is required"
    echo "Set it via: docker run -e TELEGRAM_ALLOWED_USERS=123456789,987654321"
    exit 1
fi

# Generate ClawCrew config
echo "Generating ClawCrew configuration..."
mkdir -p /root/.clawcrew

cat > /root/.clawcrew/config.toml << EOF
[telegram]
bot_token = "${TELEGRAM_BOT_TOKEN}"
chat_id = "${TELEGRAM_CHAT_ID}"
allowed_users = [${TELEGRAM_ALLOWED_USERS}]
EOF

if [ -n "$GITHUB_TOKEN" ]; then
    cat >> /root/.clawcrew/config.toml << EOF

[github]
token = "${GITHUB_TOKEN}"
EOF
fi

chmod 600 /root/.clawcrew/config.toml
echo "✓ ClawCrew config generated"

# Copy workspaces to ~/.openclaw if not exists
if [ ! -d "/root/.openclaw/workspace-orca" ]; then
    echo "Setting up agent workspaces..."
    cp -r /app/workspace-* /root/.openclaw/
    echo "✓ Workspaces copied"
fi

# Check if OpenClaw config exists
if [ ! -f "/root/.openclaw/openclaw.json" ]; then
    echo ""
    echo "Warning: OpenClaw not configured."
    echo "Mount your ~/.openclaw directory or configure OpenClaw in the container."
    echo ""
fi

# Start dashboard if enabled
if [ "$ENABLE_DASHBOARD" = "true" ]; then
    echo "Starting dashboard..."
    if [ -d "/app/dashboard" ]; then
        cd /app/dashboard && ./run.sh &
        echo "✓ Dashboard started on ports 6000/6001"
    else
        echo "Warning: Dashboard directory not found"
    fi
    cd /app
fi

echo ""
echo "ClawCrew is ready!"
echo ""
echo "Available commands:"
echo "  clawcrew status   - Check system status"
echo "  clawcrew agents   - List agents"
echo "  clawcrew run ...  - Run an agent"
echo "  clawcrew chain .. - Run agent chain"
echo ""

# If command is provided, run it
if [ $# -gt 0 ]; then
    exec "$@"
else
    # Keep container running
    exec tail -f /dev/null
fi
