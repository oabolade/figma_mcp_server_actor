#!/usr/bin/env python3
"""Test workflow scheduler endpoints."""
import asyncio
import httpx
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8080"


async def test_scheduler_status():
    """Test scheduler status endpoint."""
    print("\n=== Testing Scheduler Status ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/workflow/scheduler/status")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Scheduler Status Retrieved")
            print(f"   Enabled: {data.get('enabled', False)}")
            print(f"   Running: {data.get('is_running', False)}")
            print(f"   Frequency: {data.get('frequency', 'N/A')}")
            print(f"   Last Run: {data.get('last_run', 'N/A')}")
            print(f"   Next Run: {data.get('next_run', 'N/A')}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_start_scheduler(frequency="daily", run_immediately=False):
    """Test starting the scheduler."""
    print(f"\n=== Testing Start Scheduler ({frequency}) ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "frequency": frequency,
                "run_immediately": run_immediately
            }
            response = await client.post(
                f"{API_BASE_URL}/workflow/scheduler/start",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ Scheduler Started")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Frequency: {data.get('frequency', 'N/A')}")
            print(f"   Interval: {data.get('interval_seconds', 0)} seconds")
            print(f"   Next Run: {data.get('next_run', 'N/A')}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_trigger_scheduler():
    """Test manual trigger."""
    print("\n=== Testing Manual Trigger ===")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for workflow
            response = await client.post(f"{API_BASE_URL}/workflow/scheduler/trigger")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Workflow Triggered")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Last Run: {data.get('last_run', 'N/A')}")
            print(f"   Next Run: {data.get('next_run', 'N/A')}")
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_stop_scheduler():
    """Test stopping the scheduler."""
    print("\n=== Testing Stop Scheduler ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{API_BASE_URL}/workflow/scheduler/stop")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Scheduler Stopped")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"⚠️  Scheduler not running (expected if not started)")
            return True
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all scheduler tests."""
    print("=" * 60)
    print("Workflow Scheduler Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Check initial status
    results.append(await test_scheduler_status())
    
    # Test 2: Start scheduler (daily)
    results.append(await test_start_scheduler(frequency="daily", run_immediately=False))
    
    # Test 3: Check status after start
    await asyncio.sleep(1)
    results.append(await test_scheduler_status())
    
    # Test 4: Manual trigger (optional - takes time)
    print("\n⚠️  Manual trigger test skipped (would run full workflow)")
    print("   To test manually: curl -X POST http://localhost:8080/workflow/scheduler/trigger")
    
    # Test 5: Stop scheduler
    results.append(await test_stop_scheduler())
    
    # Test 6: Check status after stop
    await asyncio.sleep(1)
    results.append(await test_scheduler_status())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 All scheduler tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check server logs for details.")


if __name__ == "__main__":
    asyncio.run(main())

