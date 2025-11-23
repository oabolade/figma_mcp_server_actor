#!/bin/bash
# Quick test script for E2B deployment

if [ -z "$1" ]; then
    echo "Usage: $0 <sandbox-url>"
    echo "Example: $0 https://sandbox-id.e2b.dev"
    exit 1
fi

SANDBOX_URL="$1"

echo "=== Quick E2B Sandbox Test ==="
echo ""
echo "Testing: $SANDBOX_URL"
echo ""

echo "1. Health Check:"
curl -s "$SANDBOX_URL/health" | jq '.' || echo "❌ Failed"
echo ""

echo "2. System Info:"
curl -s "$SANDBOX_URL/info" | jq '.' || echo "❌ Failed"
echo ""

echo "3. Orchestrator Status:"
curl -s "$SANDBOX_URL/orchestrator/status" | jq '.' || echo "❌ Failed"
echo ""

echo "4. Data Stats:"
curl -s "$SANDBOX_URL/data/stats" | jq '.' || echo "❌ Failed"
echo ""

echo "5. Briefing (may be 404 if no workflow run yet):"
curl -s "$SANDBOX_URL/briefing" | jq '.' || echo "ℹ️  No briefing found (expected)"
echo ""

echo "✅ Quick test complete!"
echo ""
echo "💡 To trigger workflow:"
echo "   curl -X POST \"$SANDBOX_URL/orchestrator/run?days_back=7\""
