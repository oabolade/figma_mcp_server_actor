# Prompt 9: Summarizer + Output Agent

## Objective

Create a summarizer and output agent that runs inside the E2B sandbox to generate final daily briefings, format insights into structured JSON, and produce searchable intelligence threads for the UI.

## Requirements

### Summarizer Agent Responsibilities

The Summarizer Agent operates **inside the E2B sandbox** and:

1. **Generate Daily Briefing**
   - Create executive summary of the day's intelligence
   - Consolidate analysis results into coherent narrative
   - Highlight most important insights

2. **Format Structured Output**
   - Transform analysis results into UI-ready JSON format
   - Organize trends, funding, launches, and opportunities
   - Ensure consistent data structure

3. **Create Searchable Intelligence Threads**
   - Generate detailed intelligence threads for each major trend
   - Link related items across categories
   - Add metadata for searchability

4. **Produce Final JSON Briefing**
   - Combine all components into final briefing structure
   - Include summary, trends, funding, launches, opportunities
   - Format for frontend consumption

### Implementation

**File:** `backend/src/summarizer/agent.py`

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

from database.db import Database
from config.settings import settings
from llm.client import LLMClient

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self):
        self.db = Database(settings.DATABASE_PATH)
        self.llm = LLMClient(
            provider=settings.LLM_PROVIDER,
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY
        )
    
    def get_summary_prompt_template(self) -> str:
        """Get the prompt template for generating daily summary."""
        return """You are a startup intelligence analyst creating a daily briefing summary.

Based on the analysis results below, create a concise executive summary (2-3 paragraphs) that highlights:
1. The most significant trends and developments
2. Key funding activity and notable rounds
3. Important product launches
4. Top opportunities for founders and investors

**Analysis Results:**
{analysis_results}

**Output:**
Provide a well-structured summary paragraph that captures the essence of today's startup intelligence. Make it engaging and actionable."""

    async def create_briefing(self, analysis_results: Dict, days_back: int = 7) -> Dict:
        """Create a complete daily briefing from analysis results."""
        logger.info("Creating daily briefing...")
        
        briefing_start = datetime.now()
        
        # Get fresh data for briefing
        news_articles = self.db.get_recent_news(days=days_back, limit=50)
        funding_rounds = self.db.get_recent_funding(days=days_back, limit=50)
        launches = self.db.get_recent_launches(days=days_back, limit=50)
        github_repos = self.db.get_recent_github_repos(days=days_back, limit=30)
        
        # Extract trends from analysis
        trends = analysis_results.get("results", {}).get("trends", [])
        competitor_moves = analysis_results.get("results", {}).get("competitor_moves", [])
        founder_opportunities = analysis_results.get("results", {}).get("opportunities_for_founders", [])
        investor_opportunities = analysis_results.get("results", {}).get("opportunities_for_investors", [])
        
        # Generate executive summary
        summary = await self._generate_summary(analysis_results)
        
        # Format funding rounds for briefing
        briefing_funding = self._format_funding_rounds(funding_rounds)
        
        # Format product launches for briefing
        briefing_launches = self._format_launches(launches)
        
        # Create intelligence threads
        intelligence_threads = await self._create_intelligence_threads(trends, news_articles)
        
        # Build final briefing JSON
        briefing = {
            "briefing_date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "data_period": {
                "start": (datetime.now() - timedelta(days=days_back)).isoformat(),
                "end": datetime.now().isoformat(),
                "days": days_back
            },
            "summary": summary,
            "trends": self._format_trends(trends),
            "funding_rounds": briefing_funding[:15],  # Top 15
            "product_launches": briefing_launches[:15],  # Top 15
            "competitor_moves": self._format_competitor_moves(competitor_moves)[:10],  # Top 10
            "opportunities_for_founders": self._format_founder_opportunities(founder_opportunities)[:10],  # Top 10
            "opportunities_for_investors": self._format_investor_opportunities(investor_opportunities)[:10],  # Top 10
            "intelligence_threads": intelligence_threads,
            "statistics": {
                "news_articles_analyzed": len(news_articles),
                "funding_rounds_analyzed": len(funding_rounds),
                "launches_analyzed": len(launches),
                "trends_identified": len(trends),
                "opportunities_identified": len(founder_opportunities) + len(investor_opportunities)
            }
        }
        
        briefing_duration = (datetime.now() - briefing_start).total_seconds()
        logger.info(f"Briefing created in {briefing_duration:.2f} seconds")
        
        return briefing
    
    async def _generate_summary(self, analysis_results: Dict) -> str:
        """Generate executive summary using LLM."""
        try:
            prompt = self.get_summary_prompt_template().format(
                analysis_results=json.dumps(analysis_results, indent=2)
            )
            
            summary = await self.llm.complete(prompt, temperature=0.8, max_tokens=500)
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback to template-based summary
            return self._generate_fallback_summary(analysis_results)
    
    def _generate_fallback_summary(self, analysis_results: Dict) -> str:
        """Generate a fallback summary if LLM fails."""
        trends = analysis_results.get("results", {}).get("trends", [])
        funding_count = len(analysis_results.get("results", {}).get("competitor_moves", []))
        opportunities = len(analysis_results.get("results", {}).get("opportunities_for_founders", []))
        
        summary = f"Today's startup intelligence reveals {len(trends)} key trends across the ecosystem. "
        summary += f"We've identified {funding_count} significant market moves and {opportunities} actionable opportunities. "
        summary += "Key areas of interest include emerging technologies, strategic funding rounds, and market gaps."
        
        return summary
    
    def _format_trends(self, trends: List[Dict]) -> List[Dict]:
        """Format trends for briefing output."""
        formatted = []
        for trend in trends:
            formatted.append({
                "title": trend.get("title", "Unnamed Trend"),
                "description": trend.get("description", ""),
                "signals": trend.get("signals", []),
                "confidence": trend.get("confidence", "medium"),
                "sector": trend.get("sector", "General"),
                "evidence": trend.get("evidence", [])[:5]  # Top 5 evidence points
            })
        return formatted
    
    def _format_funding_rounds(self, funding_rounds: List[Dict]) -> List[Dict]:
        """Format funding rounds for briefing output."""
        formatted = []
        for funding in funding_rounds:
            formatted.append({
                "name": funding.get("company_name", "Unknown Company"),
                "amount": funding.get("amount", "N/A"),
                "type": funding.get("funding_type", "N/A"),
                "date": funding.get("date", ""),
                "description": funding.get("description", ""),
                "investors": json.loads(funding.get("investors", "[]")) if isinstance(funding.get("investors"), str) else funding.get("investors", []),
                "category": funding.get("category", ""),
                "link": funding.get("link", ""),
                "industry": funding.get("industry", ""),
                "stage": funding.get("stage", "")
            })
        return sorted(formatted, key=lambda x: self._parse_funding_amount(x.get("amount", "$0")), reverse=True)
    
    def _format_launches(self, launches: List[Dict]) -> List[Dict]:
        """Format product launches for briefing output."""
        formatted = []
        for launch in launches:
            formatted.append({
                "name": launch.get("name", "Unknown Product"),
                "description": launch.get("description", ""),
                "date": launch.get("date", ""),
                "category": launch.get("category", ""),
                "product_category": launch.get("product_category", ""),
                "link": launch.get("link", ""),
                "tagline": launch.get("tagline", ""),
                "founders": json.loads(launch.get("founders", "[]")) if isinstance(launch.get("founders"), str) else launch.get("founders", []),
                "technologies": json.loads(launch.get("technologies", "[]")) if isinstance(launch.get("technologies"), str) else launch.get("technologies", [])
            })
        return formatted
    
    def _format_competitor_moves(self, competitor_moves: List[Dict]) -> List[Dict]:
        """Format competitor moves for briefing output."""
        formatted = []
        for move in competitor_moves:
            formatted.append({
                "company": move.get("company", "Unknown Company"),
                "move_type": move.get("move_type", "unknown"),
                "description": move.get("description", ""),
                "significance": move.get("significance", ""),
                "date": move.get("date", "")
            })
        return formatted
    
    def _format_founder_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Format founder opportunities for briefing output."""
        formatted = []
        for opp in opportunities:
            formatted.append({
                "title": opp.get("title", "Untitled Opportunity"),
                "description": opp.get("description", ""),
                "reasoning": opp.get("reasoning", ""),
                "market_size_indicator": opp.get("market_size_indicator", "unknown"),
                "urgency": opp.get("urgency", "medium"),
                "category": opp.get("category", "general")
            })
        return formatted
    
    def _format_investor_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Format investor opportunities for briefing output."""
        formatted = []
        for opp in opportunities:
            formatted.append({
                "title": opp.get("title", "Untitled Opportunity"),
                "description": opp.get("description", ""),
                "reasoning": opp.get("reasoning", ""),
                "sector": opp.get("sector", "General"),
                "stage_preference": opp.get("stage_preference", "flexible"),
                "risk_level": opp.get("risk_level", "medium"),
                "potential_return": opp.get("potential_return", "medium")
            })
        return formatted
    
    async def _create_intelligence_threads(self, trends: List[Dict], news_articles: List[Dict]) -> List[Dict]:
        """Create searchable intelligence threads for major trends."""
        threads = []
        
        # Create a thread for each major trend (top 5)
        top_trends = sorted(trends, key=lambda x: x.get("confidence", "low") == "high", reverse=True)[:5]
        
        for trend in top_trends:
            # Find related articles
            trend_keywords = trend.get("signals", [])
            related_articles = self._find_related_articles(news_articles, trend_keywords)
            
            thread = {
                "thread_id": f"trend_{trend.get('title', 'unknown').lower().replace(' ', '_')}",
                "title": trend.get("title", "Unknown Trend"),
                "description": trend.get("description", ""),
                "sector": trend.get("sector", "General"),
                "confidence": trend.get("confidence", "medium"),
                "related_articles": [
                    {
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", ""),
                        "timestamp": article.get("timestamp", "")
                    }
                    for article in related_articles[:5]
                ],
                "evidence": trend.get("evidence", []),
                "created_at": datetime.now().isoformat()
            }
            threads.append(thread)
        
        return threads
    
    def _find_related_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Find articles related to keywords."""
        related = []
        keyword_str = " ".join(keywords).lower()
        
        for article in articles:
            title = article.get("title", "").lower()
            summary = article.get("summary", "").lower()
            text = f"{title} {summary}"
            
            if any(keyword.lower() in text for keyword in keywords):
                related.append(article)
        
        return related[:10]  # Return top 10 matches
    
    def _parse_funding_amount(self, amount_str: str) -> float:
        """Parse funding amount string to numeric value for sorting."""
        try:
            # Remove currency symbols and spaces
            amount_str = amount_str.replace("$", "").replace(",", "").strip()
            
            # Handle "M" (millions) and "B" (billions)
            if "B" in amount_str.upper():
                value = float(amount_str.upper().replace("B", "")) * 1_000_000_000
            elif "M" in amount_str.upper():
                value = float(amount_str.upper().replace("M", "")) * 1_000_000
            elif "K" in amount_str.upper():
                value = float(amount_str.upper().replace("K", "")) * 1_000
            else:
                value = float(amount_str)
            
            return value
        except (ValueError, AttributeError):
            return 0.0
```

### Briefing JSON Structure

The final briefing follows this structure:

```json
{
  "briefing_date": "2024-01-15",
  "generated_at": "2024-01-15T10:30:00Z",
  "data_period": {
    "start": "2024-01-08T10:30:00Z",
    "end": "2024-01-15T10:30:00Z",
    "days": 7
  },
  "summary": "Executive summary paragraph...",
  "trends": [...],
  "funding_rounds": [...],
  "product_launches": [...],
  "competitor_moves": [...],
  "opportunities_for_founders": [...],
  "opportunities_for_investors": [...],
  "intelligence_threads": [...],
  "statistics": {...}
}
```

### Deliverables

1. Complete summarizer agent implementation
2. Executive summary generation using LLM
3. Structured output formatting for all data types
4. Intelligence thread creation for searchability
5. Fallback summary generation
6. Funding amount parsing for sorting
7. Related article linking
8. Error handling and logging

### Testing

```python
import asyncio
from summarizer.agent import SummarizerAgent

async def test_summarizer():
    agent = SummarizerAgent()
    
    # Mock analysis results
    analysis_results = {
        "results": {
            "trends": [...],
            "competitor_moves": [...],
            "opportunities_for_founders": [...],
            "opportunities_for_investors": [...]
        }
    }
    
    briefing = await agent.create_briefing(analysis_results, days_back=7)
    print(f"Briefing created for {briefing['briefing_date']}")
    print(f"Summary: {briefing['summary'][:200]}...")

asyncio.run(test_summarizer())
```

### Next Steps

After completing the summarizer agent, proceed to:
- **10-api-endpoints.md** - Create FastAPI endpoints to expose the briefing
- **11-frontend-ui.md** - Build the frontend UI to display the briefing
