#!/usr/bin/env python3
"""Test E2B Sandbox Deployment - Verify all endpoints and functionality."""
import asyncio
import sys
import logging
import httpx
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2BDeploymentTester:
    """Test E2B sandbox deployment."""
    
    def __init__(self, sandbox_url: str):
        """
        Initialize tester.
        
        Args:
            sandbox_url: E2B sandbox URL (e.g., https://sandbox-id.e2b.dev)
        """
        # Remove https:// if present
        if sandbox_url.startswith("https://"):
            sandbox_url = sandbox_url[8:]
        elif sandbox_url.startswith("http://"):
            sandbox_url = sandbox_url[7:]
        
        self.base_url = f"https://{sandbox_url}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health_endpoint(self) -> bool:
        """Test /health endpoint."""
        logger.info("Testing /health endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Health check passed: {data}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    async def test_info_endpoint(self) -> bool:
        """Test /info endpoint."""
        logger.info("Testing /info endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/info")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Info endpoint working:")
                logger.info(f"   Service: {data.get('service')}")
                logger.info(f"   LLM Provider: {data.get('llm_provider')}")
                logger.info(f"   Database: {data.get('database_path')}")
                return True
            else:
                logger.error(f"❌ Info endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Info endpoint error: {e}")
            return False
    
    async def test_data_collectors(self) -> bool:
        """Test data collector agent connectivity."""
        logger.info("Testing data collector agents...")
        
        try:
            info_response = await self.client.get(f"{self.base_url}/info")
            if info_response.status_code != 200:
                logger.warning("Could not get info to check data collector URLs")
                return False
            
            info = info_response.json()
            collectors = info.get("data_collector_agents", {})
            
            results = {}
            
            # Test news-scraper
            news_url = collectors.get("news_scraper", "")
            if news_url:
                try:
                    response = await self.client.get(f"{news_url}/health", timeout=5.0)
                    results["news-scraper"] = response.status_code == 200
                    logger.info(f"   news-scraper: {'✅' if results['news-scraper'] else '❌'}")
                except Exception as e:
                    results["news-scraper"] = False
                    logger.warning(f"   news-scraper: ❌ ({e})")
            
            # Test startup-api
            startup_url = collectors.get("startup_api", "")
            if startup_url:
                try:
                    response = await self.client.get(f"{startup_url}/health", timeout=5.0)
                    results["startup-api"] = response.status_code == 200
                    logger.info(f"   startup-api: {'✅' if results['startup-api'] else '❌'}")
                except Exception as e:
                    results["startup-api"] = False
                    logger.warning(f"   startup-api: ❌ ({e})")
            
            # Test github-monitor
            github_url = collectors.get("github_monitor", "")
            if github_url:
                try:
                    response = await self.client.get(f"{github_url}/health", timeout=5.0)
                    results["github-monitor"] = response.status_code == 200
                    logger.info(f"   github-monitor: {'✅' if results['github-monitor'] else '❌'}")
                except Exception as e:
                    results["github-monitor"] = False
                    logger.warning(f"   github-monitor: ❌ ({e})")
            
            all_working = all(results.values()) if results else False
            if all_working:
                logger.info("✅ All data collector agents are accessible")
            else:
                logger.warning("⚠️  Some data collector agents are not accessible")
                logger.warning("   Note: Agents must be running locally via docker-compose")
            
            return all_working
            
        except Exception as e:
            logger.error(f"❌ Data collector test error: {e}")
            return False
    
    async def test_briefing_endpoint(self) -> bool:
        """Test /briefing endpoint."""
        logger.info("Testing /briefing endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/briefing")
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Briefing endpoint working")
                logger.info(f"   Briefing date: {data.get('date', 'N/A')}")
                logger.info(f"   Summary: {data.get('summary', 'N/A')[:100]}...")
                return True
            elif response.status_code == 404:
                logger.info("ℹ️  No briefing found (expected if workflow hasn't run yet)")
                logger.info("   Use POST /orchestrator/run to generate a briefing")
                return True  # 404 is expected if no briefing exists
            else:
                logger.error(f"❌ Briefing endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Briefing endpoint error: {e}")
            return False
    
    async def test_orchestrator_status(self) -> bool:
        """Test /orchestrator/status endpoint."""
        logger.info("Testing /orchestrator/status endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/orchestrator/status")
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Orchestrator status endpoint working")
                logger.info(f"   Running: {data.get('running', False)}")
                logger.info(f"   Last run: {data.get('last_run', 'N/A')}")
                return True
            else:
                logger.error(f"❌ Orchestrator status failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Orchestrator status error: {e}")
            return False
    
    async def test_workflow_trigger(self, wait_for_completion: bool = False) -> bool:
        """Test triggering the workflow."""
        logger.info("Testing workflow trigger (/orchestrator/run)...")
        try:
            response = await self.client.post(
                f"{self.base_url}/orchestrator/run",
                params={"days_back": 7}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Workflow triggered successfully")
                logger.info(f"   Status: {data.get('status')}")
                logger.info(f"   Message: {data.get('message')}")
                
                if wait_for_completion:
                    logger.info("⏳ Waiting for workflow to complete (this may take a few minutes)...")
                    # Poll status endpoint
                    for i in range(60):  # Wait up to 5 minutes
                        await asyncio.sleep(5)
                        status_response = await self.client.get(f"{self.base_url}/orchestrator/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if not status_data.get("running", False):
                                logger.info("✅ Workflow completed!")
                                if status_data.get("error"):
                                    logger.warning(f"   Warning: {status_data.get('error')}")
                                return True
                        if i % 6 == 0:  # Log every 30 seconds
                            logger.info(f"   Still running... ({i * 5} seconds)")
                    
                    logger.warning("⚠️  Workflow is still running after 5 minutes")
                    return True  # Workflow started, even if not complete
                else:
                    logger.info("💡 Workflow is running in background")
                    logger.info("   Check status with: GET /orchestrator/status")
                    return True
            elif response.status_code == 409:
                logger.warning("⚠️  Workflow is already running")
                return True
            else:
                logger.error(f"❌ Workflow trigger failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Workflow trigger error: {e}")
            return False
    
    async def test_data_stats(self) -> bool:
        """Test /data/stats endpoint."""
        logger.info("Testing /data/stats endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/data/stats")
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Data stats endpoint working")
                logger.info(f"   News articles: {data.get('news_count', 0)}")
                logger.info(f"   Funding rounds: {data.get('funding_count', 0)}")
                logger.info(f"   Launches: {data.get('launches_count', 0)}")
                logger.info(f"   GitHub repos: {data.get('github_repos_count', 0)}")
                return True
            else:
                logger.error(f"❌ Data stats failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Data stats error: {e}")
            return False
    
    async def run_all_tests(self, trigger_workflow: bool = False, wait_for_workflow: bool = False) -> Dict[str, bool]:
        """Run all tests."""
        print("=" * 70)
        print("E2B Sandbox Deployment Testing")
        print("=" * 70)
        print()
        print(f"Testing sandbox at: {self.base_url}")
        print()
        
        results = {}
        
        # Basic connectivity tests
        results["health"] = await self.test_health_endpoint()
        print()
        
        results["info"] = await self.test_info_endpoint()
        print()
        
        results["data_collectors"] = await self.test_data_collectors()
        print()
        
        results["orchestrator_status"] = await self.test_orchestrator_status()
        print()
        
        results["data_stats"] = await self.test_data_stats()
        print()
        
        results["briefing"] = await self.test_briefing_endpoint()
        print()
        
        # Optional workflow trigger
        if trigger_workflow:
            results["workflow"] = await self.test_workflow_trigger(wait_for_completion=wait_for_workflow)
            print()
        
        # Summary
        print("=" * 70)
        print("Test Summary")
        print("=" * 70)
        print()
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name:20s} {status}")
        
        print()
        print(f"Results: {passed}/{total} tests passed")
        print()
        
        if passed == total:
            print("🎉 All tests passed! Deployment is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        print("=" * 70)
        
        return results
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test E2B sandbox deployment")
    parser.add_argument(
        "sandbox_url",
        help="E2B sandbox URL (e.g., https://sandbox-id.e2b.dev or sandbox-id.e2b.dev)"
    )
    parser.add_argument(
        "--trigger-workflow",
        action="store_true",
        help="Trigger the workflow as part of testing"
    )
    parser.add_argument(
        "--wait-for-workflow",
        action="store_true",
        help="Wait for workflow to complete (only works with --trigger-workflow)"
    )
    
    args = parser.parse_args()
    
    tester = E2BDeploymentTester(args.sandbox_url)
    
    try:
        results = await tester.run_all_tests(
            trigger_workflow=args.trigger_workflow,
            wait_for_workflow=args.wait_for_workflow
        )
        
        # Exit with error code if any test failed
        if not all(results.values()):
            sys.exit(1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())

