"""GitHub Monitor Agent - Main entry point."""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, List
import logging

from .config import PORT, CACHE_TTL
from .models.schemas import (
    TrendingResponse, SignalsResponse, HealthResponse,
    Repository, Signal
)
from .agent.monitor import get_trending_repositories, get_repositories_by_keywords
from .agent.signals import extract_signals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Monitor Agent",
    description="Docker MCP Hub agent that monitors GitHub repositories for trending projects and technical signals",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache
_cache = {}
_cache_ttl = CACHE_TTL  # Use CACHE_TTL from config (respects environment variable)


def get_cache_key(endpoint: str, **kwargs) -> str:
    """Generate cache key."""
    key = f"{endpoint}"
    if kwargs:
        key += "?" + "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return key


def get_cached(key: str):
    """Get from cache."""
    if key in _cache:
        cached_time, value = _cache[key]
        if (datetime.now() - cached_time).total_seconds() < _cache_ttl:
            return value
        del _cache[key]
    return None


def set_cache(key: str, value):
    """Set cache."""
    _cache[key] = (datetime.now(), value)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        service="github-monitor",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/trending", response_model=TrendingResponse)
async def get_trending(
    language: Optional[str] = Query(None, description="Filter by programming language"),
    since: str = Query("daily", description="Timeframe: daily, weekly, monthly"),
    limit: int = Query(25, ge=1, le=100, description="Number of repos to return")
):
    """Get trending repositories."""
    try:
        cache_key = get_cache_key("trending", language=language, since=since, limit=limit)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        repos = await get_trending_repositories(
            language=language,
            since=since,
            limit=limit
        )
        
        response = TrendingResponse(
            count=len(repos),
            since=since,
            repositories=repos
        )
        
        set_cache(cache_key, response)
        return response
    except Exception as e:
        logger.error(f"Error getting trending repos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals", response_model=SignalsResponse)
async def get_signals(
    keywords: Optional[str] = Query(None, description="Comma-separated keywords"),
    days: int = Query(7, ge=1, le=30, description="Lookback period in days"),
    min_stars: int = Query(10, ge=1, description="Minimum star count")
):
    """Extract technical signals from GitHub activity."""
    try:
        keyword_list = keywords.split(",") if keywords else None
        cache_key = get_cache_key("signals", keywords=keywords, days=days, min_stars=min_stars)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        signals_list = await extract_signals(
            keywords=keyword_list,
            days=days,
            min_stars=min_stars
        )
        
        response = SignalsResponse(
            count=len(signals_list),
            signals=signals_list
        )
        
        set_cache(cache_key, response)
        return response
    except Exception as e:
        logger.error(f"Error extracting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_repositories(
    keywords: Optional[str] = Query(None, description="Comma-separated keywords"),
    min_stars: int = Query(10, ge=1, description="Minimum star count"),
    days: int = Query(7, ge=1, le=30, description="Days to look back")
):
    """Search repositories by keywords."""
    try:
        keyword_list = keywords.split(",") if keywords else None
        repos = await get_repositories_by_keywords(
            keywords=keyword_list or [],
            min_stars=min_stars,
            days=days
        )
        
        return {
            "count": len(repos),
            "repositories": repos
        }
    except Exception as e:
        logger.error(f"Error searching repos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/repositories/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    """Get specific repository details."""
    # Placeholder - would fetch from GitHub API
    return {
        "name": repo,
        "full_name": f"{owner}/{repo}",
        "message": "Repository details endpoint - to be implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,  # Use app object directly instead of string to avoid module path issues
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )

