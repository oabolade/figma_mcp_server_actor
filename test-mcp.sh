#!/bin/bash
# Test script for Figma MCP Server
# Usage: ./test-mcp.sh [host] [port]
# Example: ./test-mcp.sh localhost 8080

HOST=${1:-localhost}
PORT=${2:-8080}
BASE_URL="http://${HOST}:${PORT}"

echo "Testing Figma MCP Server at ${BASE_URL}"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1. Testing health check..."
curl -s "${BASE_URL}/health" | jq '.' || echo "Failed"
echo ""
echo "---"
echo ""

# Test 2: Initialize MCP
echo "2. Initializing MCP protocol..."
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }' | jq '.' || echo "Failed"
echo ""
echo "---"
echo ""

# Test 3: List available tools
echo "3. Listing available tools..."
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' | jq '.' || echo "Failed"
echo ""
echo "---"
echo ""

# Test 4: List available resources
echo "4. Listing available resources..."
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "resources/list",
    "params": {}
  }' | jq '.' || echo "Failed"
echo ""
echo "---"
echo ""

# Test 5: List available prompts
echo "5. Listing available prompts..."
curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "prompts/list",
    "params": {}
  }' | jq '.' || echo "Failed"
echo ""
echo "---"
echo ""

# Test 6: Call a tool (requires Figma file key)
if [ -n "$FIGMA_FILE_KEY" ]; then
  echo "6. Testing analyze_file tool with fileKey: ${FIGMA_FILE_KEY}..."
  curl -s -X POST "${BASE_URL}/mcp" \
    -H "Content-Type: application/json" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 5,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"analyze_file\",
        \"arguments\": {
          \"fileKey\": \"${FIGMA_FILE_KEY}\"
        }
      }
    }" | jq '.' || echo "Failed"
  echo ""
  echo "---"
  echo ""
else
  echo "6. Skipping tool call test (set FIGMA_FILE_KEY env var to test)"
  echo ""
fi

echo "Testing complete!"

