# Prompt 5: Orchestrator Agent Workflow

## Objective

Create the main orchestrator agent that runs inside an E2B sandbox and coordinates the entire workflow: calling Data Collector Agents (via Docker MCP Hub), storing data, enriching data, triggering analysis, and generating summaries.

## Requirements

### Orchestrator Responsibilities

The Orchestrator Agent lives **inside an E2B sandbox** and manages the complete workflow loop:

**Workflow Loop:** `collect → enrich → analyze → summarize`

1. **Data Collection**
   - Call `news-scraper` agent (Docker MCP Hub)
   - Call `startup-api` agent (Docker MCP Hub)
   - Call `github-monitor` agent (Docker MCP Hub)
   - Handle errors and retries
   - Coordinate parallel agent calls

2. **Data Storage**
   - Store scraped articles in SQLite/ChromaDB (in-sandbox)
   - Store funding rounds in database
   - Store launches in database
   - Store GitHub signals in database
   - Track what's been stored to avoid duplicates

3. **Data Enrichment** (Optional but Recommended)
   - Add metadata and context to collected data
   - Cross-reference data sources
   - Enhance with additional signals
   - Link related items across sources

4. **Workflow Coordination**
   - Trigger enrichment step after data collection
   - Trigger analysis agent after enrichment
   - Trigger summarizer agent after analysis
   - Manage the full pipeline: **collect → enrich → analyze → summarize**

5. **Scheduling**
   - Support manual triggering
   - Support scheduled runs (e.g., daily at 9 AM)
   - Handle concurrent runs gracefully

### Implementation

**File:** `backend/src/orchestrator/agent.py`

```python
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from database.db import Database
from enrichment.agent import EnrichmentAgent
from analysis.agent import AnalysisAgent
from summarizer.agent import SummarizerAgent
from config.settings import settings

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        self.db = Database(settings.DATABASE_PATH)
        self.enrichment_agent = EnrichmentAgent()
        self.analysis_agent = AnalysisAgent()
        self.summarizer_agent = SummarizerAgent()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def collect_from_news_agent(self) -> Dict:
        """Call news-scraper agent via Docker MCP Hub."""
        logger.info("Collecting news from news-scraper agent...")
        
        try:
            response = await self.http_client.get(
                f"{settings.NEWS_SCRAPER_URL}/all",
                params={"limit": 20, "hours": 24}
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Retrieved {data.get('total', 0)} news articles")
            return data
            
        except httpx.RequestError as e:
            logger.error(f"Error calling news-scraper agent: {e}")
            return {"error": str(e), "sources": {}, "total": 0}
    
    async def collect_from_startup_api_agent(self) -> Dict:
        """Call startup-api agent via Docker MCP Hub."""
        logger.info("Collecting startup signals from startup-api agent...")
        
        try:
            # Collect funding
            funding_response = await self.http_client.get(
                f"{settings.STARTUP_API_URL}/funding",
                params={"days": 7}
            )
            funding_data = funding_response.json() if funding_response.status_code == 200 else {"funding_rounds": []}
            
            # Collect launches
            launches_response = await self.http_client.get(
                f"{settings.STARTUP_API_URL}/launches",
                params={"days": 7}
            )
            launches_data = launches_response.json() if launches_response.status_code == 200 else {"launches": []}
            
            logger.info(f"Retrieved {len(funding_data.get('funding_rounds', []))} funding rounds")
            logger.info(f"Retrieved {len(launches_data.get('launches', []))} launches")
            
            return {
                "funding": funding_data.get("funding_rounds", []),
                "launches": launches_data.get("launches", [])
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error calling startup-api agent: {e}")
            return {"funding": [], "launches": []}
    
    async def collect_from_github_agent(self) -> Dict:
        """Call github-monitor agent via Docker MCP Hub."""
        logger.info("Collecting GitHub signals from github-monitor agent...")
        
        try:
            # Collect trending repos
            trending_response = await self.http_client.get(
                f"{settings.GITHUB_MONITOR_URL}/trending",
                params={"since": "daily", "limit": 25}
            )
            trending_data = trending_response.json() if trending_response.status_code == 200 else {"repositories": []}
            
            # Collect technical signals
            signals_response = await self.http_client.get(
                f"{settings.GITHUB_MONITOR_URL}/signals",
                params={"days": 7, "keywords": "startup,AI,tech"}
            )
            signals_data = signals_response.json() if signals_response.status_code == 200 else {"signals": []}
            
            logger.info(f"Retrieved {len(trending_data.get('repositories', []))} trending repositories")
            logger.info(f"Retrieved {len(signals_data.get('signals', []))} technical signals")
            
            return {
                "trending": trending_data.get("repositories", []),
                "signals": signals_data.get("signals", [])
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error calling github-monitor agent: {e}")
            return {"trending": [], "signals": []}
    
    async def collect_all_data(self) -> Dict:
        """Collect data from all data collector agents in parallel."""
        logger.info("Starting parallel data collection from all agents...")
        
        # Collect from all agents in parallel
        news_task = self.collect_from_news_agent()
        startup_task = self.collect_from_startup_api_agent()
        github_task = self.collect_from_github_agent()
        
        news_data, startup_data, github_data = await asyncio.gather(
            news_task, startup_task, github_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(news_data, Exception):
            logger.error(f"News collection failed: {news_data}")
            news_data = {"error": str(news_data), "sources": {}, "total": 0}
        
        if isinstance(startup_data, Exception):
            logger.error(f"Startup API collection failed: {startup_data}")
            startup_data = {"funding": [], "launches": []}
        
        if isinstance(github_data, Exception):
            logger.error(f"GitHub collection failed: {github_data}")
            github_data = {"trending": [], "signals": []}
        
        return {
            "news": news_data,
            "startup": startup_data,
            "github": github_data
        }
    
    async def store_news_articles(self, news_data: Dict) -> int:
        """Store news articles in database."""
        articles = []
        
        sources = news_data.get("sources", {})
        for source_name, source_data in sources.items():
            source_articles = source_data.get("articles", [])
            for article in source_articles:
                article["source"] = source_name
                articles.append(article)
        
        if articles:
            inserted = self.db.insert_news(articles)
            logger.info(f"Stored {inserted} new news articles")
            return inserted
        return 0
    
    async def store_startup_signals(self, signals: Dict) -> Dict[str, int]:
        """Store funding rounds and launches in database."""
        funding_rounds = signals.get("funding", [])
        launches = signals.get("launches", [])
        
        funding_inserted = self.db.insert_funding(funding_rounds) if funding_rounds else 0
        launches_inserted = self.db.insert_launches(launches) if launches else 0
        
        logger.info(f"Stored {funding_inserted} funding rounds")
        logger.info(f"Stored {launches_inserted} launches")
        
        return {
            "funding": funding_inserted,
            "launches": launches_inserted
        }
    
    async def store_github_signals(self, github_data: Dict) -> Dict[str, int]:
        """Store GitHub repositories and signals in database."""
        trending = github_data.get("trending", [])
        signals = github_data.get("signals", [])
        
        trending_inserted = self.db.insert_github_repositories(trending) if trending else 0
        signals_inserted = self.db.insert_github_signals(signals) if signals else 0
        
        logger.info(f"Stored {trending_inserted} trending repositories")
        logger.info(f"Stored {signals_inserted} GitHub signals")
        
        return {
            "repositories": trending_inserted,
            "signals": signals_inserted
        }
    
    async def run_full_workflow(self, days_back: int = 7) -> Dict:
        """Execute the complete workflow: collect → enrich → analyze → summarize."""
        logger.info("Starting full orchestrator workflow...")
        
        workflow_start = datetime.now()
        
        # STEP 1: COLLECT - Call all data collector agents
        logger.info("Step 1: Collecting data from all agents...")
        collected_data = await self.collect_all_data()
        
        # STEP 2: STORE - Store collected data in sandbox database
        logger.info("Step 2: Storing collected data...")
        news_inserted = await self.store_news_articles(collected_data["news"])
        signals_inserted = await self.store_startup_signals(collected_data["startup"])
        github_inserted = await self.store_github_signals(collected_data["github"])
        
        # STEP 3: ENRICH - Enrich stored data with additional context
        logger.info("Step 3: Enriching data with additional context...")
        enrichment_results = await self.enrichment_agent.enrich_recent_data(days_back=days_back)
        
        # STEP 4: ANALYZE - Analyze enriched data for patterns and insights
        logger.info("Step 4: Analyzing data for patterns and insights...")
        analysis_results = await self.analysis_agent.analyze_recent_data(days_back=days_back)
        
        # STEP 5: SUMMARIZE - Generate summary briefing
        logger.info("Step 5: Generating briefing...")
        briefing = await self.summarizer_agent.create_briefing(
            analysis_results=analysis_results,
            days_back=days_back
        )
        
        # STEP 6: SAVE - Save briefing to database
        briefing_date = datetime.now().strftime("%Y-%m-%d")
        data_end_date = datetime.now().isoformat()
        data_start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        self.db.save_briefing(
            briefing_date=briefing_date,
            summary_text=briefing.get("summary", ""),
            briefing_json=briefing,
            data_start_date=data_start_date,
            data_end_date=data_end_date
        )
        
        workflow_duration = (datetime.now() - workflow_start).total_seconds()
        
        logger.info(f"Workflow completed in {workflow_duration:.2f} seconds")
        
        return {
            "status": "success",
            "duration_seconds": workflow_duration,
            "workflow": "collect → enrich → analyze → summarize",
            "data_collected": {
                "news_articles": news_inserted,
                "funding_rounds": signals_inserted["funding"],
                "launches": signals_inserted["launches"],
                "github_repositories": github_inserted["repositories"],
                "github_signals": github_inserted["signals"]
            },
            "briefing_date": briefing_date,
            "briefing": briefing
        }
    
    async def run_data_collection_only(self) -> Dict:
        """Run only data collection and storage (skip enrichment, analysis, summarization)."""
        logger.info("Running data collection only...")
        
        collected_data = await self.collect_all_data()
        
        news_inserted = await self.store_news_articles(collected_data["news"])
        signals_inserted = await self.store_startup_signals(collected_data["startup"])
        github_inserted = await self.store_github_signals(collected_data["github"])
        
        return {
            "status": "success",
            "data_collected": {
                "news_articles": news_inserted,
                "funding_rounds": signals_inserted["funding"],
                "launches": signals_inserted["launches"],
                "github_repositories": github_inserted["repositories"],
                "github_signals": github_inserted["signals"]
            }
        }
    
    async def close(self):
        """Cleanup resources including HTTP clients and LLM clients."""
        logger.info("Closing orchestrator resources...")
        
        # Close orchestrator's HTTP client
        await self.http_client.aclose()
        
        # Close LLM clients from analysis and summarizer agents
        if hasattr(self.analysis_agent, 'llm') and hasattr(self.analysis_agent.llm, 'close'):
            await self.analysis_agent.llm.close()
            logger.info("Analysis agent LLM client closed")
        
        if hasattr(self.summarizer_agent, 'llm') and hasattr(self.summarizer_agent.llm, 'close'):
            await self.summarizer_agent.llm.close()
            logger.info("Summarizer agent LLM client closed")
        
        logger.info("Orchestrator resources closed successfully")
```

### Integration with FastAPI

**Note:** The actual API endpoint implementation is in **10-api-endpoints.md**. This is a simplified example for reference.

**File:** `backend/src/api/routes.py`

```python
from fastapi import APIRouter
import asyncio
from orchestrator.agent import OrchestratorAgent

router = APIRouter()
orchestrator = OrchestratorAgent()

@router.post("/orchestrator/run")
async def trigger_workflow(days_back: int = 7):
    """Trigger full workflow in background: collect → enrich → analyze → summarize."""
    async def run_workflow():
        try:
            await orchestrator.run_full_workflow(days_back=days_back)
        except Exception as e:
            logger.error(f"Workflow error: {e}")
    
    # Use asyncio.create_task for async background execution
    asyncio.create_task(run_workflow())
    
    return {
        "status": "started", 
        "message": "Full workflow started in background",
        "workflow": "collect → enrich → analyze → summarize"
    }

@router.post("/orchestrator/collect")
async def trigger_collection():
    """Trigger data collection only (no enrichment/analysis)."""
    async def run_collection():
        try:
            await orchestrator.run_data_collection_only()
        except Exception as e:
            logger.error(f"Collection error: {e}")
    
    # Use asyncio.create_task for async background execution
    asyncio.create_task(run_collection())
    
    return {
        "status": "started", 
        "message": "Data collection started in background"
    }
```

**Important:** For the complete, production-ready API implementation with proper error handling and status tracking, see **10-api-endpoints.md**.

### Error Handling

- **Agent Unavailable**: Log error, continue with available agents
- **Database Errors**: Log error, return partial results
- **Timeout**: Retry with exponential backoff (max 3 retries)
- **Invalid Data**: Skip invalid entries, log warnings
- **Partial Failures**: Continue workflow with available data

### Logging

Use structured logging:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Configuration

Ensure these settings are configured in `.env`:
- `NEWS_SCRAPER_URL` - URL of news-scraper agent (default: http://localhost:3001)
- `STARTUP_API_URL` - URL of startup-api agent (default: http://localhost:3002)
- `GITHUB_MONITOR_URL` - URL of github-monitor agent (default: http://localhost:3003)
- `DATABASE_PATH` - Path to SQLite database (in-sandbox)

### Testing

```python
import asyncio
from orchestrator.agent import OrchestratorAgent

async def test_orchestrator():
    agent = OrchestratorAgent()
    
    # Test data collection only
    result = await agent.run_data_collection_only()
    print(result)
    
    # Test full workflow
    result = await agent.run_full_workflow(days_back=7)
    print(result)
    
    await agent.close()

# Run test
asyncio.run(test_orchestrator())
```

### Deliverables

1. Complete orchestrator agent implementation
2. Data collection methods for all three Docker MCP Hub agents
3. Parallel data collection coordination
4. Data storage coordination for all data types
5. Full workflow orchestration: collect → enrich → analyze → summarize
6. Error handling and retry logic
7. Logging and monitoring
8. FastAPI route integration
9. Background task support

### Next Steps

After completing the orchestrator, proceed to:
- **06-database-setup.md** - Set up database schema including GitHub signals
- **07-enrichment-agent.md** - Implement enrichment agent for data enhancement
- **08-analysis-agent.md** - Implement analysis agent that processes stored data
- **09-summarizer-agent.md** - Implement summarizer agent that creates JSON briefings
