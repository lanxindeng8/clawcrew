---
title: Deployment Procedures
tags: [deploy, ops, onboarding]
updated: 2026-02-18
author: OrcaBot
summary: Deployment runbook for ClawCrew services including Dashboard and MarketVisualizer.
---

# Deployment Procedures

## Infrastructure Overview

| Resource | Value |
|----------|-------|
| Machine | Tailscale IP `100.102.200.46` |
| Reserved Port | 8000 (occupied, do not use) |

## ClawCrew Dashboard

### Ports
- **Web UI**: 3001
- **API Backend**: 8002

### Deployment Steps

1. **Navigate to project directory**
   ```bash
   cd ~/projects/clawcrew
   ```

2. **Ensure dependencies are installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   reflex run
   ```

4. **Verify deployment**
   - Web UI: http://localhost:3001
   - API: http://localhost:8002

### Stopping the Service
```bash
# Find and kill reflex process
pkill -f "reflex run"
```

---

## MarketVisualizer

### Port
- **Web UI**: 8080

### Deployment Steps

1. **Navigate to project directory**
   ```bash
   cd ~/projects/market-visualizer
   ```

2. **Start with correct Python path**
   ```bash
   PYTHONPATH=../../src python run_web.py
   ```

3. **Verify deployment**
   - Web UI: http://localhost:8080

### Environment Notes
- Requires `PYTHONPATH=../../src` to resolve module imports
- Runs as foreground process (use tmux/screen for persistence)

---

## BTC Dive Monitor

### Location
- Script: `scripts/btc_dive_monitor.py`

### Data Source
- Binance US WebSocket (real-time BTC/USDT trades)

### Deployment Steps

1. **Set required environment variables**
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   export TELEGRAM_CHAT_ID="your-chat-id"
   ```

2. **Optional configuration**
   ```bash
   export BTC_DIVE_THRESHOLD="0.7"    # Default: 0.7%
   export BTC_ALERT_COOLDOWN="900"    # Default: 900s (15min)
   ```

3. **Run the monitor**
   ```bash
   python scripts/btc_dive_monitor.py
   ```

### Dependencies
```
websocket-client>=1.6.0
requests>=2.28.0
```

---

## Pre-Deploy Checklist

- [ ] Check port availability (`lsof -i :<port>`)
- [ ] Verify environment variables are set
- [ ] Confirm dependencies installed
- [ ] Test in development before production
- [ ] Remember: Port 8000 is occupied — do not use

## Post-Deploy Verification

- [ ] Service responds on expected port
- [ ] Logs show no errors
- [ ] Key functionality tested
- [ ] Monitoring/alerts configured (if applicable)

## Rollback

If deployment fails:

1. Stop the new service
2. Check logs for errors
3. Restore previous version from git
4. Restart with known-good configuration

---

## Lessons Applied

- Always check port availability before starting services
- Use `PYTHONPATH` for MarketVisualizer module resolution
- BTC monitor auto-reconnects on WebSocket disconnect (exponential backoff)
