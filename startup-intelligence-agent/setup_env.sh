#!/bin/bash
# Setup script for .env file configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "LLM API Key Configuration Setup"
echo "======================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠ .env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping .env creation. Edit .env manually to add your API keys."
        exit 0
    fi
fi

# Copy .env.example to .env
if [ -f .env.example ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
else
    echo "✗ .env.example not found. Creating .env from scratch..."
    cat > .env << 'EOF'
# LLM Configuration
# Choose one provider: "openai" or "anthropic"
LLM_PROVIDER=openai

# Model selection based on provider
# OpenAI models: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
# Anthropic models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
LLM_MODEL=gpt-4-turbo-preview

# API Keys - Add at least one
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Docker MCP Hub Agent URLs (optional - defaults shown)
NEWS_SCRAPER_URL=http://localhost:3001
STARTUP_API_URL=http://localhost:3002
GITHUB_MONITOR_URL=http://localhost:3003

# Database (optional - defaults shown)
DATABASE_PATH=./storage/intelligence.db

# Server Configuration (optional - defaults shown)
PORT=8080
HOST=0.0.0.0

# E2B Sandbox (optional)
E2B_API_KEY=
SANDBOX_ID=
EOF
    echo "✓ Created .env file"
fi

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Edit the .env file and add your API keys:"
echo "   nano .env"
echo "   # or"
echo "   vim .env"
echo "   # or"
echo "   code .env"
echo ""
echo "2. Add your API keys:"
echo "   - For OpenAI: Set OPENAI_API_KEY=sk-your-key-here"
echo "   - For Anthropic: Set ANTHROPIC_API_KEY=sk-ant-your-key-here"
echo ""
echo "3. Get API keys from:"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - Anthropic: https://console.anthropic.com/"
echo ""
echo "4. Verify configuration:"
echo "   python3 verify_config.py"
echo ""
echo "5. Test LLM integration:"
echo "   See LLM_API_SETUP.md for detailed instructions"
echo ""
echo "======================================"
echo "✓ Setup complete!"
echo "======================================"

