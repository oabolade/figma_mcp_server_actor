"""Pydantic models for data validation."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class FundingRound(BaseModel):
    """Funding round model."""
    name: str
    type: str  # Series A, Series B, Seed, etc.
    amount: str
    amount_numeric: Optional[float] = None
    currency: str = "USD"
    date: str
    description: Optional[str] = None
    investors: List[str] = []
    category: Optional[str] = None
    link: Optional[HttpUrl] = None
    source: str


class Launch(BaseModel):
    """Product/startup launch model."""
    name: str
    type: str  # "product" or "startup"
    description: Optional[str] = None
    date: str
    category: Optional[str] = None
    link: Optional[HttpUrl] = None
    founders: List[str] = []
    tagline: Optional[str] = None
    source: str


class FundingResponse(BaseModel):
    """Funding rounds response."""
    count: int
    funding_rounds: List[FundingRound]


class LaunchResponse(BaseModel):
    """Launches response."""
    count: int
    launches: List[Launch]


class Event(BaseModel):
    """Industry event model."""
    name: str
    type: str
    date: str
    location: Optional[str] = None
    description: Optional[str] = None
    link: Optional[HttpUrl] = None
    source: str


class EventResponse(BaseModel):
    """Events response."""
    count: int
    events: List[Event]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: str

