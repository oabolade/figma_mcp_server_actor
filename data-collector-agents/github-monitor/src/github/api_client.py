"""GitHub API client."""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio

from ..config import GITHUB_TOKEN, GITHUB_API_URL, TIMEOUT


class GitHubAPIClient:
    """Async GitHub API client."""
    
    def __init__(self):
        self.base_url = GITHUB_API_URL
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-monitor-agent"
        }
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {GITHUB_TOKEN}"
        self.timeout = TIMEOUT / 1000  # Convert to seconds
    
    async def get_trending_repos(
        self,
        language: Optional[str] = None,
        since: str = "daily",
        limit: int = 25
    ) -> List[Dict]:
        """
        Get trending repositories.
        
        Note: GitHub doesn't have an official trending API.
        This uses the search API to find recently updated repositories.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build search query
                query_parts = ["stars:>10"]
                
                if language:
                    query_parts.append(f"language:{language}")
                
                # Sort by stars, created/updated recently
                sort = "stars"
                order = "desc"
                
                # Construct query
                query = "+".join(query_parts)
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "per_page": min(limit, 100)  # GitHub API max is 100
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                repos = []
                for item in data.get("items", [])[:limit]:
                    # Handle missing html_url - construct from full_name if needed
                    html_url = item.get("html_url", "")
                    if not html_url and item.get("full_name"):
                        # Construct GitHub URL from full_name as fallback
                        html_url = f"https://github.com/{item.get('full_name')}"
                    
                    repo = {
                        "name": item.get("name", ""),
                        "full_name": item.get("full_name", ""),
                        "description": item.get("description", ""),
                        "language": item.get("language", ""),
                        "stars": item.get("stargazers_count", 0),
                        "stars_today": 0,  # Would need to track over time
                        "forks": item.get("forks_count", 0),
                        "url": html_url if html_url else None,  # Use None instead of empty string
                        "created_at": item.get("created_at", ""),
                        "updated_at": item.get("updated_at", ""),
                        "topics": item.get("topics", []),
                        "signals": {}
                    }
                    repos.append(repo)
                
                return repos
        except Exception as e:
            print(f"Error fetching trending repos: {e}")
            return []
    
    async def search_repos(
        self,
        keywords: List[str],
        min_stars: int = 10,
        days: int = 7
    ) -> List[Dict]:
        """Search repositories by keywords."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build search query
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                query_parts = [f"stars:>={min_stars}", f"pushed:>={cutoff_date}"]
                
                if keywords:
                    keyword_query = "+".join(keywords)
                    query_parts.append(keyword_query)
                
                query = "+".join(query_parts)
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 100
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                repos = []
                for item in data.get("items", [])[:50]:  # Limit to 50
                    # Handle missing html_url - construct from full_name if needed
                    html_url = item.get("html_url", "")
                    if not html_url and item.get("full_name"):
                        # Construct GitHub URL from full_name as fallback
                        html_url = f"https://github.com/{item.get('full_name')}"
                    
                    repo = {
                        "name": item.get("name", ""),
                        "full_name": item.get("full_name", ""),
                        "description": item.get("description", ""),
                        "language": item.get("language", ""),
                        "stars": item.get("stargazers_count", 0),
                        "stars_today": 0,  # Would need to track over time
                        "forks": item.get("forks_count", 0),
                        "url": html_url if html_url else None,  # Use None instead of empty string
                        "created_at": item.get("created_at", ""),
                        "updated_at": item.get("updated_at", ""),
                        "topics": item.get("topics", []),
                        "signals": {}
                    }
                    repos.append(repo)
                
                return repos
        except Exception as e:
            print(f"Error searching repos: {e}")
            return []


# Singleton instance
_github_client = None


def get_github_client() -> GitHubAPIClient:
    """Get singleton GitHub API client."""
    global _github_client
    if _github_client is None:
        _github_client = GitHubAPIClient()
    return _github_client

