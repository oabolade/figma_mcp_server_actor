# Data Collector Agents

Docker MCP Hub agents that collect startup intelligence data from multiple sources.

## Overview

This directory contains three autonomous data collector agents that run in Docker containers:

1. **news-scraper** (Node.js/Express) - Port 3001
   - Scrapes startup news from TechCrunch, HackerNews, and ProductHunt
   - RSS feed parsing and Playwright-based scraping
   
2. **startup-api** (Python/FastAPI) - Port 3002
   - Aggregates funding rounds, product launches, and industry events
   - RSS feed parsing with keyword filtering
   
3. **github-monitor** (Python/FastAPI) - Port 3003
   - Monitors trending repositories and technical signals
   - GitHub API integration with signal detection

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all agents
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all agents
docker-compose down
```

### Individual Agent Setup

See individual README files in each agent directory:
- `news-scraper/README.md`
- `startup-api/README.md`
- `github-monitor/README.md`

## Testing

Once all agents are running, test their endpoints:

### News Scraper (Port 3001)
```bash
curl http://localhost:3001/health
curl http://localhost:3001/all?limit=10&hours=12
```

### Startup API (Port 3002)
```bash
curl http://localhost:3002/health
curl http://localhost:3002/all?days=7
```

### GitHub Monitor (Port 3003)
```bash
curl http://localhost:3003/health
curl http://localhost:3003/trending?limit=10
```

## Integration with Orchestrator

The orchestrator agent calls these agents via HTTP:

```bash
# News scraper
GET http://news-scraper:3001/all?limit=20&hours=24

# Startup API
GET http://startup-api:3002/all?days=7

# GitHub Monitor
GET http://github-monitor:3003/trending?limit=25
GET http://github-monitor:3003/signals?days=7
```

## Environment Variables

Create a `.env` file in this directory (optional):

```env
# Optional API keys
CRUNCHBASE_API_KEY=your-api-key
ANGEL_LIST_API_KEY=your-api-key
GITHUB_TOKEN=your-github-token
```

## Ports

- **3001**: news-scraper
- **3002**: startup-api
- **3003**: github-monitor

## MCP Hub Registration

Each agent includes an `mcp-manifest.json` file for Docker MCP Hub registration:

1. Build Docker images:
```bash
docker build -t news-scraper:latest ./news-scraper
docker build -t startup-api:latest ./startup-api
docker build -t github-monitor:latest ./github-monitor
```

2. Push to Docker Hub:
```bash
docker tag news-scraper:latest yourusername/news-scraper:latest
docker push yourusername/news-scraper:latest
# Repeat for other agents
```

3. Use the `mcp-manifest.json` files for registration.

## Health Checks

All agents include health check endpoints:
- `GET /health` - Returns service status

Docker Compose automatically monitors health checks and restarts unhealthy containers.

## Notes

- All agents use in-memory caching (15 minutes TTL by default)
- Graceful error handling (returns partial results if one source fails)
- CORS enabled for cross-origin requests
- Rate limiting considerations built-in

---

**Ready for integration!** 🚀

