#!/bin/bash
# ClawCrew Dashboard (Reflex) Launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🦞 ClawCrew Dashboard (Reflex)${NC}"
echo "================================"

# Check if reflex is installed
if ! python3 -c "import reflex" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Initialize reflex if needed
if [ ! -d ".web" ]; then
    echo -e "${YELLOW}Initializing Reflex...${NC}"
    reflex init
fi

echo ""
echo -e "${GREEN}Starting Dashboard...${NC}"
echo ""
echo "  📊 Dashboard:  http://localhost:3000"
echo "  🔌 Backend:    http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Run reflex
reflex run
