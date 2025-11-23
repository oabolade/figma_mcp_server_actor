# Prompt 3: Docker MCP Hub Agent - Startup API

## Objective

Build a Docker-based MCP Hub **agent** that runs inside a Docker container and actively aggregates startup activity signals including funding rounds, product launches, and industry events. This is an autonomous agent that wraps various APIs (Crunchbase, AngelList, Dealroom, ProductHunt) and RSS feeds to provide startup intelligence data.

## Requirements

### Agent Specifications

**Agent Name:** `startup-api`

**Agent Type:** Autonomous data collector agent running in Docker container via Docker MCP Hub

**Technology Stack:**
- Python 3.11+ (better for API integration)
- FastAPI for HTTP server
- httpx for async HTTP requests
- Pydantic for data validation

### Directory Structure

```
tools/startup-api/
├── src/
│   ├── main.py
│   ├── scrapers/
│   │   ├── funding.py
│   │   ├── launches.py
│   │   └── events.py
│   ├── providers/
│   │   ├── crunchbase.py (optional, if API available)
│   │   ├── techcrunch_funding.py
│   │   └── rss_fallback.py
│   ├── models/
│   │   └── schemas.py
│   └── config.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── README.md
```

### API Endpoints

**Base URL:** `http://localhost:3002` (configurable via PORT env var)

#### 1. GET /funding
Retrieves recent funding rounds and investment news.

**Query Parameters:**
- `keyword` (optional): Filter by keyword (e.g., "AI", "fintech")
- `days` (optional): Number of days to look back (default: 7)
- `min_amount` (optional): Minimum funding amount filter

**Response Format:**
```json
{
  "count": 15,
  "funding_rounds": [
    {
      "name": "Company Name",
      "type": "Series A",
      "amount": "$10M",
      "amount_numeric": 10000000,
      "currency": "USD",
      "date": "2024-01-15",
      "description": "Funding round description",
      "investors": ["Investor 1", "Investor 2"],
      "category": "AI/ML",
      "link": "https://...",
      "source": "techcrunch"
    }
  ]
}
```

#### 2. GET /launches
Retrieves newly launched products and startup launches.

**Query Parameters:**
- `keyword` (optional): Filter by keyword
- `days` (optional): Number of days to look back (default: 7)
- `category` (optional): Filter by category

**Response Format:**
```json
{
  "count": 20,
  "launches": [
    {
      "name": "Product/Startup Name",
      "type": "product",  // or "startup"
      "description": "Launch description",
      "date": "2024-01-15",
      "category": "SaaS",
      "link": "https://...",
      "founders": ["Founder 1"],
      "tagline": "Product tagline",
      "source": "producthunt"
    }
  ]
}
```

#### 3. GET /events
Retrieves startup events, conferences, and industry happenings.

**Query Parameters:**
- `keyword` (optional): Filter by keyword
- `days` (optional): Number of days to look forward (default: 30)

**Response Format:**
```json
{
  "count": 10,
  "events": [
    {
      "name": "Event Name",
      "type": "conference",  // or "webinar", "demo-day"
      "description": "Event description",
      "date": "2024-02-15",
      "location": "San Francisco, CA",
      "link": "https://...",
      "source": "eventbrite"
    }
  ]
}
```

#### 4. GET /all
Aggregates all signals (funding, launches, events).

**Query Parameters:**
- `keyword` (optional): Filter all signals by keyword
- `days` (optional): Lookback period (default: 7)

**Response Format:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "funding": {
    "count": 15,
    "rounds": [...]
  },
  "launches": {
    "count": 20,
    "items": [...]
  },
  "events": {
    "count": 10,
    "items": [...]
  },
  "total": 45
}
```

#### 5. GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "startup-api-wrapper",
  "version": "1.0.0"
}
```

### Data Sources & Implementation

#### Funding Data Sources

1. **TechCrunch Funding RSS Feed**
   - URL: `https://techcrunch.com/tag/funding/feed/`
   - Parse RSS for funding articles
   - Extract company name, amount, investors using NLP/pattern matching
   - Fallback if RSS unavailable

2. **Crunchbase API** (if API key available)
   - Use Crunchbase API v4 if credentials provided
   - Fetch recent funding rounds
   - Extract structured data

3. **HackerNews "Who's Hiring" Posts**
   - Monitor posts mentioning funding
   - Parse funding announcements

4. **RSS Fallback**
   - Aggregate multiple startup news RSS feeds
   - Keyword-based filtering for funding content
   - Basic NLP to extract funding amounts

#### Launch Data Sources

1. **ProductHunt API/Scraping**
   - Daily product launches
   - Extract product details, makers, votes

2. **TechCrunch Launch Posts**
   - RSS feed for launch announcements
   - Parse product launch articles

3. **Indie Hackers (optional)**
   - Community launches
   - Product showcases

#### Event Data Sources

1. **Eventbrite API** (if available)
   - Startup events and conferences
   - Filter by tech/startup categories

2. **Meetup API** (if available)
   - Tech startup meetups
   - Demo days and pitch events

3. **RSS Aggregation**
   - Aggregate event listings from multiple sources

### Data Models

**Pydantic Schemas** (`models/schemas.py`):

```python
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class FundingRound(BaseModel):
    name: str
    type: str  # Seed, Series A, Series B, etc.
    amount: str  # Human-readable: "$10M"
    amount_numeric: Optional[float]
    currency: str = "USD"
    date: str  # ISO format: "2024-01-15"
    description: str
    investors: List[str] = []
    category: Optional[str]
    link: str
    source: str

class Launch(BaseModel):
    name: str
    type: str  # "product" or "startup"
    description: str
    date: str
    category: Optional[str]
    link: str
    founders: List[str] = []
    tagline: Optional[str]
    source: str

class Event(BaseModel):
    name: str
    type: str  # "conference", "webinar", "demo-day"
    description: str
    date: str
    location: Optional[str]
    link: str
    source: str
```

### Caching Strategy

- Cache funding data for 1 hour (changes slowly)
- Cache launches for 30 minutes (more frequent)
- Cache events for 6 hours (very stable)
- Use Redis or in-memory cache (dict-based)
- Cache key: `${endpoint}-${keyword}-${days}`

### Error Handling

- Graceful degradation if primary source fails
- Fallback to RSS parsing
- Return partial results with error messages
- Retry logic with exponential backoff
- Timeout handling (30 seconds per source)

### Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.1
pydantic==2.5.0
python-dotenv==1.0.0
feedparser==6.0.10
beautifulsoup4==4.12.2
lxml==4.9.3
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3002

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3002"]
```

### Configuration

**Environment Variables:**
```env
PORT=3002
CRUNCHBASE_API_KEY=optional-api-key
EVENTBRITE_API_KEY=optional-api-key
CACHE_TTL_FUNDING=3600  # 1 hour
CACHE_TTL_LAUNCHES=1800  # 30 minutes
CACHE_TTL_EVENTS=21600  # 6 hours
TIMEOUT=30000
```

### MCP Hub Registration

**Docker Image:**
```bash
docker build -t startup-api:latest .
docker tag startup-api:latest yourusername/startup-api:latest
docker push yourusername/startup-api:latest
```

**MCP Hub Manifest** (`mcp-manifest.json`):
```json
{
  "name": "startup-api",
  "type": "agent",
  "version": "1.0.0",
  "description": "Aggregates startup funding, launches, and events from multiple sources",
  "endpoints": [
    {
      "path": "/funding",
      "method": "GET",
      "description": "Get recent funding rounds",
      "queryParams": ["keyword", "days", "min_amount"]
    },
    {
      "path": "/launches",
      "method": "GET",
      "description": "Get recent product/startup launches",
      "queryParams": ["keyword", "days", "category"]
    },
    {
      "path": "/events",
      "method": "GET",
      "description": "Get upcoming startup events",
      "queryParams": ["keyword", "days"]
    },
    {
      "path": "/all",
      "method": "GET",
      "description": "Get all signals aggregated",
      "queryParams": ["keyword", "days"]
    }
  ],
  "healthCheck": "/health"
}
```

### Testing

**Local Testing:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.main:app --host 0.0.0.0 --port 3002

# Test endpoints
curl http://localhost:3002/health
curl http://localhost:3002/funding?days=7
curl http://localhost:3002/launches?keyword=AI
curl http://localhost:3002/events
curl http://localhost:3002/all?days=7&keyword=fintech
```

**Docker Testing:**
```bash
docker build -t startup-api-wrapper:latest .
docker run -p 3002:3002 startup-api-wrapper:latest
```

### Rate Limiting & Best Practices

- Respect API rate limits (if using APIs)
- Implement request throttling (max 20 requests/minute)
- Use proper headers and user agents
- Handle 429 responses gracefully
- Implement exponential backoff
- Fallback to free RSS sources

### Deliverables

1. Complete startup API wrapper tool with all endpoints
2. Dockerfile for containerization
3. MCP Hub manifest file
4. Pydantic models for data validation
5. Multiple data source integrations with fallbacks
6. Caching implementation
7. Error handling and retry logic
8. README with setup and usage instructions

### Integration Notes

This agent will be called from the Orchestrator Agent (step 5) using HTTP requests. The orchestrator will:
- Call `/funding` endpoint to get funding rounds
- Call `/launches` endpoint to get product launches
- Parse JSON responses
- Store data in SQLite database

### Next Steps

After completing this agent, proceed to:
- **04-docker-mcp-github-monitor-agent.md** - Build the GitHub monitor agent
- **05-orchestrator-agent.md** - Integrate all three data collector agents into the orchestrator
- **06-database-setup.md** - Set up database schema for storing collected data
