# GitHub Monitor Agent

Docker MCP Hub agent that monitors GitHub repositories for trending projects, technical signals, and developer activity.

## Features

- ✅ Monitors trending repositories
- ✅ Extracts technical signals from GitHub activity
- ✅ Searches repositories by keywords
- ✅ Analyzes startup indicators
- ✅ In-memory caching (15 minutes TTL)
- ✅ Health check endpoint

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.main:app --host 0.0.0.0 --port 3003
```

### Docker

```bash
# Build image
docker build -t github-monitor:latest .

# Run container
docker run -p 3003:3003 github-monitor:latest
```

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "github-monitor",
  "version": "1.0.0"
}
```

### GET /trending
Get trending repositories.

**Query Parameters:**
- `language` (optional): Filter by programming language
- `since` (optional): Timeframe - "daily", "weekly", "monthly" (default: "daily")
- `limit` (optional): Number of repos to return (default: 25)

**Example:**
```bash
curl http://localhost:3003/trending?language=python&limit=10
```

### GET /signals
Extract technical signals from GitHub activity.

**Query Parameters:**
- `keywords` (optional): Comma-separated keywords
- `days` (optional): Lookback period in days (default: 7)
- `min_stars` (optional): Minimum star count (default: 10)

**Example:**
```bash
curl http://localhost:3003/signals?keywords=startup,saas&days=7
```

### GET /search
Search repositories by keywords.

**Query Parameters:**
- `keywords` (optional): Comma-separated keywords
- `min_stars` (optional): Minimum star count (default: 10)
- `days` (optional): Days to look back (default: 7)

### GET /repositories/{owner}/{repo}
Get specific repository details.

## Configuration

Environment variables:

- `PORT` - Server port (default: 3003)
- `NODE_ENV` - Environment (default: production)
- `CACHE_TTL` - Cache TTL in seconds (default: 900)
- `TIMEOUT` - Request timeout in milliseconds (default: 30000)
- `GITHUB_TOKEN` - Optional GitHub API token (for higher rate limits)

## Testing

```bash
# Health check
curl http://localhost:3003/health

# Test all endpoints
curl http://localhost:3003/trending?language=python
curl http://localhost:3003/signals?keywords=startup
curl http://localhost:3003/search?keywords=api,platform
```

## Integration

This agent is called by the Orchestrator Agent via HTTP:

```bash
# Orchestrator calls these endpoints
GET http://github-monitor:3003/trending?limit=25
GET http://github-monitor:3003/signals?days=7
```

## MCP Hub Registration

To register with Docker MCP Hub:

1. Build and push Docker image:
```bash
docker build -t github-monitor:latest .
docker tag github-monitor:latest yourusername/github-monitor:latest
docker push yourusername/github-monitor:latest
```

2. Use the `mcp-manifest.json` for registration.

## Notes

- Uses GitHub Search API (doesn't require authentication for basic usage)
- GitHub token recommended for higher rate limits (5000 requests/hour vs 60)
- Gracefully handles errors and rate limits
- Analyzes repositories for startup/tech indicators

---

**Ready for use!** 🚀

