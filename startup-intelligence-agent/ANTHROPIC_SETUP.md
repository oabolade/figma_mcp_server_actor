# Anthropic API Key Setup - Quick Guide

## 🎯 Current Configuration

Your system is now configured to use **Anthropic Claude**. 

**Configuration Status:**
- ✅ LLM Provider: `anthropic`
- ✅ Model: `claude-3-sonnet-20240229` (cost-effective option)
- ⏳ Waiting for API key

## 📝 Next Steps: Get Your Anthropic API Key

### Step 1: Create Account / Sign In
1. Go to: **https://console.anthropic.com/**
2. Sign in or create a new account

### Step 2: Navigate to API Keys
1. Once logged in, go to the **API Keys** section
2. Click **"Create Key"** or **"Get API Key"**

### Step 3: Create New Key
1. Give it a name (e.g., "Startup Intelligence Agent")
2. Click **"Create Key"**
3. **IMPORTANT:** Copy the key immediately - it starts with `sk-ant-` and won't be shown again!

### Step 4: Add Key to .env File

**Option A: Edit manually**
```bash
cd startup-intelligence-agent
nano .env
# or
vim .env
# or
code .env  # VS Code
```

Find this line:
```env
ANTHROPIC_API_KEY=
```

Replace it with your actual key:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Option B: Quick command (replace YOUR_KEY with your actual key)**
```bash
cd startup-intelligence-agent
sed -i '' 's/^ANTHROPIC_API_KEY=$/ANTHROPIC_API_KEY=sk-ant-your-actual-key-here/' .env
```

**⚠️ Security Note:** Never commit your `.env` file to git (it's already in `.gitignore`)

### Step 5: Verify Configuration

After adding your API key, verify it works:

```bash
cd startup-intelligence-agent
python3 verify_config.py
```

You should see:
```
✓ LLM API key is configured!
```

### Step 6: Test LLM Connection

Test that your API key works:

```bash
cd startup-intelligence-agent/backend/src
source ../venv/bin/activate

python3 << 'PYEOF'
import asyncio
from llm.client import LLMClient
from config.settings import settings

async def test():
    if not settings.LLM_API_KEY:
        print("⚠ No API key configured yet")
        return
    
    print(f"Testing {settings.LLM_PROVIDER} with {settings.LLM_MODEL}...")
    client = LLMClient(
        provider=settings.LLM_PROVIDER,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY
    )
    
    try:
        response = await client.complete("Say 'Hello, Startup Intelligence!' in one sentence.")
        print(f"\n✓ LLM Response: {response}")
        print("\n✅ Your Anthropic API key is working correctly!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\n⚠ API key may be incorrect. Check your .env file.")
        elif "403" in str(e) or "Forbidden" in str(e):
            print("\n⚠ API access may not be approved yet. Check Anthropic console.")
    finally:
        await client.close()

asyncio.run(test())
PYEOF
```

## 🎛️ Model Options

Your `.env` file is currently set to use **Claude 3 Sonnet**, which is a good balance of cost and quality.

### Available Anthropic Models:

| Model | Use Case | Cost* | Current Setting |
|-------|----------|-------|-----------------|
| `claude-3-opus-20240229` | Best quality, most expensive | Highest | No |
| `claude-3-sonnet-20240229` | Balanced quality/cost | Medium | ✅ **Yes** |
| `claude-3-haiku-20240307` | Fastest, cheapest | Lowest | No |

*Relative cost per API call

To change models, edit `.env`:
```env
LLM_MODEL=claude-3-opus-20240229  # Best quality
# or
LLM_MODEL=claude-3-sonnet-20240229  # Balanced (current)
# or
LLM_MODEL=claude-3-haiku-20240307  # Fastest/cheapest
```

**Recommendation:** Start with Sonnet for testing, then switch to Haiku for cost savings or Opus for best quality.

## 💰 Cost Estimates

For a typical workflow run (analysis + summarization):

- **Claude 3 Opus:** ~$0.15-0.30 per run
- **Claude 3 Sonnet:** ~$0.03-0.06 per run (current setting)
- **Claude 3 Haiku:** ~$0.01-0.02 per run

**Tip:** Use Sonnet for initial testing, then switch to Haiku once you're confident everything works.

## 🔐 Security Best Practices

1. ✅ Never commit `.env` file (already in `.gitignore`)
2. ✅ Never share API keys in public forums/issues
3. ✅ Rotate keys periodically
4. ✅ Set up billing alerts in Anthropic console
5. ✅ Use separate keys for dev/prod environments

## ✅ After Configuration

Once your API key is set and verified:

1. **Test all agents:**
   ```bash
   cd startup-intelligence-agent
   python3 test_all_agents.py
   ```

2. **Test orchestrator workflow:**
   ```bash
   python3 test_orchestrator.py
   ```

3. **Start the API server:**
   ```bash
   cd backend/src
   python3 main.py
   ```

## 🆘 Troubleshooting

### Issue: "401 Unauthorized"
- **Solution:** Check that your API key is correct in `.env`
- Verify key starts with `sk-ant-`
- Make sure there are no extra spaces

### Issue: "403 Forbidden" 
- **Solution:** Your Anthropic account may need API access approval
- Check Anthropic console for access status
- Contact Anthropic support if needed

### Issue: "Rate limit exceeded"
- **Solution:** Add delays between requests or use Haiku model
- Check Anthropic console for rate limits

### Issue: API key not detected
- **Solution:** 
  1. Verify `.env` file exists in `startup-intelligence-agent/` directory
  2. Check that `ANTHROPIC_API_KEY` line is not commented out
  3. Run `python3 verify_config.py` to check

## 📚 Resources

- **Anthropic Console:** https://console.anthropic.com/
- **Anthropic Docs:** https://docs.anthropic.com/
- **API Status:** https://status.anthropic.com/
- **Support:** https://support.anthropic.com/

---

**Ready?** Get your API key from https://console.anthropic.com/ and add it to your `.env` file! 🚀

