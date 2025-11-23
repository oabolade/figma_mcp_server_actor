# Quick Start: LLM API Key Setup

## ✅ Current Status

I've detected you already have an **Anthropic API key** configured! However, your `LLM_PROVIDER` is set to `openai`. 

## 🚀 Quick Fix (Option 1: Use Anthropic)

To use your existing Anthropic API key, update the `.env` file:

```bash
cd startup-intelligence-agent
nano .env
```

Change this line:
```env
LLM_PROVIDER=openai
```

To:
```env
LLM_PROVIDER=anthropic
```

And optionally update the model:
```env
LLM_MODEL=claude-3-opus-20240229
# or for cost savings:
# LLM_MODEL=claude-3-sonnet-20240229
# LLM_MODEL=claude-3-haiku-20240307
```

Then verify:
```bash
python3 verify_config.py
```

## 🔑 Quick Setup (Option 2: Get OpenAI Key)

If you prefer OpenAI:

1. **Get OpenAI API Key:**
   - Go to: https://platform.openai.com/api-keys
   - Sign in or create account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. **Update .env file:**
   ```bash
   cd startup-intelligence-agent
   nano .env
   ```

3. **Add your OpenAI key:**
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4-turbo-preview
   ```

4. **Verify:**
   ```bash
   python3 verify_config.py
   ```

## 📋 What You Need

**Minimum Requirement:** One API key from either provider:
- ✅ **OpenAI** (`OPENAI_API_KEY`) - OR
- ✅ **Anthropic** (`ANTHROPIC_API_KEY`)

**Provider Setting:**
- `LLM_PROVIDER=openai` - Use OpenAI
- `LLM_PROVIDER=anthropic` - Use Anthropic

## ✅ Test Your Configuration

After configuring, test it:

```bash
cd startup-intelligence-agent/backend/src
source ../venv/bin/activate

python3 << 'PYEOF'
import asyncio
from llm.client import LLMClient
from config.settings import settings

async def test():
    if not settings.LLM_API_KEY:
        print("⚠ No API key configured")
        return
    
    print(f"Testing {settings.LLM_PROVIDER} with {settings.LLM_MODEL}...")
    client = LLMClient(
        provider=settings.LLM_PROVIDER,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY
    )
    
    try:
        response = await client.complete("Say 'Hello!' in one word.")
        print(f"✓ Response: {response}")
        print("\n✅ LLM API key is working!")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.close()

asyncio.run(test())
PYEOF
```

## 💰 Cost Comparison (Approximate)

| Provider | Model | Cost per Run* |
|----------|-------|---------------|
| OpenAI | GPT-4 Turbo | ~$0.10-0.20 |
| OpenAI | GPT-3.5 Turbo | ~$0.01-0.02 |
| Anthropic | Claude 3 Opus | ~$0.15-0.30 |
| Anthropic | Claude 3 Sonnet | ~$0.03-0.06 |
| Anthropic | Claude 3 Haiku | ~$0.01-0.02 |

*Typical analysis + summarization workflow

**Recommendation for testing:** Use GPT-3.5 Turbo or Claude 3 Haiku for cost-effective testing.

## 📚 Full Documentation

See `LLM_API_SETUP.md` for complete setup instructions including:
- Detailed API key retrieval steps
- Security best practices
- Troubleshooting guide
- Advanced configuration

## ✅ Next Steps After Configuration

Once your API key is working:

1. **Test all agents:**
   ```bash
   python3 test_all_agents.py
   ```

2. **Test full workflow:**
   ```bash
   python3 test_orchestrator.py
   ```

3. **Start the API server:**
   ```bash
   cd backend/src
   python3 main.py
   ```

---

**Need help?** Check `LLM_API_SETUP.md` for detailed troubleshooting!

