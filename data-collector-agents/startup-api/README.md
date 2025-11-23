# Startup API Agent

Docker MCP Hub agent that aggregates startup activity signals including funding rounds, product launches, and industry events.

## Features

- ✅ Aggregates funding rounds from TechCrunch RSS
- ✅ Scrapes product launches from multiple sources
- ✅ Retrieves industry events (placeholder)
- ✅ In-memory caching (15 minutes TTL)
- ✅ Error handling and graceful degradation
- ✅ Health check endpoint

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.main:app --host 0.0.0.0 --port 3002
```

### Docker

```bash
# Build image
docker build -t startup-api:latest .

# Run container
docker run -p 3002:3002 startup-api:latest
```

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "startup-api",
  "version": "1.0.0"
}
```

### GET /funding
Get recent funding rounds.

**Query Parameters:**
- `keyword` (optional): Filter by keyword
- `days` (optional): Days to look back (default: 7)
- `min_amount` (optional): Minimum funding amount

**Example:**
```bash
curl http://localhost:3002/funding?keyword=AI&days=7
```

### GET /launches
Get recent product launches.

**Query Parameters:**
- `keyword` (optional): Filter by keyword
- `days` (optional): Days to look back (default: 7)
- `category` (optional): Filter by category

**Example:**
```bash
curl http://localhost:3002/launches?keyword=fintech
```

### GET /events
Get upcoming industry events.

**Query Parameters:**
- `keyword` (optional): Filter by keyword
- `days` (optional): Days to look ahead (default: 30)

### GET /all
Get all signals aggregated.

**Query Parameters:**
- `days` (optional): Days to look back (default: 7)

**Example:**
```bash
curl http://localhost:3002/all?days=7
```

## Configuration

Environment variables:

- `PORT` - Server port (default: 3002)
- `NODE_ENV` - Environment (default: production)
- `CACHE_TTL` - Cache TTL in seconds (default: 900)
- `TIMEOUT` - Request timeout in milliseconds (default: 30000)
- `CRUNCHBASE_API_KEY` - Optional Crunchbase API key
- `ANGEL_LIST_API_KEY` - Optional AngelList API key

## Testing

```bash
# Health check
curl http://localhost:3002/health

# Test all endpoints
curl http://localhost:3002/funding?days=7
curl http://localhost:3002/launches?keyword=AI
curl http://localhost:3002/events
curl http://localhost:3002/all?days=7
```

## Integration

This agent is called by the Orchestrator Agent via HTTP:

```bash
# Orchestrator calls this endpoint
GET http://startup-api:3002/all?days=7
```

## MCP Hub Registration

To register with Docker MCP Hub:

1. Build and push Docker image:
```bash
docker build -t startup-api:latest .
docker tag startup-api:latest yourusername/startup-api:latest
docker push yourusername/startup-api:latest
```

2. Use the `mcp-manifest.json` for registration.

## Notes

- Uses RSS feeds as primary data source
- Can be extended with Crunchbase, AngelList, etc. APIs
- Gracefully handles errors (returns partial results)
- Filters content for relevance

---

**Ready for use!** 🚀

