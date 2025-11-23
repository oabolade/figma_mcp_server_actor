#!/usr/bin/env python3
"""Check E2B Sandbox Deployment Status."""
import asyncio
import sys
import logging
import httpx
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_sandbox_status():
    """Check if there are any active sandboxes."""
    print("=" * 70)
    print("E2B Sandbox Deployment Status Check")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = settings.E2B_API_KEY
    if not api_key or not api_key.strip():
        print("❌ E2B_API_KEY is not configured!")
        print()
        sys.exit(1)
    
    print(f"✅ E2B API key found")
    print()
    
    # Check for active sandboxes via API
    headers = {
        "X-API-Key": api_key.strip(),
        "Content-Type": "application/json"
    }
    
    url = "https://api.e2b.app/sandboxes"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                sandboxes = response.json()
                
                # Check if we have any sandboxes
                if isinstance(sandboxes, list):
                    active_count = len(sandboxes)
                    print(f"📊 Active Sandboxes: {active_count}")
                    print()
                    
                    if active_count > 0:
                        print("Active Sandbox Details:")
                        print("-" * 70)
                        for i, sandbox in enumerate(sandboxes[:5], 1):  # Show first 5
                            sandbox_id = sandbox.get("sandboxID", "unknown")
                            template = sandbox.get("templateID", "unknown")
                            created = sandbox.get("createdAt", "unknown")
                            status = sandbox.get("status", "unknown")
                            
                            print(f"{i}. Sandbox ID: {sandbox_id}")
                            print(f"   Template: {template}")
                            print(f"   Status: {status}")
                            print(f"   Created: {created}")
                            print()
                        
                        if active_count > 5:
                            print(f"   ... and {active_count - 5} more sandboxes")
                            print()
                        
                        # Try to check if any sandbox is serving our app
                        print("🔍 Checking if any sandbox is serving the application...")
                        print()
                        
                        for sandbox in sandboxes[:3]:  # Check first 3
                            sandbox_id = sandbox.get("sandboxID", "")
                            if sandbox_id:
                                # Try to construct URL and check health
                                # E2B sandboxes typically have URLs like: {sandbox_id}.runs.apify.net
                                # But we need to check the actual E2B URL format
                                try:
                                    # Try common E2B URL patterns
                                    test_urls = [
                                        f"https://{sandbox_id}.runs.apify.net/health",
                                        f"https://{sandbox_id}.e2b.dev/health",
                                        f"https://api.e2b.app/sandboxes/{sandbox_id}/url",
                                    ]
                                    
                                    for test_url in test_urls:
                                        try:
                                            health_response = await client.get(test_url, timeout=5.0)
                                            if health_response.status_code == 200:
                                                print(f"✅ Found accessible sandbox: {sandbox_id}")
                                                print(f"   Health check URL: {test_url}")
                                                data = health_response.json()
                                                print(f"   Response: {data}")
                                                print()
                                                break
                                        except Exception:
                                            continue
                                except Exception as e:
                                    logger.debug(f"Error checking sandbox {sandbox_id}: {e}")
                    else:
                        print("ℹ️  No active sandboxes found")
                        print()
                        print("💡 This could mean:")
                        print("   • Deployment hasn't been run yet")
                        print("   • Previous sandbox has been closed")
                        print("   • Sandbox expired (E2B sandboxes are ephemeral)")
                        print()
                else:
                    print("⚠️  Unexpected response format from E2B API")
                    print(f"   Response: {sandboxes}")
                    print()
                    
            elif response.status_code == 401:
                print("❌ API key is invalid (401 Unauthorized)")
                print()
                sys.exit(1)
            else:
                print(f"⚠️  Unexpected response from E2B API: {response.status_code}")
                print(f"   Response: {response.text}")
                print()
                
    except httpx.RequestError as e:
        print(f"❌ Network error connecting to E2B API: {e}")
        print()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking sandbox status: {e}")
        sys.exit(1)
    
    print("=" * 70)
    print("Status Check Complete")
    print("=" * 70)
    print()
    print("💡 To deploy or check deployment logs:")
    print("   python scripts/deploy_to_e2b.py")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(check_sandbox_status())
    except KeyboardInterrupt:
        print()
        print("⚠️  Status check interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during status check: {e}")
        sys.exit(1)

