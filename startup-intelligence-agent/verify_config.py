#!/usr/bin/env python3
"""Verify LLM API key configuration."""
import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings

def main():
    print("=" * 70)
    print("LLM Configuration Verification")
    print("=" * 70)
    print()
    
    # Check provider
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    print()
    
    # Check API keys
    openai_key = settings.OPENAI_API_KEY
    anthropic_key = settings.ANTHROPIC_API_KEY
    active_key = settings.LLM_API_KEY
    
    print("API Key Status:")
    print(f"  OpenAI API Key: {'✓ Set' if openai_key else '✗ Not set'}")
    if openai_key:
        print(f"    Key preview: {openai_key[:10]}...{openai_key[-4:]}")
    
    print(f"  Anthropic API Key: {'✓ Set' if anthropic_key else '✗ Not set'}")
    if anthropic_key:
        print(f"    Key preview: {anthropic_key[:10]}...{anthropic_key[-4:]}")
    
    print(f"  Active API Key: {'✓ Set' if active_key else '✗ Not set'}")
    print()
    
    # Status
    if active_key:
        print("=" * 70)
        print("✓ LLM API key is configured!")
        print("=" * 70)
        print()
        print("Your system is ready to use LLM-powered features:")
        print("  • Analysis Agent will use LLM for trend analysis")
        print("  • Summarizer Agent will use LLM for briefing generation")
        print()
        print("Next steps:")
        print("  1. Run: python3 test_all_agents.py")
        print("  2. Start server: python3 backend/src/main.py")
        print()
        return 0
    else:
        print("=" * 70)
        print("⚠ LLM API key not configured")
        print("=" * 70)
        print()
        print("The system will work but use fallback responses instead of LLM.")
        print()
        print("To configure:")
        print("  1. Edit .env file in startup-intelligence-agent/ directory")
        print("  2. Add either OPENAI_API_KEY or ANTHROPIC_API_KEY")
        print("  3. Set LLM_PROVIDER to match (openai or anthropic)")
        print()
        print("Get API keys from:")
        print("  • OpenAI: https://platform.openai.com/api-keys")
        print("  • Anthropic: https://console.anthropic.com/")
        print()
        print("See LLM_API_SETUP.md for detailed instructions.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

