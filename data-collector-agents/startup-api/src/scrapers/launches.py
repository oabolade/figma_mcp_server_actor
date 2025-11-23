"""Product launches scraper."""
from typing import List, Dict
from datetime import datetime, timedelta
import httpx
import asyncio

from ..config import TECHCRUNCH_STARTUPS_RSS, TIMEOUT
from ..providers.rss_fallback import parse_launches_from_rss


async def get_launches(
    keyword: str = None,
    days: int = 7,
    category: str = None
) -> List[Dict]:
    """
    Get recent product launches.
    
    Args:
        keyword: Filter by keyword
        days: Number of days to look back
        category: Filter by category
    
    Returns:
        List of launch dictionaries
    """
    try:
        # Use RSS feed as primary source
        launches = await parse_launches_from_rss(TECHCRUNCH_STARTUPS_RSS, days)
        
        # Filter by keyword if provided
        if keyword:
            keyword_lower = keyword.lower()
            launches = [
                launch for launch in launches
                if keyword_lower in launch.get("name", "").lower() or
                   keyword_lower in launch.get("description", "").lower() or
                   keyword_lower in str(launch.get("category", "")).lower()
            ]
        
        # Filter by category if provided
        if category:
            category_lower = category.lower()
            launches = [
                launch for launch in launches
                if category_lower in str(launch.get("category", "")).lower()
            ]
        
        return launches
    except Exception as e:
        print(f"Error getting launches: {e}")
        return []


async def get_all_launches(days: int = 7) -> List[Dict]:
    """Get all launches from all sources."""
    # For now, use RSS feed
    # In production, you could add ProductHunt API, etc.
    return await get_launches(days=days)

