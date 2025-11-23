#!/bin/bash
# Stop all services: Data Collector Agents + Main Server

echo "=== Stopping Startup Intelligence System ==="
echo ""

# Stop Data Collector Agents
echo "📦 Stopping Data Collector Agents..."
cd "$(dirname "$0")/data-collector-agents"
docker-compose down

echo ""

# Stop Main Server
echo "🛑 Stopping Main Server..."
if lsof -i :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    SERVER_PID=$(lsof -ti :8080)
    echo "   Found server on port 8080 (PID: $SERVER_PID)"
    kill -9 $SERVER_PID 2>/dev/null || true
    echo "✅ Server stopped"
else
    echo "   No server running on port 8080"
fi

echo ""
echo "✨ All services stopped!"

