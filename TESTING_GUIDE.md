# Testing Guide - Startup Intelligence System

## Quick Start

### Start All Services

```bash
# Option 1: Use the helper script (recommended)
./start_services.sh

# Option 2: Manual start
cd data-collector-agents
docker-compose up -d

cd ../startup-intelligence-agent/backend/src
python3 main.py > /tmp/server.log 2>&1 &
```

### Stop All Services

```bash
./stop_services.sh
```

## Service URLs

### Data Collector Agents
- **News Scraper** (Port 3001): http://localhost:3001
- **Startup API** (Port 3002): http://localhost:3002
- **GitHub Monitor** (Port 3003): http://localhost:3003

### Main Server
- **Frontend UI**: http://localhost:8080/
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **API Info**: http://localhost:8080/info

## Testing Health Endpoints

### Test All Data Collector Agents

```bash
./test_data_collectors.sh
```

### Individual Health Checks

```bash
# News Scraper
curl http://localhost:3001/health | python3 -m json.tool

# Startup API
curl http://localhost:3002/health | python3 -m json.tool

# GitHub Monitor
curl http://localhost:3003/health | python3 -m json.tool

# Main Server
curl http://localhost:8080/health | python3 -m json.tool
```

## Testing Agent Endpoints

### News Scraper

```bash
# Get all news sources
curl "http://localhost:3001/all?limit=10&hours=24" | python3 -m json.tool

# Get TechCrunch articles
curl http://localhost:3001/techcrunch | python3 -m json.tool

# Get HackerNews posts
curl http://localhost:3001/hackernews | python3 -m json.tool

# Get ProductHunt launches
curl http://localhost:3001/producthunt | python3 -m json.tool
```

### Startup API

```bash
# Get all signals
curl "http://localhost:3002/all?days=7" | python3 -m json.tool

# Get funding rounds
curl "http://localhost:3002/funding?days=7" | python3 -m json.tool

# Get launches
curl "http://localhost:3002/launches?days=7" | python3 -m json.tool

# Get events
curl http://localhost:3002/events | python3 -m json.tool
```

### GitHub Monitor

```bash
# Get trending repositories
curl "http://localhost:3003/trending?limit=10" | python3 -m json.tool

# Get technical signals
curl "http://localhost:3003/signals?days=7" | python3 -m json.tool

# Search repositories
curl "http://localhost:3003/search?keywords=startup,saas" | python3 -m json.tool
```

## Testing Main Server

### Test Orchestrator Integration

```bash
# Trigger full workflow (collect → enrich → analyze → summarize)
curl -X POST "http://localhost:8080/orchestrator/run?days_back=7"

# Trigger data collection only
curl -X POST http://localhost:8080/orchestrator/collect

# Check workflow status
curl http://localhost:8080/orchestrator/status | python3 -m json.tool

# Get data statistics
curl http://localhost:8080/data/stats | python3 -m json.tool
```

### Test API Endpoints

```bash
# Get latest briefing
curl http://localhost:8080/briefing | python3 -m json.tool

# Get latest analysis
curl http://localhost:8080/analysis/latest | python3 -m json.tool

# Get trends
curl http://localhost:8080/analysis/trends | python3 -m json.tool

# Get opportunities
curl "http://localhost:8080/analysis/opportunities?type=all" | python3 -m json.tool
```

## View Logs

### Data Collector Agents

```bash
cd data-collector-agents
docker-compose logs -f

# Individual agent logs
docker-compose logs -f news-scraper
docker-compose logs -f startup-api
docker-compose logs -f github-monitor
```

### Main Server

```bash
# View server logs
tail -f /tmp/server.log

# Follow logs in real-time
tail -f /tmp/server.log | grep -i error
```

## Check Service Status

### Docker Containers

```bash
cd data-collector-agents
docker-compose ps

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Port Status

```bash
# Check which ports are in use
lsof -i :3001  # News Scraper
lsof -i :3002  # Startup API
lsof -i :3003  # GitHub Monitor
lsof -i :8080  # Main Server
```

## Troubleshooting

### Agent Not Responding

```bash
# Check container logs
docker-compose logs <service-name>

# Restart specific agent
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up -d --build <service-name>
```

### Main Server Not Starting

```bash
# Check if port is in use
lsof -i :8080

# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Check server logs
tail -f /tmp/server.log
```

### Connection Errors

```bash
# Test if agents are accessible from host
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health

# Check Docker network
docker network ls
docker network inspect data-collector-agents
```

## Example Integration Test

```bash
# 1. Check all services are running
./test_data_collectors.sh

# 2. Test main server
curl http://localhost:8080/health

# 3. Trigger data collection
curl -X POST http://localhost:8080/orchestrator/collect

# 4. Wait a moment, then check status
sleep 5
curl http://localhost:8080/orchestrator/status | python3 -m json.tool

# 5. Check data stats
curl http://localhost:8080/data/stats | python3 -m json.tool
```

## Next Steps

1. **Start all services**: `./start_services.sh`
2. **Test agent health**: `./test_data_collectors.sh`
3. **Access frontend**: http://localhost:8080/
4. **Trigger workflow**: `curl -X POST http://localhost:8080/orchestrator/run`
5. **View briefing**: http://localhost:8080/briefing

---

**Happy Testing!** 🚀

