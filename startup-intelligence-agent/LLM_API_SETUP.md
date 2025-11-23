# LLM API Key Setup Guide

This guide will help you configure LLM API keys for the Startup Intelligence Agent system.

## Overview

The system supports two LLM providers:
- **OpenAI** (default): Uses GPT models (e.g., `gpt-4-turbo-preview`)
- **Anthropic**: Uses Claude models (e.g., `claude-3-opus-20240229`)

## Required API Keys

You need **at least one** of the following API keys:
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Anthropic models

## Step 1: Get Your API Keys

### Option A: OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key immediately (it won't be shown again)
5. Save it securely

**Note**: You'll need billing enabled on your OpenAI account to use the API.

### Option B: Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Click "Create Key"
5. Copy the key immediately
6. Save it securely

**Note**: You'll need API access approved by Anthropic.

## Step 2: Configure Environment Variables

### Quick Setup Script

Run this command to set up your .env file:

```bash
cd startup-intelligence-agent
cp .env.example .env
```

Then edit the `.env` file and add your API keys:

```bash
# Edit .env file (use your preferred editor)
nano .env
# or
vim .env
# or
code .env  # VS Code
```

### Manual Setup

Create or edit `.env` file in the `startup-intelligence-agent` directory:

```env
# LLM Configuration
# Choose one provider: "openai" or "anthropic"
LLM_PROVIDER=openai

# Model selection based on provider
# OpenAI models: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
# Anthropic models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
LLM_MODEL=gpt-4-turbo-preview

# API Keys - Add at least one
OPENAI_API_KEY=sk-your-openai-api-key-here
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Docker MCP Hub Agent URLs (optional - defaults shown)
NEWS_SCRAPER_URL=http://localhost:3001
STARTUP_API_URL=http://localhost:3002
GITHUB_MONITOR_URL=http://localhost:3003

# Database (optional - defaults shown)
DATABASE_PATH=./storage/intelligence.db

# Server Configuration (optional - defaults shown)
PORT=8080
HOST=0.0.0.0
```

## Step 3: Verify Configuration

After setting up your API keys, verify the configuration:

```bash
cd backend/src
source ../venv/bin/activate
python3 << 'PYEOF'
from config.settings import settings

print("LLM Configuration:")
print(f"  Provider: {settings.LLM_PROVIDER}")
print(f"  Model: {settings.LLM_MODEL}")
print(f"  OpenAI API Key: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Not set'}")
print(f"  Anthropic API Key: {'✓ Set' if settings.ANTHROPIC_API_KEY else '✗ Not set'}")
print(f"  Active API Key: {'✓ Set' if settings.LLM_API_KEY else '✗ Not set'}")

if settings.LLM_API_KEY:
    print("\n✓ LLM API key is configured! You can now use LLM-powered features.")
else:
    print("\n⚠ LLM API key not configured. The system will use fallback responses.")
    print("  Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file to enable LLM features.")
PYEOF
```

## Step 4: Test LLM Integration

Test that your API key works:

```bash
cd backend/src
source ../venv/bin/activate
python3 << 'PYEOF'
import asyncio
from llm.client import LLMClient
from config.settings import settings

async def test():
    if not settings.LLM_API_KEY:
        print("⚠ No LLM API key configured. Skipping test.")
        return
    
    print("Testing LLM client...")
    client = LLMClient(
        provider=settings.LLM_PROVIDER,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY
    )
    
    try:
        response = await client.complete("Say 'Hello, Startup Intelligence!'")
        print(f"✓ LLM Response: {response[:100]}...")
        print("\n✓ LLM API key is working correctly!")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\n⚠ Check that your API key is correct and has billing enabled.")
    finally:
        await client.close()

asyncio.run(test())
PYEOF
```

## Cost Considerations

### OpenAI Pricing (approximate)
- **GPT-4 Turbo**: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- **GPT-3.5 Turbo**: Much cheaper, ~$0.001 per 1K tokens
- **Typical workflow**: Analysis + Summarization ≈ $0.05-0.20 per run

### Anthropic Pricing (approximate)
- **Claude 3 Opus**: ~$0.015 per 1K input tokens, ~$0.075 per 1K output tokens
- **Claude 3 Sonnet**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Typical workflow**: Analysis + Summarization ≈ $0.10-0.30 per run

**Recommendation**: Start with OpenAI GPT-3.5 Turbo or Claude 3 Haiku for cost-effective testing.

## Security Best Practices

1. **Never commit .env file to git**: The `.env` file is already in `.gitignore`
2. **Use environment variables in production**: Set API keys as environment variables, not in files
3. **Rotate keys regularly**: Change API keys periodically for security
4. **Monitor usage**: Set up billing alerts on your provider's dashboard
5. **Use separate keys for dev/prod**: Different API keys for different environments

## Troubleshooting

### Issue: "LLM API key not configured"
**Solution**: Ensure `.env` file exists in `startup-intelligence-agent/` directory with correct API key.

### Issue: "401 Unauthorized" error
**Solution**: 
- Verify API key is correct (no extra spaces)
- Check that billing is enabled on your account
- For Anthropic, ensure API access is approved

### Issue: "Rate limit exceeded"
**Solution**: 
- Add delays between requests
- Use a model with higher rate limits
- Implement retry logic with exponential backoff

### Issue: "Invalid JSON response"
**Solution**: This is handled gracefully - check logs for details. The system falls back to empty results.

## Next Steps

Once API keys are configured:
1. ✅ Test the configuration (see Step 4 above)
2. ✅ Run full workflow test: `python3 test_all_agents.py`
3. ✅ Start the API server: `python3 backend/src/main.py`
4. ✅ Test the orchestrator workflow end-to-end

## Support

- **OpenAI Support**: https://help.openai.com/
- **Anthropic Support**: https://support.anthropic.com/
- **Project Issues**: Check the main README for troubleshooting

---

**Ready to configure?** Follow the steps above to set up your LLM API keys! 🚀

