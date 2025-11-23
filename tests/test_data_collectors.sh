#!/bin/bash
# Test script for Data Collector Agents health endpoints

echo "=== Data Collector Agents Health Check ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null | sed 's/^/  /'
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
        if [ -n "$body" ]; then
            echo "$body" | sed 's/^/  /'
        fi
    fi
    echo ""
}

echo "1. News Scraper Agent (Port 3001)"
test_endpoint "News Scraper" "http://localhost:3001/health"

echo "2. Startup API Agent (Port 3002)"
test_endpoint "Startup API" "http://localhost:3002/health"

echo "3. GitHub Monitor Agent (Port 3003)"
test_endpoint "GitHub Monitor" "http://localhost:3003/health"

echo "=== Summary ==="
echo "All agents should return HTTP 200 with status 'ok'"
echo ""
echo "To test individual endpoints:"
echo "  curl http://localhost:3001/health"
echo "  curl http://localhost:3002/health"
echo "  curl http://localhost:3003/health"

