#!/bin/bash
# Helper script to start the server, handling port conflicts and dependencies

PORT=${PORT:-8080}
HOST=${HOST:-127.0.0.1}

echo "=== Starting Startup Intelligence Agent Server ==="
echo ""

# Check if we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    cd "$SCRIPT_DIR/.."
    python3 -m pip install -r requirements.txt
    cd "$SCRIPT_DIR"
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies OK"
fi

echo ""

# Check if port is in use
if lsof -i :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port $PORT is already in use"
    echo ""
    echo "Processes using port $PORT:"
    lsof -i :$PORT
    echo ""
    read -p "Kill existing process and start server? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing processes on port $PORT..."
        lsof -ti :$PORT | xargs kill -9 2>/dev/null
        sleep 2
        echo "✅ Stopped existing processes"
    else
        echo "❌ Aborted. Please stop the process manually or use a different port."
        exit 1
    fi
fi

# Start the server
echo "Starting server on http://$HOST:$PORT..."
python3 main.py
