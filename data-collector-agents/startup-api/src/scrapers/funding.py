"""Funding rounds scraper."""
from typing import List, Dict
from datetime import datetime, timedelta
import httpx
import asyncio

from ..config import TECHCRUNCH_FUNDING_RSS, TIMEOUT
from ..providers.rss_fallback import parse_funding_from_rss


async def get_funding_rounds(
    keyword: str = None,
    days: int = 7,
    min_amount: float = None
) -> List[Dict]:
    """
    Get recent funding rounds.
    
    Args:
        keyword: Filter by keyword
        days: Number of days to look back
        min_amount: Minimum funding amount filter
    
    Returns:
        List of funding round dictionaries
    """
    try:
        # Use RSS feed as primary source
        funding_rounds = await parse_funding_from_rss(TECHCRUNCH_FUNDING_RSS, days)
        
        # Filter by keyword if provided
        if keyword:
            keyword_lower = keyword.lower()
            funding_rounds = [
                fr for fr in funding_rounds
                if keyword_lower in fr.get("name", "").lower() or
                   keyword_lower in fr.get("description", "").lower() or
                   keyword_lower in str(fr.get("category", "")).lower()
            ]
        
        # Filter by minimum amount if provided
        if min_amount:
            funding_rounds = [
                fr for fr in funding_rounds
                if fr.get("amount_numeric") and fr["amount_numeric"] >= min_amount
            ]
        
        return funding_rounds
    except Exception as e:
        print(f"Error getting funding rounds: {e}")
        return []


async def get_all_funding(days: int = 7) -> List[Dict]:
    """Get all funding rounds from all sources."""
    # For now, use RSS feed
    # In production, you could add Crunchbase API, AngelList, etc.
    return await get_funding_rounds(days=days)

