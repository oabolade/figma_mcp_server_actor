#!/usr/bin/env python3
"""Deploy Startup Intelligence Agent to E2B Sandbox."""
import asyncio
import sys
import logging
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from sandbox_integration.client import E2BClient
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Deploy to E2B sandbox."""
    logger.info("=== E2B Sandbox Deployment ===")
    logger.info("")
    
    # Check for E2B API key
    if not settings.E2B_API_KEY:
        logger.error("❌ E2B_API_KEY not configured!")
        logger.error("   Please set E2B_API_KEY environment variable.")
        logger.error("   Get your API key from: https://e2b.dev")
        sys.exit(1)
    
    logger.info(f"✅ E2B API key configured")
    logger.info(f"   Template: {settings.E2B_TEMPLATE} (will try fallbacks if needed)")
    logger.info(f"   Reconnect to existing: {bool(settings.SANDBOX_ID)}")
    logger.info("")
    
    # Create client and deploy
    client = E2BClient()
    
    try:
        logger.info("🚀 Starting deployment...")
        sandbox_url = await client.deploy(
            reconnect_to_existing=bool(settings.SANDBOX_ID)
        )
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Deployment Successful!")
        logger.info("=" * 60)
        logger.info("")
        logger.info(f"🌐 Server URL: https://{sandbox_url}")
        logger.info(f"📊 Health Check: https://{sandbox_url}/health")
        logger.info(f"📋 Briefing: https://{sandbox_url}/briefing")
        logger.info("")
        logger.info("🧪 To test the deployment, run:")
        logger.info(f"   python scripts/test_e2b_deployment.py https://{sandbox_url}")
        logger.info("")
        logger.info("💡 To stop the sandbox, press Ctrl+C")
        logger.info("")
        logger.info("⚠️  Note: E2B sandboxes are ephemeral and will close when:")
        logger.info("   • You press Ctrl+C")
        logger.info("   • The sandbox times out (check E2B dashboard for timeout settings)")
        logger.info("   • The deployment script exits")
        logger.info("")
        
        # Keep sandbox alive
        try:
            await asyncio.Event().wait()  # Wait indefinitely
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Stopping sandbox...")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)
    finally:
        await client.close()
        logger.info("✅ Sandbox closed")


if __name__ == "__main__":
    asyncio.run(main())

