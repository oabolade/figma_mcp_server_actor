#!/usr/bin/env python3
"""Verify E2B Template Access - Test which templates your account can access."""
import asyncio
import sys
import logging
import httpx
from pathlib import Path
from typing import Tuple

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_template_access_via_api(template: str, api_key: str) -> Tuple[bool, str]:
    """
    Test if a specific template is accessible by attempting to create a sandbox via E2B API.
    
    Returns:
        (success: bool, error_message: str)
    """
    headers = {
        "X-API-Key": api_key.strip(),
        "Content-Type": "application/json"
    }
    
    # E2B API endpoint for creating sandboxes
    url = "https://api.e2b.app/sandboxes"
    
    # E2B API expects "templateID" not "template"
    payload = {
        "templateID": template
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 201:
                # Sandbox created successfully
                data = response.json()
                sandbox_id = data.get("sandboxID", "unknown")
                
                # Immediately close the sandbox to avoid charges
                if sandbox_id != "unknown":
                    try:
                        close_url = f"{url}/{sandbox_id}"
                        await client.delete(close_url, headers=headers)
                    except Exception:
                        pass  # Ignore errors when closing
                
                return True, f"✅ Template '{template}' is accessible (sandbox ID: {sandbox_id})"
            
            elif response.status_code == 403:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("message", response.text)
                return False, f"❌ Template '{template}' NOT accessible (403 Forbidden): {error_msg}"
            
            elif response.status_code == 401:
                return False, f"❌ API key invalid (401 Unauthorized)"
            
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("message", response.text)
                return False, f"⚠️  Template '{template}' failed (HTTP {response.status_code}): {error_msg}"
                
    except httpx.RequestError as e:
        return False, f"⚠️  Network error testing template '{template}': {str(e)}"
    except Exception as e:
        return False, f"⚠️  Error testing template '{template}': {str(e)}"


async def test_template_access_via_sdk(template: str, api_key: str) -> Tuple[bool, str]:
    """
    Test if a specific template is accessible using E2B SDK.
    
    Returns:
        (success: bool, error_message: str)
    """
    try:
        from sandbox_integration.sandbox_manager import SandboxManager
        
        manager = SandboxManager(api_key=api_key)
        sandbox = await manager.create_sandbox(template=template, fallback_templates=[])
        
        # If we get here, template is accessible
        sandbox_id = sandbox.sandbox_id
        await manager.close()
        
        return True, f"✅ Template '{template}' is accessible (sandbox ID: {sandbox_id})"
        
    except ImportError:
        # SDK not available, fall back to API method
        return None, "SDK not available"
    except Exception as e:
        error_msg = str(e)
        
        # Check for specific error types
        if "403" in error_msg or "does not have access" in error_msg.lower():
            return False, f"❌ Template '{template}' NOT accessible (403 Forbidden)"
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return False, f"❌ API key invalid (401 Unauthorized)"
        else:
            return False, f"⚠️  Template '{template}' failed: {error_msg}"


async def test_template_access(template: str, api_key: str) -> Tuple[bool, str]:
    """
    Test template access, trying SDK first, then falling back to API.
    """
    # Try SDK first if available
    result = await test_template_access_via_sdk(template, api_key)
    if result[0] is not None:
        return result
    
    # Fall back to API method
    return await test_template_access_via_api(template, api_key)


async def verify_templates():
    """Verify which E2B templates are accessible."""
    print("=" * 70)
    print("E2B Template Access Verification")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = settings.E2B_API_KEY
    if not api_key or not api_key.strip():
        print("❌ E2B_API_KEY is not configured!")
        print()
        print("To fix this:")
        print("  1. Get your API key from: https://e2b.dev/docs/api-key")
        print("  2. Add to .env file:")
        print("     E2B_API_KEY=your-api-key-here")
        print()
        sys.exit(1)
    
    print(f"✅ E2B API key found (length: {len(api_key.strip())} chars)")
    print()
    
    # Get configured template
    configured_template = settings.E2B_TEMPLATE
    print(f"📋 Configured template (E2B_TEMPLATE): {configured_template}")
    print()
    
    # List of templates to test
    templates_to_test = [
        configured_template,  # Test configured template first
        "base",
        "ubuntu",
        "python3",
        "nodejs",
        "go",
        "rust",
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_templates = []
    for t in templates_to_test:
        if t not in seen:
            seen.add(t)
            unique_templates.append(t)
    
    print("🧪 Testing template access...")
    print()
    print("-" * 70)
    
    results = {}
    
    for template in unique_templates:
        print(f"Testing template: {template}")
        success, message = await test_template_access(template, api_key)
        results[template] = (success, message)
        print(f"  {message}")
        print()
        
        # Small delay between tests to avoid rate limiting
        await asyncio.sleep(1)
    
    print("-" * 70)
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    
    # Count accessible templates
    accessible = [t for t, (s, _) in results.items() if s]
    inaccessible = [t for t, (s, _) in results.items() if not s]
    
    if accessible:
        print(f"✅ Accessible templates ({len(accessible)}):")
        for template in accessible:
            print(f"   • {template}")
        print()
    else:
        print("❌ No accessible templates found!")
        print()
        print("This could indicate:")
        print("  1. Your E2B account doesn't have access to these templates")
        print("  2. Your API key is invalid or expired")
        print("  3. Your account needs to be upgraded or templates need to be enabled")
        print()
        print("💡 Next steps:")
        print("  • Check your E2B dashboard: https://e2b.dev/dashboard")
        print("  • Contact E2B support: https://e2b.dev/docs/support")
        print("  • Verify your API key: python scripts/verify_e2b_key.py")
        print()
        sys.exit(1)
    
    if inaccessible:
        print(f"❌ Inaccessible templates ({len(inaccessible)}):")
        for template in inaccessible:
            print(f"   • {template}")
        print()
    
    # Check if configured template is accessible
    if configured_template in accessible:
        print(f"✅ Your configured template '{configured_template}' is accessible!")
        print()
        print("💡 You can proceed with deployment:")
        print("   python scripts/deploy_to_e2b.py")
        print()
    else:
        print(f"⚠️  Your configured template '{configured_template}' is NOT accessible!")
        print()
        if accessible:
            recommended = accessible[0]
            print(f"💡 Recommendation: Use template '{recommended}' instead")
            print()
            print("Update your .env file:")
            print(f"   E2B_TEMPLATE={recommended}")
            print()
            print("Or the system will automatically use it as a fallback.")
            print()
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(verify_templates())
    except KeyboardInterrupt:
        print()
        print("⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during template verification: {e}")
        sys.exit(1)

