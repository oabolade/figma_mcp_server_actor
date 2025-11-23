"""Startup API Agent - Main entry point."""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import logging

from .config import PORT, CACHE_TTL
from .models.schemas import (
    FundingResponse, LaunchResponse, EventResponse, HealthResponse
)
from .scrapers.funding import get_funding_rounds, get_all_funding
from .scrapers.launches import get_launches, get_all_launches
from .scrapers.events import get_events, get_all_events
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Startup API Agent",
    description="Docker MCP Hub agent that aggregates startup activity signals",
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

# In-memory cache (simple implementation)
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
        service="startup-api",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/funding", response_model=FundingResponse)
async def get_funding(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    min_amount: Optional[float] = Query(None, description="Minimum funding amount")
):
    """Get recent funding rounds."""
    try:
        cache_key = get_cache_key("funding", keyword=keyword, days=days, min_amount=min_amount)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        funding_rounds = await get_funding_rounds(
            keyword=keyword,
            days=days,
            min_amount=min_amount
        )
        
        response = FundingResponse(
            count=len(funding_rounds),
            funding_rounds=funding_rounds
        )
        
        set_cache(cache_key, response)
        return response
    except Exception as e:
        logger.error(f"Error getting funding rounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/launches", response_model=LaunchResponse)
async def get_launches_endpoint(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get recent product launches."""
    try:
        cache_key = get_cache_key("launches", keyword=keyword, days=days, category=category)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        launches_list = await get_launches(
            keyword=keyword,
            days=days,
            category=category
        )
        
        response = LaunchResponse(
            count=len(launches_list),
            launches=launches_list
        )
        
        set_cache(cache_key, response)
        return response
    except Exception as e:
        logger.error(f"Error getting launches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events", response_model=EventResponse)
async def get_events_endpoint(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    days: int = Query(30, ge=1, le=90, description="Days to look ahead")
):
    """Get industry events."""
    try:
        cache_key = get_cache_key("events", keyword=keyword, days=days)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        events_list = await get_events(
            keyword=keyword,
            days=days
        )
        
        response = EventResponse(
            count=len(events_list),
            events=events_list
        )
        
        set_cache(cache_key, response)
        return response
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/all")
async def get_all(
    days: int = Query(7, ge=1, le=30, description="Days to look back")
):
    """Get all data aggregated."""
    try:
        cache_key = get_cache_key("all", days=days)
        cached = get_cached(cache_key)
        if cached:
            return cached
        
        funding_rounds, launches_list, events_list = await asyncio.gather(
            get_all_funding(days=days),
            get_all_launches(days=days),
            get_all_events(days=days)
        )
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "funding": {
                "count": len(funding_rounds),
                "funding_rounds": funding_rounds
            },
            "launches": {
                "count": len(launches_list),
                "launches": launches_list
            },
            "events": {
                "count": len(events_list),
                "events": events_list
            }
        }
        
        set_cache(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,  # Use app object directly instead of string to avoid module path issues
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )

