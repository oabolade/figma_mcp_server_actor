"""Pydantic models for data validation."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class Repository(BaseModel):
    """GitHub repository model."""
    name: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    stars_today: int = 0
    forks: int
    url: Optional[HttpUrl] = None  # Optional to handle missing html_url from API
    created_at: str
    updated_at: str
    topics: List[str] = []
    signals: Dict = {}


class Signal(BaseModel):
    """Technical signal model."""
    signal_type: str  # "emerging_technology", "startup_activity", "tech_trend"
    repository_name: Optional[str] = None
    repository_url: Optional[str] = None
    indicator: str  # Signal description/indicator text
    confidence: str  # "high", "medium", "low"
    date: str  # Date in YYYY-MM-DD format
    metadata: Optional[Dict] = None  # Additional data (keywords, stars, etc.)


class TrendingResponse(BaseModel):
    """Trending repositories response."""
    count: int
    since: str
    repositories: List[Repository]


class SignalsResponse(BaseModel):
    """Technical signals response."""
    count: int
    signals: List[Signal]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: str

