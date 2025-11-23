# News Scraper Agent

Docker MCP Hub agent that scrapes startup news from TechCrunch, HackerNews, and ProductHunt.

## Features

- ✅ Scrapes TechCrunch via RSS feed
- ✅ Scrapes HackerNews via official API
- ✅ Scrapes ProductHunt using Playwright
- ✅ Filters for startup-related content
- ✅ In-memory caching (15 minutes TTL)
- ✅ Error handling and graceful degradation
- ✅ Health check endpoint

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run locally
npm start

# Or with nodemon (auto-reload)
npm run dev
```

### Docker

```bash
# Build image
docker build -t news-scraper:latest .

# Run container
docker run -p 3001:3001 news-scraper:latest
```

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "news-scraper",
  "version": "1.0.0"
}
```

### GET /techcrunch
Get latest TechCrunch articles.

**Response:**
```json
{
  "source": "techcrunch",
  "count": 20,
  "articles": [...]
}
```

### GET /hackernews
Get latest HackerNews posts.

**Response:**
```json
{
  "source": "hackernews",
  "count": 30,
  "articles": [...]
}
```

### GET /producthunt
Get latest ProductHunt launches.

**Response:**
```json
{
  "source": "producthunt",
  "count": 20,
  "articles": [...]
}
```

### GET /all
Aggregate all sources.

**Query Parameters:**
- `limit` (optional): Number of articles per source (default: 20)
- `hours` (optional): Only return articles from last N hours (default: 24)

**Example:**
```bash
curl http://localhost:3001/all?limit=10&hours=12
```

## Configuration

Environment variables:

- `PORT` - Server port (default: 3001)
- `NODE_ENV` - Environment (default: production)
- `CACHE_TTL` - Cache TTL in seconds (default: 900)
- `TIMEOUT` - Request timeout in milliseconds (default: 30000)

## Testing

```bash
# Health check
curl http://localhost:3001/health

# Test all endpoints
curl http://localhost:3001/techcrunch
curl http://localhost:3001/hackernews
curl http://localhost:3001/producthunt
curl http://localhost:3001/all?limit=10&hours=12
```

## Integration

This agent is called by the Orchestrator Agent via HTTP:

```bash
# Orchestrator calls this endpoint
GET http://news-scraper:3001/all?limit=20&hours=24
```

## MCP Hub Registration

To register with Docker MCP Hub:

1. Build and push Docker image:
```bash
docker build -t news-scraper:latest .
docker tag news-scraper:latest yourusername/news-scraper:latest
docker push yourusername/news-scraper:latest
```

2. Use the `mcp-manifest.json` for registration.

## Notes

- Respects rate limiting and robots.txt
- Uses caching to reduce API calls
- Gracefully handles errors (returns partial results if one source fails)
- Filters content for startup/funding relevance

---

**Ready for use!** 🚀

