# Prompt 2: Docker MCP Hub Agent - News Scraper

## Objective

Build a Docker-based MCP Hub **agent** that runs inside a Docker container and actively scrapes startup news from TechCrunch, HackerNews, and ProductHunt. This is an autonomous agent (not just a passive tool) that exposes HTTP endpoints for E2B sandboxes to consume.

## Requirements

### Agent Specifications

**Agent Name:** `news-scraper`

**Agent Type:** Autonomous data collector agent running in Docker container via Docker MCP Hub

**Technology Stack:**
- Node.js 20+ (for Playwright compatibility)
- Playwright for web scraping
- Express.js for HTTP server
- RSS parser for feed aggregation

### Directory Structure

```
tools/news-scraper/
├── src/
│   ├── index.js
│   ├── scrapers/
│   │   ├── techcrunch.js
│   │   ├── hackernews.js
│   │   └── producthunt.js
│   ├── utils/
│   │   ├── parser.js
│   │   └── cache.js
│   └── config.js
├── Dockerfile
├── package.json
├── .dockerignore
└── README.md
```

### API Endpoints

**Base URL:** `http://localhost:3001` (configurable via PORT env var)

#### 1. GET /techcrunch
Scrapes or parses TechCrunch RSS feed for latest startup news.

**Response Format:**
```json
{
  "source": "techcrunch",
  "count": 20,
  "articles": [
    {
      "title": "Article title",
      "url": "https://techcrunch.com/...",
      "timestamp": "2024-01-15T10:30:00Z",
      "summary": "Article summary or excerpt",
      "author": "Author name",
      "categories": ["startup", "funding"]
    }
  ]
}
```

#### 2. GET /hackernews
Scrapes HackerNews for startup-related posts and news.

**Response Format:**
```json
{
  "source": "hackernews",
  "count": 30,
  "articles": [
    {
      "title": "Post title",
      "url": "https://news.ycombinator.com/item?id=...",
      "timestamp": "2024-01-15T10:30:00Z",
      "summary": "Post excerpt or first paragraph",
      "author": "username",
      "score": 250,
      "comments": 45
    }
  ]
}
```

#### 3. GET /producthunt
Scrapes ProductHunt for newly launched products and startups.

**Response Format:**
```json
{
  "source": "producthunt",
  "count": 20,
  "articles": [
    {
      "title": "Product name",
      "url": "https://www.producthunt.com/posts/...",
      "timestamp": "2024-01-15T10:30:00Z",
      "summary": "Product description",
      "maker": "Maker name",
      "votes": 450,
      "tagline": "Product tagline"
    }
  ]
}
```

#### 4. GET /all
Aggregates all sources into a single response.

**Query Parameters:**
- `limit` (optional): Number of articles per source (default: 20)
- `hours` (optional): Only return articles from last N hours (default: 24)

**Response Format:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "sources": {
    "techcrunch": { "count": 20, "articles": [...] },
    "hackernews": { "count": 30, "articles": [...] },
    "producthunt": { "count": 20, "articles": [...] }
  },
  "total": 70
}
```

#### 5. GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "news-scraper",
  "version": "1.0.0"
}
```

### Implementation Details

#### TechCrunch Scraper
- Use RSS feed: `https://techcrunch.com/feed/`
- Parse RSS XML using `rss-parser` package
- Extract: title, link, pubDate, description, author
- Filter for startup/funding related content (keyword matching)

#### HackerNews Scraper
- Use HackerNews API: `https://hacker-news.firebaseio.com/v0/`
- Fetch top stories: `GET /v0/topstories.json`
- For each story: `GET /v0/item/{id}.json`
- Filter for startup-related content
- Include score and comment count

#### ProductHunt Scraper
- Option 1: Use Playwright to scrape ProductHunt daily page
- Option 2: Use unofficial API if available
- Extract: product name, tagline, description, maker, votes
- Focus on products launched today or yesterday

#### Caching Strategy
- Cache responses for 15 minutes
- Use in-memory cache (Map or LRU cache)
- Cache key: `${source}-${date}`

#### Error Handling
- Graceful degradation if one source fails
- Return partial results with error messages
- Retry logic for transient failures
- Timeout handling (30 seconds per source)

### Dependencies

```json
{
  "name": "news-scraper",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2",
    "playwright": "^1.40.0",
    "rss-parser": "^3.13.0",
    "node-fetch": "^3.3.2",
    "cheerio": "^1.0.0-rc.12"
  }
}
```

### Dockerfile

```dockerfile
FROM node:20-slim

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm ci

# Install Playwright browsers
RUN npx playwright install --with-deps chromium

COPY . .

EXPOSE 3001

CMD ["node", "src/index.js"]
```

### Configuration

**Environment Variables:**
```env
PORT=3001
NODE_ENV=production
CACHE_TTL=900  # 15 minutes in seconds
TIMEOUT=30000  # 30 seconds in milliseconds
```

### MCP Hub Registration

To register with Docker MCP Hub:

1. **Docker Image:** Build and push to Docker Hub
   ```bash
   docker build -t news-scraper:latest .
   docker tag news-scraper:latest yourusername/news-scraper:latest
   docker push yourusername/news-scraper:latest
   ```

2. **MCP Hub Manifest:** Create `mcp-manifest.json`
   ```json
   {
     "name": "news-scraper",
     "version": "1.0.0",
     "description": "Scrapes startup news from TechCrunch, HackerNews, and ProductHunt",
     "endpoints": [
       {
         "path": "/techcrunch",
         "method": "GET",
         "description": "Get latest TechCrunch articles"
       },
       {
         "path": "/hackernews",
         "method": "GET",
         "description": "Get latest HackerNews posts"
       },
       {
         "path": "/producthunt",
         "method": "GET",
         "description": "Get latest ProductHunt launches"
       },
       {
         "path": "/all",
         "method": "GET",
         "description": "Get all sources aggregated",
         "queryParams": ["limit", "hours"]
       }
     ],
     "healthCheck": "/health"
   }
   ```

### Testing

**Local Testing:**
```bash
# Install dependencies
npm install

# Run locally
npm start

# Test endpoints
curl http://localhost:3001/health
curl http://localhost:3001/techcrunch
curl http://localhost:3001/hackernews
curl http://localhost:3001/producthunt
curl http://localhost:3001/all?limit=10&hours=12
```

**Docker Testing:**
```bash
# Build image
docker build -t news-scraper:latest .

# Run container
docker run -p 3001:3001 news-scraper:latest

# Test endpoints (same as above)
```

### Rate Limiting & Best Practices

- Respect robots.txt for each site
- Implement request rate limiting (max 10 requests/minute)
- Use user-agent headers
- Handle 429 (Too Many Requests) responses gracefully
- Implement exponential backoff for retries

### Deliverables

1. Complete news scraper tool with all endpoints
2. Dockerfile for containerization
3. MCP Hub manifest file
4. README with setup and usage instructions
5. Error handling and caching implementation
6. Health check endpoint

### Integration Notes

This tool will be called from the Orchestrator Agent (step 4) using HTTP requests. The orchestrator will:
- Call `/all` endpoint to get aggregated news
- Parse the JSON response
- Store articles in SQLite database

### Next Steps

After completing this tool, proceed to:
- **03-docker-mcp-startup-api-wrapper.md** - Build the startup API wrapper tool
- Then integrate both tools in **04-orchestrator-agent.md**
