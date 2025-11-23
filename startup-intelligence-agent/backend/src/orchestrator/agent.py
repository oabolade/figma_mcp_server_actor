import asyncio
import httpx
import json
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
            
            # Parse JSON with error handling
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from news-scraper agent: {e}")
                logger.error(f"Response text (first 500 chars): {response.text[:500]}")
                return {"error": f"Invalid JSON response: {str(e)}", "sources": {}, "total": 0}
            
            logger.info(f"Retrieved {data.get('total', 0)} news articles")
            return data
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
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
            
            # Parse funding JSON with error handling
            if funding_response.status_code == 200:
                try:
                    funding_data = funding_response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in funding response: {e}")
                    logger.error(f"Response text (first 500 chars): {funding_response.text[:500]}")
                    funding_data = {"funding_rounds": []}
            else:
                funding_data = {"funding_rounds": []}
            
            # Collect launches
            launches_response = await self.http_client.get(
                f"{settings.STARTUP_API_URL}/launches",
                params={"days": 7}
            )
            
            # Parse launches JSON with error handling
            if launches_response.status_code == 200:
                try:
                    launches_data = launches_response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in launches response: {e}")
                    logger.error(f"Response text (first 500 chars): {launches_response.text[:500]}")
                    launches_data = {"launches": []}
            else:
                launches_data = {"launches": []}
            
            logger.info(f"Retrieved {len(funding_data.get('funding_rounds', []))} funding rounds")
            logger.info(f"Retrieved {len(launches_data.get('launches', []))} launches")
            
            return {
                "funding": funding_data.get("funding_rounds", []),
                "launches": launches_data.get("launches", [])
            }
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
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
            
            # Parse trending JSON with error handling
            if trending_response.status_code == 200:
                try:
                    trending_data = trending_response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in trending response: {e}")
                    logger.error(f"Response text (first 500 chars): {trending_response.text[:500]}")
                    trending_data = {"repositories": []}
            else:
                trending_data = {"repositories": []}
            
            # Collect technical signals
            signals_response = await self.http_client.get(
                f"{settings.GITHUB_MONITOR_URL}/signals",
                params={"days": 7, "keywords": "startup,AI,tech"}
            )
            
            # Parse signals JSON with error handling
            if signals_response.status_code == 200:
                try:
                    signals_data = signals_response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in signals response: {e}")
                    logger.error(f"Response text (first 500 chars): {signals_response.text[:500]}")
                    signals_data = {"signals": []}
            else:
                signals_data = {"signals": []}
            
            logger.info(f"Retrieved {len(trending_data.get('repositories', []))} trending repositories")
            logger.info(f"Retrieved {len(signals_data.get('signals', []))} technical signals")
            
            return {
                "trending": trending_data.get("repositories", []),
                "signals": signals_data.get("signals", [])
            }
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
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
        
        # Close analysis and summarizer agents (they will close their LLM clients)
        if hasattr(self.analysis_agent, 'close'):
            await self.analysis_agent.close()
            logger.info("Analysis agent closed")
        
        if hasattr(self.summarizer_agent, 'close'):
            await self.summarizer_agent.close()
            logger.info("Summarizer agent closed")
        
        logger.info("Orchestrator resources closed successfully")