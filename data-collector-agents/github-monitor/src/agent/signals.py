"""Technical signals extraction."""
from typing import List, Dict
from datetime import datetime

from ..github.api_client import get_github_client


async def extract_signals(
    keywords: List[str] = None,
    days: int = 7,
    min_stars: int = 10
) -> List[Dict]:
    """Extract technical signals from GitHub activity."""
    client = get_github_client()
    
    if not keywords:
        keywords = ["startup", "saas", "api", "platform"]
    
    repos = await client.search_repos(
        keywords=keywords,
        min_stars=min_stars,
        days=days
    )
    
    signals = []
    for repo in repos[:20]:  # Limit to top 20
        # Determine signal type based on keywords and repository characteristics
        signal_type = "emerging_technology"
        if any(kw in str(repo.get("topics", [])).lower() for kw in ["startup", "saas", "product"]):
            signal_type = "startup_activity"
        elif any(kw in str(repo.get("description", "")).lower() for kw in ["trend", "popular", "growing"]):
            signal_type = "tech_trend"
        
        # Adjust confidence based on stars and activity
        stars = repo.get("stars", 0)
        confidence = "medium"
        if stars > 500:
            confidence = "high"
        elif stars > 50:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Create indicator text from description
        repo_description = repo.get("description", "")
        indicator = f"Active repository: {repo.get('full_name')}"
        if repo_description:
            indicator = f"{indicator} - {repo_description[:200]}"  # Limit length
        
        # Build signal with correct field names matching database schema
        signal = {
            "signal_type": signal_type,
            "repository_name": repo.get("full_name", ""),
            "repository_url": repo.get("url", ""),
            "indicator": indicator,
            "confidence": confidence,
            "date": datetime.now().strftime("%Y-%m-%d"),  # Format as YYYY-MM-DD
            "metadata": {
                "keywords": keywords,
                "stars": stars,
                "forks": repo.get("forks", 0),
                "language": repo.get("language", ""),
                "topics": repo.get("topics", []),
                "original_timestamp": datetime.now().isoformat()
            }
        }
        
        signals.append(signal)
    
    return signals

