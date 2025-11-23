"""GitHub monitoring agent."""
from typing import List, Dict, Optional
from datetime import datetime

from ..github.api_client import get_github_client


async def get_trending_repositories(
    language: Optional[str] = None,
    since: str = "daily",
    limit: int = 25
) -> List[Dict]:
    """Get trending repositories."""
    client = get_github_client()
    repos = await client.get_trending_repos(
        language=language,
        since=since,
        limit=limit
    )
    
    # Add signal analysis
    for repo in repos:
        repo["signals"] = analyze_repository_signals(repo)
    
    return repos


async def get_repositories_by_keywords(
    keywords: List[str],
    min_stars: int = 10,
    days: int = 7
) -> List[Dict]:
    """Get repositories by keywords."""
    client = get_github_client()
    repos = await client.search_repos(
        keywords=keywords,
        min_stars=min_stars,
        days=days
    )
    
    return repos


def analyze_repository_signals(repo: Dict) -> Dict:
    """Analyze repository for startup/tech signals."""
    signals = {
        "growth_rate": "medium",
        "developer_activity": "active",
        "startup_indicator": False
    }
    
    description = (repo.get("description") or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    
    # Startup indicators
    startup_keywords = ["startup", "saas", "product", "app", "platform", "api"]
    if any(kw in description or any(kw in topic for topic in topics) for kw in startup_keywords):
        signals["startup_indicator"] = True
    
    # Growth rate based on stars
    stars = repo.get("stars", 0)
    if stars > 1000:
        signals["growth_rate"] = "high"
    elif stars > 100:
        signals["growth_rate"] = "medium"
    else:
        signals["growth_rate"] = "low"
    
    # Developer activity based on recent updates
    updated_at = repo.get("updated_at", "")
    if updated_at:
        try:
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(updated.tzinfo) - updated).days
            if days_since_update < 7:
                signals["developer_activity"] = "very_active"
            elif days_since_update < 30:
                signals["developer_activity"] = "active"
            else:
                signals["developer_activity"] = "inactive"
        except:
            pass
    
    return signals

