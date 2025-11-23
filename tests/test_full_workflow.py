#!/usr/bin/env python3
"""Test the full end-to-end workflow: collect → enrich → analyze → summarize."""
import asyncio
import sys
import os
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent / "startup-intelligence-agent" / "backend" / "src"
sys.path.insert(0, str(backend_src))

from orchestrator.agent import OrchestratorAgent
from database.db import Database
from config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_data_collectors():
    """Test all data collector agents are accessible."""
    print("\n" + "="*60)
    print("STEP 1: Testing Data Collector Agents")
    print("="*60)
    
    orchestrator = OrchestratorAgent()
    
    # Test news-scraper
    print("\n📰 Testing news-scraper agent...")
    news_data = await orchestrator.collect_from_news_agent()
    print(f"   Status: {'✅ Success' if not news_data.get('error') else '❌ Error'}")
    if news_data.get('error'):
        print(f"   Error: {news_data.get('error')}")
    else:
        print(f"   Articles collected: {news_data.get('total', 0)}")
        sources = news_data.get('sources', {})
        for source, data in sources.items():
            if isinstance(data, dict):
                count = data.get('count', 0)
                print(f"     • {source}: {count} articles")
    
    # Test startup-api
    print("\n🚀 Testing startup-api agent...")
    startup_data = await orchestrator.collect_from_startup_api_agent()
    print(f"   Status: {'✅ Success' if not startup_data.get('error') else '❌ Error'}")
    if startup_data.get('error'):
        print(f"   Error: {startup_data.get('error')}")
    else:
        # Handle different response formats
        if isinstance(startup_data.get('funding'), list):
            funding_count = len(startup_data.get('funding', []))
        elif isinstance(startup_data.get('funding'), dict):
            funding_count = len(startup_data.get('funding', {}).get('funding_rounds', []))
        else:
            funding_count = 0
        
        if isinstance(startup_data.get('launches'), list):
            launches_count = len(startup_data.get('launches', []))
        elif isinstance(startup_data.get('launches'), dict):
            launches_count = len(startup_data.get('launches', {}).get('launches', []))
        else:
            launches_count = 0
        
        print(f"   Funding rounds: {funding_count}")
        print(f"   Launches: {launches_count}")
    
    # Test github-monitor
    print("\n🐙 Testing github-monitor agent...")
    github_data = await orchestrator.collect_from_github_agent()
    print(f"   Status: {'✅ Success' if not github_data.get('error') else '❌ Error'}")
    if github_data.get('error'):
        print(f"   Error: {github_data.get('error')}")
    else:
        # Handle different response formats - orchestrator returns lists directly
        if isinstance(github_data.get('trending'), list):
            trending_count = len(github_data.get('trending', []))
        elif isinstance(github_data.get('trending'), dict):
            trending_count = len(github_data.get('trending', {}).get('repositories', []))
        else:
            trending_count = 0
        
        if isinstance(github_data.get('signals'), list):
            signals_count = len(github_data.get('signals', []))
        elif isinstance(github_data.get('signals'), dict):
            signals_count = len(github_data.get('signals', {}).get('signals', []))
        else:
            signals_count = 0
        
        print(f"   Trending repos: {trending_count}")
        print(f"   Signals: {signals_count}")
    
    await orchestrator.close()
    return True


async def test_data_collection_workflow():
    """Test data collection workflow only."""
    print("\n" + "="*60)
    print("STEP 2: Testing Data Collection Workflow")
    print("="*60)
    
    orchestrator = OrchestratorAgent()
    
    print("\n🔄 Running data collection workflow...")
    result = await orchestrator.run_data_collection_only()
    
    print(f"\n   Status: {result.get('status')}")
    if result.get('status') == 'success':
        data = result.get('data_collected', {})
        print(f"   News articles: {data.get('news_articles', 0)}")
        print(f"   Funding rounds: {data.get('funding_rounds', 0)}")
        print(f"   Launches: {data.get('launches', 0)}")
        print(f"   GitHub repos: {data.get('github_repos', 0)}")
        print(f"   GitHub signals: {data.get('github_signals', 0)}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    await orchestrator.close()
    return result.get('status') == 'success'


async def test_full_workflow():
    """Test the complete workflow: collect → enrich → analyze → summarize."""
    print("\n" + "="*60)
    print("STEP 3: Testing Full Workflow (collect → enrich → analyze → summarize)")
    print("="*60)
    
    orchestrator = OrchestratorAgent()
    
    print("\n🔄 Running full workflow...")
    print("   This may take a few minutes...")
    
    try:
        result = await orchestrator.run_full_workflow(days_back=7)
        
        print(f"\n   Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print("\n✅ Workflow completed successfully!")
            
            # Show data collection results
            data_collected = result.get('data_collected', {})
            print("\n📊 Data Collected:")
            print(f"   News articles: {data_collected.get('news_articles', 0)}")
            print(f"   Funding rounds: {data_collected.get('funding_rounds', 0)}")
            print(f"   Launches: {data_collected.get('launches', 0)}")
            print(f"   GitHub repos: {data_collected.get('github_repos', 0)}")
            print(f"   GitHub signals: {data_collected.get('github_signals', 0)}")
            
            # Check if briefing was created
            db = Database(settings.DATABASE_PATH)
            latest_briefing = db.get_latest_briefing()
            
            if latest_briefing:
                print("\n📄 Briefing Created:")
                briefing_json = latest_briefing.get('briefing_json', {})
                print(f"   Date: {latest_briefing.get('briefing_date')}")
                print(f"   Summary: {briefing_json.get('summary', 'N/A')[:100]}...")
                print(f"   Trends: {len(briefing_json.get('trends', []))}")
                print(f"   Funding rounds: {len(briefing_json.get('funding_rounds', []))}")
            else:
                print("\n⚠️  Warning: No briefing was created")
            
        else:
            print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Error during full workflow: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False
    finally:
        await orchestrator.close()
    
    return result.get('status') == 'success'


async def test_database_queries():
    """Test database queries to verify data was stored."""
    print("\n" + "="*60)
    print("STEP 4: Testing Database Queries")
    print("="*60)
    
    db = Database(settings.DATABASE_PATH)
    
    print("\n📊 Database Statistics:")
    
    # Count recent data
    news_count = db.count_recent_news(days=7)
    funding_count = db.count_recent_funding(days=7)
    launches_count = db.count_recent_launches(days=7)
    github_repos_count = db.count_recent_github_repos(days=7)
    # Count github signals using get_recent_github_signals
    github_signals = db.get_recent_github_signals(days=7)
    github_signals_count = len(github_signals) if github_signals else 0
    
    print(f"   News articles (last 7 days): {news_count}")
    print(f"   Funding rounds (last 7 days): {funding_count}")
    print(f"   Launches (last 7 days): {launches_count}")
    print(f"   GitHub repos (last 7 days): {github_repos_count}")
    print(f"   GitHub signals (last 7 days): {github_signals_count}")
    
    # Check for briefings
    latest_briefing = db.get_latest_briefing()
    if latest_briefing:
        print(f"\n✅ Latest briefing found: {latest_briefing.get('briefing_date')}")
    else:
        print("\n⚠️  No briefings found")
    
    # Check for analysis results
    latest_analysis = db.get_latest_analysis()
    if latest_analysis:
        print(f"✅ Latest analysis found: {latest_analysis.get('created_at')}")
    else:
        print("⚠️  No analysis results found")


async def main():
    """Run all workflow tests."""
    print("\n" + "="*60)
    print("STARTUP INTELLIGENCE SYSTEM - WORKFLOW TESTING")
    print("="*60)
    print("\nThis will test the complete workflow:")
    print("  1. Data Collector Agents connectivity")
    print("  2. Data Collection workflow")
    print("  3. Full workflow (collect → enrich → analyze → summarize)")
    print("  4. Database queries")
    
    try:
        # Step 1: Test data collectors
        await test_data_collectors()
        
        # Step 2: Test data collection
        collection_success = await test_data_collection_workflow()
        if not collection_success:
            print("\n⚠️  Data collection failed. Skipping full workflow test.")
            return
        
        # Step 3: Test full workflow
        print("\n\n⚠️  Note: Full workflow test requires LLM API key.")
        print("   If API key is not set, analysis/summarization will fail gracefully.")
        
        workflow_success = await test_full_workflow()
        
        # Step 4: Test database queries
        await test_database_queries()
        
        print("\n" + "="*60)
        print("WORKFLOW TESTING COMPLETE")
        print("="*60)
        
        if workflow_success:
            print("\n✅ All tests passed!")
            print("\n🌐 Next steps:")
            print("  • View briefing: curl http://localhost:8080/briefing")
            print("  • Open frontend: http://localhost:8080/")
            print("  • View API docs: http://localhost:8080/docs")
        else:
            print("\n⚠️  Some tests failed. Check logs above for details.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

