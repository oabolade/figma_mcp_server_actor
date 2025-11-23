#!/usr/bin/env python3
"""Verify E2B API Key."""
import os
import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings

def verify_api_key():
    """Verify E2B API key configuration."""
    print("=== E2B API Key Verification ===")
    print()
    
    # Check if API key is set
    api_key = settings.E2B_API_KEY
    
    if not api_key:
        print("❌ E2B_API_KEY is not set!")
        print()
        print("To fix this:")
        print("  1. Get your API key from: https://e2b.dev/docs/api-key")
        print("  2. Add to .env file:")
        print("     E2B_API_KEY=your-api-key-here")
        print()
        return False
    
    # Check if API key is empty
    if not api_key.strip():
        print("❌ E2B_API_KEY is set but empty (whitespace only)")
        print()
        print("To fix this:")
        print("  1. Check your .env file for E2B_API_KEY")
        print("  2. Ensure it has a value (no quotes needed)")
        print()
        return False
    
    # Check API key length
    api_key_clean = api_key.strip()
    print(f"✅ E2B_API_KEY is set")
    print(f"   Length: {len(api_key_clean)} characters")
    print(f"   First 10 chars: {api_key_clean[:10]}...")
    print()
    
    if len(api_key_clean) < 20:
        print("⚠️  Warning: API key appears to be too short")
        print("   E2B API keys are typically longer. Please verify your key is correct.")
        print()
    
    # Test API key with curl command
    print("📋 To test your API key manually, run:")
    print(f"   curl -X GET 'https://api.e2b.dev/sandboxes' -H 'X-API-Key: {api_key_clean[:10]}...'")
    print()
    
    # Try to import E2B SDK and test
    try:
        from e2b import Sandbox
        print("✅ E2B SDK is installed")
        print()
        print("💡 To test sandbox creation, run:")
        print("   python scripts/deploy_to_e2b.py")
        print()
        return True
    except ImportError:
        print("⚠️  E2B SDK is not installed")
        print("   Install with: pip install e2b")
        print()
        return False
    except Exception as e:
        print(f"⚠️  Error checking E2B SDK: {e}")
        print()
        return False


if __name__ == "__main__":
    success = verify_api_key()
    sys.exit(0 if success else 1)

