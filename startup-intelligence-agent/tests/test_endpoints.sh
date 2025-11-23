#!/bin/bash
# Test script for the Startup Intelligence Agent server endpoints

SERVER_PID=""
SERVER_DIR="backend/src"
VENV_PATH="../venv"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Startup Intelligence Agent - Server Test"
echo "=========================================="
echo ""

# Function to start server
start_server() {
    echo -e "${YELLOW}Starting server...${NC}"
    cd "$SERVER_DIR" || exit 1
    source "$VENV_PATH/bin/activate"
    python3 main.py > /tmp/server.log 2>&1 &
    SERVER_PID=$!
    cd - > /dev/null || exit 1
    echo "Server started (PID: $SERVER_PID)"
    echo "Waiting for server to be ready..."
    sleep 5
    
    # Check if server is running
    if ps -p $SERVER_PID > /dev/null; then
        echo -e "${GREEN}✓ Server is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Server failed to start${NC}"
        echo "Last 20 lines of server log:"
        tail -20 /tmp/server.log
        return 1
    fi
}

# Function to stop server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo ""
        echo -e "${YELLOW}Stopping server (PID: $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null
        sleep 2
        if ps -p $SERVER_PID > /dev/null; then
            kill -9 $SERVER_PID 2>/dev/null
        fi
        echo -e "${GREEN}✓ Server stopped${NC}"
    fi
}

# Trap to ensure server is stopped on exit
trap stop_server EXIT

# Start server
if ! start_server; then
    exit 1
fi

# Test endpoints
echo ""
echo "Testing endpoints..."
echo ""

# Test /health
echo -n "GET /health: "
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8080/health)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ (HTTP $HTTP_CODE)${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""

# Test /info
echo -n "GET /info: "
INFO_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8080/info)
HTTP_CODE=$(echo "$INFO_RESPONSE" | tail -1)
BODY=$(echo "$INFO_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ (HTTP $HTTP_CODE)${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""

# Test /briefing (should return 404)
echo -n "GET /briefing: "
BRIEFING_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8080/briefing)
HTTP_CODE=$(echo "$BRIEFING_RESPONSE" | tail -1)
BODY=$(echo "$BRIEFING_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "404" ]; then
    echo -e "${GREEN}✓ (HTTP $HTTP_CODE - Expected)${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${YELLOW}⚠ (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All endpoint tests completed!${NC}"
echo "=========================================="

