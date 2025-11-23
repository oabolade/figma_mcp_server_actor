#!/bin/bash
# Start all services: Data Collector Agents + Main Server

echo "=== Starting Startup Intelligence System ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Data Collector Agents
echo "📦 Starting Data Collector Agents..."
cd "$(dirname "$0")/data-collector-agents"
docker-compose up -d

echo ""
echo "⏳ Waiting for agents to be ready..."
sleep 5

# Test agent health
echo ""
echo "🔍 Testing agent health..."
./../tests/test_data_collectors.sh || true

echo ""
echo "=== Data Collector Agents Status ==="
docker-compose ps

echo ""
echo "=== Starting Main Server ==="
echo ""
echo "Server will start in the background..."
echo "Logs will be written to: /tmp/server.log"
echo ""

cd ../startup-intelligence-agent/backend/src

# Activate virtual environment
if [ -f "../venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠️  Virtual environment not found at ../venv/bin/activate"
    echo "   Attempting to run without venv (may fail if dependencies not installed)"
fi

# Check if server is already running
if lsof -i :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8080 is already in use!"
    echo "   Stopping existing server..."
    lsof -ti :8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start server in background
python3 main.py > /tmp/server.log 2>&1 &
SERVER_PID=$!

echo "✅ Server started (PID: $SERVER_PID)"
echo ""
echo "📋 Services:"
echo "  • News Scraper:     http://localhost:3001"
echo "  • Startup API:      http://localhost:3002"
echo "  • GitHub Monitor:   http://localhost:3003"
echo "  • Main Server:      http://localhost:8080"
echo "  • Frontend UI:      http://localhost:8080/"
echo ""
echo "📊 Check server logs:"
echo "  tail -f /tmp/server.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop_services.sh"
echo ""

# Wait a moment and test server
sleep 3
echo "🔍 Testing main server..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Main server is responding!"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || true
else
    echo "⏳ Server is starting... check logs: tail -f /tmp/server.log"
fi

echo ""
echo "✨ All services starting! Check the URLs above."

