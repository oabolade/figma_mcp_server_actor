from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

from database.db import Database
from config.settings import settings
from llm.client import LLMClient

logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        self.db = Database(settings.DATABASE_PATH)
        self.llm = LLMClient(
            provider=settings.LLM_PROVIDER,
            model=settings.LLM_MODEL,
            api_key=settings.LLM_API_KEY
        )
    
    async def close(self):
        """Cleanup resources including HTTP client."""
        logger.info("Closing analysis agent resources...")
        if hasattr(self, 'llm') and hasattr(self.llm, 'close'):
            await self.llm.close()
            logger.info("Analysis agent LLM client closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.close()
    
    def get_analysis_prompt_template(self) -> str:
        """Get the prompt template for analysis."""
        return """You are a startup intelligence analyst with expertise in technology trends, startup ecosystems, and venture capital.

Analyze the following startup signals (news articles, funding events, launches, GitHub activity) and identify patterns, trends, and opportunities.

**Your Task:**

1. **Cluster Trends**
   - Group related items into thematic clusters (e.g., "AI Infrastructure", "Climate Tech", "Developer Tools")
   - Identify emerging sectors or early signals
   - Note pattern shifts and market movements

2. **Identify Competitor Moves**
   - Track strategic shifts and competitive positioning changes
   - Identify M&A activity and industry consolidation
   - Note competitor product launches and funding rounds

3. **Extract Opportunities for Founders**
   - Market gaps and unmet needs
   - Partnership opportunities
   - Emerging trends to leverage
   - Underserved market segments

4. **Extract Opportunities for Investors**
   - Hot sectors with high activity
   - Promising startups showing early traction
   - Emerging technology trends
   - Market timing indicators

**Input Data:**
{data_summary}

**Output Format (JSON):**
{{
  "trends": [
    {{
      "title": "Trend name",
      "description": "Detailed description",
      "signals": ["signal1", "signal2"],
      "confidence": "high|medium|low",
      "sector": "sector name",
      "evidence": ["evidence1", "evidence2"]
    }}
  ],
  "competitor_moves": [
    {{
      "company": "Company name",
      "move_type": "funding|acquisition|launch|pivot",
      "description": "What happened",
      "significance": "Why this matters",
      "date": "YYYY-MM-DD"
    }}
  ],
  "opportunities_for_founders": [
    {{
      "title": "Opportunity title",
      "description": "Detailed description",
      "reasoning": "Why this is an opportunity",
      "market_size_indicator": "small|medium|large",
      "urgency": "low|medium|high",
      "category": "market_gap|partnership|trend|segment"
    }}
  ],
  "opportunities_for_investors": [
    {{
      "title": "Opportunity title",
      "description": "Investment opportunity description",
      "reasoning": "Investment thesis",
      "sector": "sector name",
      "stage_preference": "early|growth|later",
      "risk_level": "low|medium|high",
      "potential_return": "low|medium|high"
    }}
  ]
}}

Provide your analysis as valid JSON only."""

    async def analyze_recent_data(self, days_back: int = 7) -> Dict:
        """Analyze recently collected and enriched data."""
        logger.info(f"Starting analysis for last {days_back} days...")
        
        analysis_start = datetime.now()
        
        # Collect enriched data from database
        news_articles = self.db.get_recent_news(days=days_back, enriched=True, limit=100)
        funding_rounds = self.db.get_recent_funding(days=days_back, enriched=True, limit=100)
        launches = self.db.get_recent_launches(days=days_back, enriched=True, limit=100)
        github_repos = self.db.get_recent_github_repos(days=days_back, enriched=True, limit=50)
        github_signals = self.db.get_recent_github_signals(days=days_back, limit=50)
        
        # Prepare data summary for LLM
        data_summary = self._prepare_data_summary({
            "news": news_articles,
            "funding": funding_rounds,
            "launches": launches,
            "github_repos": github_repos,
            "github_signals": github_signals
        })
        
        # Get analysis prompt
        prompt = self.get_analysis_prompt_template().format(data_summary=data_summary)
        
        # Call LLM for analysis
        logger.info("Calling LLM for analysis...")
        try:
            response = await self.llm.complete(prompt, temperature=0.7, max_tokens=4000)
            analysis_results = self._parse_llm_response(response)
            
            # Validate and enhance results
            analysis_results = self._validate_analysis_results(analysis_results)
            
            # Save analysis results to database
            data_start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            data_end_date = datetime.now().isoformat()
            
            self.db.save_analysis_result(
                analysis_type="comprehensive",
                date_start=data_start_date,
                date_end=data_end_date,
                results_json=analysis_results,
                model_used=settings.LLM_MODEL
            )
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
            logger.info(f"Found {len(analysis_results.get('trends', []))} trends, "
                       f"{len(analysis_results.get('competitor_moves', []))} competitor moves, "
                       f"{len(analysis_results.get('opportunities_for_founders', []))} founder opportunities, "
                       f"{len(analysis_results.get('opportunities_for_investors', []))} investor opportunities")
            
            return {
                "status": "success",
                "duration_seconds": analysis_duration,
                "results": analysis_results,
                "data_analyzed": {
                    "news_articles": len(news_articles),
                    "funding_rounds": len(funding_rounds),
                    "launches": len(launches),
                    "github_repositories": len(github_repos),
                    "github_signals": len(github_signals)
                }
            }
            
        except ValueError as e:
            # API key not configured - return empty results with helpful message
            logger.warning(f"LLM API key not configured: {e}")
            logger.info("Returning empty analysis results. Configure API key for full functionality.")
            return {
                "status": "error",
                "error": str(e),
                "message": "LLM API key not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.",
                "results": {
                    "trends": [],
                    "competitor_moves": [],
                    "opportunities_for_founders": [],
                    "opportunities_for_investors": []
                }
            }
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": {
                    "trends": [],
                    "competitor_moves": [],
                    "opportunities_for_founders": [],
                    "opportunities_for_investors": []
                }
            }
    
    def _prepare_data_summary(self, data: Dict) -> str:
        """Prepare a concise data summary for LLM analysis."""
        summary_parts = []
        
        # News summary
        news = data.get("news", [])
        if news:
            news_summary = f"\n**Recent News ({len(news)} articles):**\n"
            for article in news[:10]:  # Top 10 most recent
                news_summary += f"- {article.get('title', 'Untitled')} ({article.get('source', 'unknown')})\n"
            summary_parts.append(news_summary)
        
        # Funding summary
        funding = data.get("funding", [])
        if funding:
            funding_summary = f"\n**Recent Funding ({len(funding)} rounds):**\n"
            for round_data in funding[:10]:  # Top 10
                company = round_data.get('company_name', 'Unknown')
                amount = round_data.get('amount', 'N/A')
                funding_type = round_data.get('funding_type', 'N/A')
                funding_summary += f"- {company}: {amount} ({funding_type})\n"
            summary_parts.append(funding_summary)
        
        # Launches summary
        launches = data.get("launches", [])
        if launches:
            launches_summary = f"\n**Recent Launches ({len(launches)} products):**\n"
            for launch in launches[:10]:  # Top 10
                name = launch.get('name', 'Unknown')
                category = launch.get('category', 'N/A')
                launches_summary += f"- {name} ({category})\n"
            summary_parts.append(launches_summary)
        
        # GitHub summary
        github_repos = data.get("github_repos", [])
        if github_repos:
            github_summary = f"\n**Trending GitHub Repos ({len(github_repos)} repositories):**\n"
            for repo in github_repos[:10]:  # Top 10
                name = repo.get('full_name', 'Unknown')
                stars = repo.get('stars', 0)
                language = repo.get('language', 'N/A')
                github_summary += f"- {name}: {stars} stars ({language})\n"
            summary_parts.append(github_summary)
        
        # GitHub signals
        github_signals = data.get("github_signals", [])
        if github_signals:
            signals_summary = f"\n**Technical Signals ({len(github_signals)} signals):**\n"
            for signal in github_signals[:10]:  # Top 10
                signal_type = signal.get('signal_type', 'unknown')
                indicator = signal.get('indicator', 'N/A')
                signals_summary += f"- {signal_type}: {indicator}\n"
            summary_parts.append(signals_summary)
        
        return "\n".join(summary_parts)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response and extract JSON."""
        try:
            # Try to extract JSON from response
            # Handle cases where LLM wraps JSON in markdown code blocks
            json_str = None
            extraction_method = None
            
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                # Validate that closing marker was found
                if json_end != -1:
                    json_str = response[json_start:json_end].strip()
                    extraction_method = "markdown_json_block"
                else:
                    # Closing marker not found, log for debugging
                    logger.warning(
                        f"Closing ``` marker not found in markdown JSON block. "
                        f"Opening marker at position {json_start - 7}, response length: {len(response)}"
                    )
                    json_str = None
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                # Validate that closing marker was found
                if json_end != -1:
                    json_str = response[json_start:json_end].strip()
                    extraction_method = "markdown_code_block"
                else:
                    # Closing marker not found, log for debugging
                    logger.warning(
                        f"Closing ``` marker not found in markdown code block. "
                        f"Opening marker at position {json_start - 3}, response length: {len(response)}"
                    )
                    json_str = None
            
            # If we didn't extract from markdown blocks, try finding JSON object boundaries
            if json_str is None:
                json_start = response.find("{")
                json_end = response.rfind("}")
                
                # Validate that we found both opening and closing braces
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_str = response[json_start:json_end + 1]  # +1 to include closing brace
                    extraction_method = "brace_boundaries"
                else:
                    # No valid JSON found - provide detailed error message
                    error_details = {
                        "json_start_found": json_start != -1,
                        "json_end_found": json_end != -1,
                        "json_start_pos": json_start if json_start != -1 else None,
                        "json_end_pos": json_end if json_end != -1 else None,
                        "response_length": len(response),
                        "response_preview": response[:200] if len(response) > 200 else response
                    }
                    logger.error(f"No valid JSON structure found in response. Details: {error_details}")
                    raise json.JSONDecodeError(
                        f"No valid JSON structure found in response. "
                        f"Opening brace: {json_start != -1}, Closing brace: {json_end != -1}",
                        response,
                        json_start if json_start != -1 else 0
                    )
            
            # Parse JSON
            if extraction_method:
                logger.debug(f"Extracted JSON using method: {extraction_method}")
            parsed_json = json.loads(json_str)
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Error position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
            logger.error(f"Response preview (first 500 chars): {response[:500]}")
            logger.error(f"Response preview (last 200 chars): {response[-200:] if len(response) > 200 else response}")
            # Return empty structure
            return {
                "trends": [],
                "competitor_moves": [],
                "opportunities_for_founders": [],
                "opportunities_for_investors": []
            }
        except (ValueError, Exception) as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
            logger.error(f"Response preview (first 500 chars): {response[:500]}")
            # Return empty structure
            return {
                "trends": [],
                "competitor_moves": [],
                "opportunities_for_founders": [],
                "opportunities_for_investors": []
            }
    
    def _validate_analysis_results(self, results: Dict) -> Dict:
        """Validate and normalize analysis results."""
        validated = {
            "trends": results.get("trends", [])[:20],  # Limit to top 20
            "competitor_moves": results.get("competitor_moves", [])[:20],
            "opportunities_for_founders": results.get("opportunities_for_founders", [])[:15],
            "opportunities_for_investors": results.get("opportunities_for_investors", [])[:15]
        }
        
        # Add timestamps
        for category in validated:
            for item in validated[category]:
                if "created_at" not in item:
                    item["created_at"] = datetime.now().isoformat()
        
        return validated
    
    async def analyze_specific_trend(self, trend_keywords: List[str]) -> Dict:
        """Analyze a specific trend or topic."""
        logger.info(f"Analyzing specific trend: {', '.join(trend_keywords)}")
        
        # Find relevant data for the trend
        relevant_news = self.db.search_articles_by_keywords(trend_keywords, limit=50)
        relevant_funding = self.db.search_funding_by_keywords(trend_keywords, limit=50)
        relevant_launches = self.db.search_launches_by_keywords(trend_keywords, limit=50)
        
        # Prepare focused analysis
        prompt = f"""Analyze the following data related to the trend: {', '.join(trend_keywords)}

Focus on:
1. Trend strength and momentum
2. Key players and companies
3. Market size indicators
4. Investment opportunities
5. Potential risks

**Data:**
{self._prepare_data_summary({
    "news": relevant_news,
    "funding": relevant_funding,
    "launches": relevant_launches
})}

Provide a focused analysis as JSON."""
        
        response = await self.llm.complete(prompt, temperature=0.7, max_tokens=2000)
        return self._parse_llm_response(response)