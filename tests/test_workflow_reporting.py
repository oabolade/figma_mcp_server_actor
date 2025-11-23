#!/usr/bin/env python3
"""Test workflow reporting endpoints."""
import asyncio
import httpx
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8080"


async def test_workflow_health():
    """Test workflow health endpoint."""
    print("\n=== Testing Workflow Health ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/workflow/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Health Status: {data.get('status', 'unknown')}")
            print(f"   Data Collection (24h):")
            print(f"     - News: {data.get('data_collection', {}).get('last_24h', {}).get('news_24h', 0)}")
            print(f"     - Funding: {data.get('data_collection', {}).get('last_24h', {}).get('funding_24h', 0)}")
            print(f"     - Launches: {data.get('data_collection', {}).get('last_24h', {}).get('launches_24h', 0)}")
            print(f"   Last Briefing: {data.get('workflow', {}).get('last_briefing', 'N/A')}")
            print(f"   Last Analysis: {data.get('workflow', {}).get('last_analysis', 'N/A')}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_workflow_report(days: int = 7):
    """Test workflow report endpoint."""
    print(f"\n=== Testing Workflow Report (Last {days} days) ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/workflow/report", params={"days": days})
            response.raise_for_status()
            data = response.json()
            print(f"✅ Report Generated")
            print(f"   Period: {data.get('period', 'N/A')}")
            print(f"   Data Collected:")
            dc = data.get('data_collected', {})
            print(f"     - News: {dc.get('news_articles', 0)}")
            print(f"     - Funding: {dc.get('funding_rounds', 0)}")
            print(f"     - Launches: {dc.get('launches', 0)}")
            print(f"     - GitHub Repos: {dc.get('github_repositories', 0)}")
            print(f"     - GitHub Signals: {dc.get('github_signals', 0)}")
            print(f"     - Total: {dc.get('total', 0)}")
            print(f"   Workflow Executions:")
            we = data.get('workflow_executions', {})
            print(f"     - Briefings: {we.get('briefings_generated', 0)}")
            print(f"     - Analyses: {we.get('analyses_performed', 0)}")
            print(f"   Enrichment Rate: {data.get('data_enrichment', {}).get('enrichment_rate', 0)}%")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_daily_report(date: str = None):
    """Test daily report endpoint."""
    print(f"\n=== Testing Daily Report ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {}
            if date:
                params["date"] = date
            response = await client.get(f"{API_BASE_URL}/workflow/daily-report", params=params)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Daily Report Generated")
            print(f"   Report Date: {data.get('report_date', 'N/A')}")
            print(f"   Data Collection:")
            dc = data.get('data_collection', {})
            print(f"     - News: {dc.get('news_articles', 0)}")
            print(f"     - Funding: {dc.get('funding_rounds', 0)}")
            print(f"     - Launches: {dc.get('launches', 0)}")
            print(f"     - GitHub Repos: {dc.get('github_repositories', 0)}")
            print(f"     - GitHub Signals: {dc.get('github_signals', 0)}")
            print(f"     - Total: {dc.get('total', 0)}")
            print(f"   Workflow Status:")
            ws = data.get('workflow_status', {})
            print(f"     - Briefing Available: {ws.get('briefing_available', False)}")
            print(f"     - Analysis Available: {ws.get('analysis_available', False)}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all workflow reporting tests."""
    print("=" * 60)
    print("Workflow Reporting System Test")
    print("=" * 60)
    
    results = []
    
    # Test health endpoint
    results.append(await test_workflow_health())
    
    # Test workflow report
    results.append(await test_workflow_report(days=7))
    
    # Test daily report
    results.append(await test_daily_report())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 All workflow reporting tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check server logs for details.")
        print("   Make sure the server is running and has been restarted")
        print("   to load the new workflow reporting endpoints.")


if __name__ == "__main__":
    asyncio.run(main())

