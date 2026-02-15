#!/bin/bash
# ClawCrew Dashboard Launcher
# Starts both FastAPI backend and Streamlit frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🦞 ClawCrew Dashboard${NC}"
echo "================================"

# Check if dependencies are installed
check_deps() {
    python3 -c "import streamlit, fastapi, uvicorn" 2>/dev/null
    return $?
}

# Install dependencies if needed
if ! check_deps; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $API_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI backend
echo -e "${GREEN}Starting API server on http://localhost:8000${NC}"
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API to be ready
sleep 2

# Start Streamlit frontend
echo -e "${GREEN}Starting Dashboard on http://localhost:8501${NC}"
streamlit run dashboard.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!

echo ""
echo -e "${GREEN}✅ Dashboard is running!${NC}"
echo ""
echo "  📊 Dashboard:  http://localhost:8501"
echo "  🔌 API:        http://localhost:8000"
echo "  📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

# Wait for either process to exit
wait
