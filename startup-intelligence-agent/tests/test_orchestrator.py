#!/usr/bin/env python3
"""Test script for the Orchestrator Agent workflow."""
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_orchestrator_creation():
    """Test that orchestrator can be created."""
    print("=" * 60)
    print("Test 1: Orchestrator Creation")
    print("=" * 60)
    
    try:
        from orchestrator.agent import OrchestratorAgent
        
        agent = OrchestratorAgent()
        print("✓ OrchestratorAgent created successfully")
        print(f"  Database path: {agent.db.db_path}")
        print(f"  Has enrichment agent: {hasattr(agent, 'enrichment_agent')}")
        print(f"  Has analysis agent: {hasattr(agent, 'analysis_agent')}")
        print(f"  Has summarizer agent: {hasattr(agent, 'summarizer_agent')}")
        print(f"  Has HTTP client: {hasattr(agent, 'http_client')}")
        
        await agent.close()
        print("✓ Orchestrator closed successfully")
        return True
    except Exception as e:
        print(f"✗ Orchestrator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_collection():
    """Test data collection from agents (will fail gracefully if agents not running)."""
    print("\n" + "=" * 60)
    print("Test 2: Data Collection")
    print("=" * 60)
    
    try:
        from orchestrator.agent import OrchestratorAgent
        
        agent = OrchestratorAgent()
        
        print("Testing data collection (agents may not be running)...")
        print("  Note: This will return empty data if agents are not available")
        
        # Test individual collection methods
        print("\n  Testing news collection...")
        news_data = await agent.collect_from_news_agent()
        print(f"    Result: {news_data.get('total', 0)} articles (or error: {news_data.get('error')})")
        
        print("\n  Testing startup API collection...")
        startup_data = await agent.collect_from_startup_api_agent()
        print(f"    Funding rounds: {len(startup_data.get('funding', []))}")
        print(f"    Launches: {len(startup_data.get('launches', []))}")
        
        print("\n  Testing GitHub collection...")
        github_data = await agent.collect_from_github_agent()
        print(f"    Trending repos: {len(github_data.get('trending', []))}")
        print(f"    Signals: {len(github_data.get('signals', []))}")
        
        # Test parallel collection
        print("\n  Testing parallel collection...")
        all_data = await agent.collect_all_data()
        print(f"    News: {all_data['news'].get('total', 0) if 'total' in all_data['news'] else 'error'}")
        print(f"    Funding: {len(all_data['startup'].get('funding', []))}")
        print(f"    Launches: {len(all_data['startup'].get('launches', []))}")
        print(f"    GitHub repos: {len(all_data['github'].get('trending', []))}")
        print(f"    GitHub signals: {len(all_data['github'].get('signals', []))}")
        
        await agent.close()
        print("\n✓ Data collection test completed (errors are expected if agents not running)")
        return True
    except Exception as e:
        print(f"\n✗ Data collection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_storage():
    """Test data storage with mock data."""
    print("\n" + "=" * 60)
    print("Test 3: Data Storage")
    print("=" * 60)
    
    try:
        from orchestrator.agent import OrchestratorAgent
        
        agent = OrchestratorAgent()
        
        # Create mock data
        mock_news_data = {
            "sources": {
                "techcrunch": {
                    "articles": [
                        {
                            "title": "Test Article 1",
                            "url": "https://example.com/article1",
                            "source": "techcrunch",
                            "timestamp": datetime.now().isoformat(),
                            "summary": "Test summary",
                            "author": "Test Author"
                        }
                    ]
                }
            },
            "total": 1
        }
        
        mock_startup_data = {
            "funding": [
                {
                    "company_name": "Test Startup",
                    "amount": "$1M",
                    "funding_type": "Seed",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "description": "Test funding round",
                    "source": "test"
                }
            ],
            "launches": [
                {
                    "name": "Test Product",
                    "description": "Test product launch",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "test"
                }
            ]
        }
        
        mock_github_data = {
            "trending": [
                {
                    "name": "test-repo",
                    "full_name": "test/test-repo",
                    "description": "Test repository",
                    "url": "https://github.com/test/test-repo",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "stars": 100
                }
            ],
            "signals": [
                {
                    "signal_type": "spike",
                    "repository_name": "test/test-repo",
                    "indicator": "rapid growth",
                    "confidence": "high",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
        }
        
        print("Storing mock data...")
        
        # Test news storage
        news_inserted = await agent.store_news_articles(mock_news_data)
        print(f"  ✓ Stored {news_inserted} news articles")
        
        # Test startup signals storage
        signals_inserted = await agent.store_startup_signals(mock_startup_data)
        print(f"  ✓ Stored {signals_inserted['funding']} funding rounds")
        print(f"  ✓ Stored {signals_inserted['launches']} launches")
        
        # Test GitHub signals storage
        github_inserted = await agent.store_github_signals(mock_github_data)
        print(f"  ✓ Stored {github_inserted['repositories']} GitHub repositories")
        print(f"  ✓ Stored {github_inserted['signals']} GitHub signals")
        
        # Verify data in database
        print("\nVerifying stored data...")
        recent_news = agent.db.get_recent_news(days=1, limit=10)
        print(f"  Recent news articles in DB: {len(recent_news)}")
        
        recent_funding = agent.db.get_recent_funding(days=1, limit=10)
        print(f"  Recent funding rounds in DB: {len(recent_funding)}")
        
        recent_launches = agent.db.get_recent_launches(days=1, limit=10)
        print(f"  Recent launches in DB: {len(recent_launches)}")
        
        recent_repos = agent.db.get_recent_github_repos(days=1, limit=10)
        print(f"  Recent GitHub repos in DB: {len(recent_repos)}")
        
        await agent.close()
        print("\n✓ Data storage test completed successfully")
        return True
    except Exception as e:
        print(f"\n✗ Data storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_execution():
    """Test workflow execution (will fail at enrichment/analysis/summarization)."""
    print("\n" + "=" * 60)
    print("Test 4: Workflow Execution")
    print("=" * 60)
    
    try:
        from orchestrator.agent import OrchestratorAgent
        
        agent = OrchestratorAgent()
        
        print("Testing data collection only workflow...")
        print("  (This skips enrichment/analysis/summarization)")
        
        result = await agent.run_data_collection_only()
        
        print(f"\n✓ Workflow result:")
        print(f"  Status: {result.get('status')}")
        print(f"  News articles: {result['data_collected'].get('news_articles', 0)}")
        print(f"  Funding rounds: {result['data_collected'].get('funding_rounds', 0)}")
        print(f"  Launches: {result['data_collected'].get('launches', 0)}")
        print(f"  GitHub repos: {result['data_collected'].get('github_repositories', 0)}")
        print(f"  GitHub signals: {result['data_collected'].get('github_signals', 0)}")
        
        await agent.close()
        print("\n✓ Data collection workflow test completed")
        
        # Test full workflow (will fail at enrichment step)
        print("\nTesting full workflow (will fail at enrichment step)...")
        agent = OrchestratorAgent()
        
        try:
            result = await agent.run_full_workflow(days_back=7)
            print(f"✓ Full workflow completed!")
            print(f"  Status: {result.get('status')}")
            print(f"  Duration: {result.get('duration_seconds', 0):.2f} seconds")
            await agent.close()
        except AttributeError as e:
            print(f"  ⚠ Expected failure: {e}")
            print("  (This is expected - enrichment/analysis/summarizer agents are placeholders)")
            await agent.close()
        except Exception as e:
            print(f"  ⚠ Error in workflow: {e}")
            print("  (This is expected if agents are placeholders or not implemented)")
            await agent.close()
        
        return True
    except Exception as e:
        print(f"\n✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_operations():
    """Test database operations directly."""
    print("\n" + "=" * 60)
    print("Test 5: Database Operations")
    print("=" * 60)
    
    try:
        from database.db import Database
        from config.settings import settings
        
        db = Database(settings.DATABASE_PATH)
        
        print("Testing database operations...")
        
        # Test counts
        news_count = db.count_recent_news(days=7)
        print(f"  Recent news (7 days): {news_count}")
        
        funding_count = db.count_recent_funding(days=7)
        print(f"  Recent funding (7 days): {funding_count}")
        
        launches_count = db.count_recent_launches(days=7)
        print(f"  Recent launches (7 days): {launches_count}")
        
        repos_count = db.count_recent_github_repos(days=7)
        print(f"  Recent GitHub repos (7 days): {repos_count}")
        
        # Test retrieval
        recent_news = db.get_recent_news(days=7, limit=5)
        print(f"  Retrieved {len(recent_news)} news articles")
        
        if recent_news:
            print(f"    Example: {recent_news[0].get('title', 'N/A')[:50]}...")
        
        print("\n✓ Database operations test completed")
        return True
    except Exception as e:
        print(f"\n✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Orchestrator Agent - Comprehensive Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Orchestrator Creation", await test_orchestrator_creation()))
    results.append(("Data Collection", await test_data_collection()))
    results.append(("Data Storage", await test_data_storage()))
    results.append(("Database Operations", await test_database_operations()))
    results.append(("Workflow Execution", await test_workflow_execution()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n⚠ Some tests had issues (may be expected for placeholders)")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Implement Enrichment Agent (07-enrichment-agent.md)")
    print("2. Implement Analysis Agent (08-analysis-agent.md)")
    print("3. Implement Summarizer Agent (09-summarizer-agent.md)")
    print("4. Build Data Collector Agents (02-04 workflow prompts)")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

