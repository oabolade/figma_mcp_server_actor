# Prompt 4: Docker MCP Hub Agent - GitHub Monitor

## Objective

Build a Docker-based MCP Hub agent that monitors GitHub repositories for trending projects, technical signals, and developer activity that indicates emerging technologies or startup activity.

## Requirements

### Agent Specifications

**Agent Name:** `github-monitor`

**Technology Stack:**
- Python 3.11+ (for GitHub API and data processing)
- FastAPI for HTTP server
- GitHub API v4 (GraphQL) or v3 (REST)
- httpx for async HTTP requests
- Pydantic for data validation

### Agent Architecture

This is an **autonomous agent** running in a Docker container via Docker MCP Hub, not just a passive tool. It actively monitors and tracks GitHub activity.

### Directory Structure

```
tools/github-monitor/
├── src/
│   ├── main.py
│   ├── agent/
│   │   ├── monitor.py
│   │   ├── trending.py
│   │   └── signals.py
│   ├── github/
│   │   ├── api_client.py
│   │   └── queries.py
│   ├── models/
│   │   └── schemas.py
│   └── config.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
└── README.md
```

### API Endpoints

**Base URL:** `http://localhost:3003` (configurable via PORT env var)

#### 1. GET /trending
Retrieves trending repositories across different timeframes and languages.

**Query Parameters:**
- `language` (optional): Filter by programming language (e.g., "python", "javascript")
- `since` (optional): Timeframe - "daily", "weekly", "monthly" (default: "daily")
- `limit` (optional): Number of repos to return (default: 25)

**Response Format:**
```json
{
  "count": 25,
  "since": "daily",
  "repositories": [
    {
      "name": "repo-name",
      "full_name": "owner/repo-name",
      "description": "Repository description",
      "language": "Python",
      "stars": 1250,
      "stars_today": 45,
      "forks": 89,
      "url": "https://github.com/owner/repo-name",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z",
      "topics": ["ai", "machine-learning"],
      "signals": {
        "growth_rate": "high",
        "developer_activity": "active",
        "startup_indicator": true
      }
    }
  ]
}
```

#### 2. GET /signals
Extracts technical signals from GitHub activity that indicate startup/tech trends.

**Query Parameters:**
- `keywords` (optional): Comma-separated keywords to search for
- `days` (optional): Lookback period in days (default: 7)
- `min_stars` (optional): Minimum star count (default: 10)

**Response Format:**
```json
{
  "count": 15,
  "signals": [
    {
      "type": "emerging_technology",
      "repository": {
        "name": "new-ai-framework",
        "full_name": "owner/new-ai-framework",
        "url": "https://github.com/owner/new-ai-framework",
        "description": "Description",
        "language": "Python",
        "stars": 500,
        "growth_rate": "exponential"
      },
      "indicator": "Rapid star growth in AI/ML category",
      "confidence": "high",
      "date": "2024-01-15"
    },
    {
      "type": "startup_activity",
      "repository": {
        "name": "stealth-startup",
        "full_name": "owner/stealth-startup",
        "url": "https://github.com/owner/stealth-startup",
        "description": "Description",
        "language": "TypeScript",
        "stars": 150,
        "recent_commits": 45
      },
      "indicator": "High commit activity, stealth mode patterns",
      "confidence": "medium",
      "date": "2024-01-15"
    }
  ]
}
```

#### 3. GET /repositories/{owner}/{repo}
Get detailed information about a specific repository.

**Path Parameters:**
- `owner`: Repository owner username
- `repo`: Repository name

**Response Format:**
```json
{
  "name": "repo-name",
  "full_name": "owner/repo-name",
  "description": "Detailed description",
  "language": "Python",
  "stars": 1250,
  "forks": 89,
  "watchers": 234,
  "open_issues": 12,
  "url": "https://github.com/owner/repo-name",
  "homepage": "https://example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "pushed_at": "2024-01-15T09:00:00Z",
  "topics": ["ai", "machine-learning", "startup"],
  "contributors_count": 15,
  "recent_activity": {
    "commits_last_7d": 45,
    "issues_opened": 3,
    "pull_requests": 5
  },
  "signals": {
    "startup_indicator": true,
    "active_development": true,
    "community_growth": "high"
  }
}
```

#### 4. GET /search
Search repositories by keywords, topics, or criteria.

**Query Parameters:**
- `q` (required): Search query
- `language` (optional): Filter by language
- `sort` (optional): "stars", "updated", "created" (default: "stars")
- `order` (optional): "asc", "desc" (default: "desc")
- `limit` (optional): Number of results (default: 20)

**Response Format:**
```json
{
  "query": "AI startup",
  "count": 20,
  "repositories": [...]
}
```

#### 5. GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "github-monitor",
  "version": "1.0.0",
  "github_api_status": "connected"
}
```

### Implementation Details

#### GitHub API Integration

**Authentication:**
- Use GitHub Personal Access Token (PAT) for higher rate limits
- Store token in environment variable: `GITHUB_TOKEN`
- Fallback to unauthenticated requests with lower rate limits

**API Client** (`github/api_client.py`):
- Use GitHub GraphQL API v4 for efficient queries
- Implement rate limiting and retry logic
- Cache responses appropriately

**Key Queries:**
1. **Trending Repositories**: Query by stars, forks, recent activity
2. **Repository Details**: Get comprehensive repo information
3. **Search**: Search repositories by keywords, topics, languages
4. **Activity Signals**: Monitor commit activity, issues, PRs

#### Signal Detection Logic

**Startup Indicators:**
- High commit frequency in new repos
- Stealth mode patterns (limited public info, active development)
- Specific topic tags (startup, saas, producthunt)
- Homepage URLs indicating products/services
- Organization accounts (vs personal)

**Technical Signals:**
- Rapid star growth
- Multiple contributors
- Active issue discussions
- Recent major releases
- Language trends

**Emerging Technology Indicators:**
- New frameworks or libraries
- High adoption rate
- Community engagement
- Documentation quality

#### Caching Strategy

- Cache trending repos for 1 hour (updates daily)
- Cache repository details for 30 minutes
- Cache search results for 15 minutes
- Use in-memory cache (dict or Redis if available)
- Cache key: `${endpoint}-${params_hash}`

### Data Models

**Pydantic Schemas** (`models/schemas.py`):

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Repository(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    watchers: Optional[int]
    url: str
    homepage: Optional[str]
    created_at: str
    updated_at: str
    pushed_at: Optional[str]
    topics: List[str] = []
    open_issues: Optional[int] = 0
    contributors_count: Optional[int] = 0

class RepositorySignal(BaseModel):
    type: str  # "emerging_technology", "startup_activity", "tech_trend"
    repository: Repository
    indicator: str
    confidence: str  # "high", "medium", "low"
    date: str

class TrendingRepositories(BaseModel):
    count: int
    since: str
    repositories: List[Repository]
```

### Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.1
pydantic==2.5.0
python-dotenv==1.0.0
PyGithub==2.1.1  # Optional: GitHub SDK
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

EXPOSE 3003

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3003"]
```

### Configuration

**Environment Variables:**
```env
PORT=3003
GITHUB_TOKEN=your-github-pat-optional
CACHE_TTL_TRENDING=3600  # 1 hour
CACHE_TTL_REPOS=1800  # 30 minutes
CACHE_TTL_SEARCH=900  # 15 minutes
TIMEOUT=30000
RATE_LIMIT_REQUESTS=5000  # GitHub API rate limit
```

### MCP Hub Registration

**Docker Image:**
```bash
docker build -t github-monitor:latest .
docker tag github-monitor:latest yourusername/github-monitor:latest
docker push yourusername/github-monitor:latest
```

**MCP Hub Manifest** (`mcp-manifest.json`):
```json
{
  "name": "github-monitor",
  "version": "1.0.0",
  "description": "Monitors GitHub repositories for trending projects and technical signals",
  "type": "agent",
  "endpoints": [
    {
      "path": "/trending",
      "method": "GET",
      "description": "Get trending repositories",
      "queryParams": ["language", "since", "limit"]
    },
    {
      "path": "/signals",
      "method": "GET",
      "description": "Extract technical signals from GitHub activity",
      "queryParams": ["keywords", "days", "min_stars"]
    },
    {
      "path": "/repositories/{owner}/{repo}",
      "method": "GET",
      "description": "Get detailed repository information",
      "pathParams": ["owner", "repo"]
    },
    {
      "path": "/search",
      "method": "GET",
      "description": "Search repositories",
      "queryParams": ["q", "language", "sort", "order", "limit"]
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

# Set GitHub token (optional)
export GITHUB_TOKEN=your-token

# Run server
uvicorn src.main:app --host 0.0.0.0 --port 3003

# Test endpoints
curl http://localhost:3003/health
curl http://localhost:3003/trending?since=daily&limit=10
curl http://localhost:3003/signals?days=7&keywords=AI,startup
curl http://localhost:3003/repositories/microsoft/vscode
curl http://localhost:3003/search?q=AI%20startup&language=python
```

### Rate Limiting & Best Practices

- Respect GitHub API rate limits (5,000 requests/hour with auth, 60/hour without)
- Implement exponential backoff for 429 responses
- Use conditional requests (ETags) to reduce API calls
- Cache aggressively for trending data
- Use GraphQL API for efficient multi-field queries

### Deliverables

1. Complete GitHub monitor agent with all endpoints
2. GitHub API client with rate limiting
3. Signal detection logic for startup/tech indicators
4. Dockerfile for containerization
5. MCP Hub manifest file
6. Pydantic models for data validation
7. Caching implementation
8. Error handling and retry logic
9. README with setup and usage instructions

### Integration Notes

This agent will be called from the Orchestrator Agent (step 5) using HTTP requests. The orchestrator will:
- Call `/trending` endpoint to get trending repositories
- Call `/signals` endpoint to get technical signals
- Store repository data and signals in SQLite database
- Use signals for analysis and opportunity identification

### Next Steps

After completing this agent, proceed to:
- **05-orchestrator-agent.md** - Integrate all three data collector agents
- **06-database-setup.md** - Set up database schema including GitHub signals table
