# UI Testing Guide - Quick Start

## 🌐 Access the Dashboard

**URL:** http://localhost:8080/

The server should already be running. If not, start it:
```bash
cd startup-intelligence-agent/backend/src
source ../venv/bin/activate
python main.py
```

## ✅ Quick Test Checklist

### 1. Dashboard Loads
- [ ] Open http://localhost:8080/ in your browser
- [ ] Dashboard header shows "Startup Intelligence Dashboard"
- [ ] Briefing date is displayed
- [ ] Refresh button is visible

### 2. Data Display
- [ ] Statistics cards show numbers (may be 0 if no data)
- [ ] Summary section displays text
- [ ] Trends section is visible (may be empty)
- [ ] Funding rounds section is visible
- [ ] Opportunities sections are visible

### 3. Interactive Features
- [ ] Click "Refresh" button - should reload data
- [ ] Check that loading spinner appears during refresh
- [ ] Verify data updates after refresh

### 4. Trigger Workflow (if no data)
If the dashboard shows empty data:

```bash
# Trigger workflow to collect and analyze data
curl -X POST "http://localhost:8080/orchestrator/run?days_back=7"

# Wait 30-60 seconds for workflow to complete
# Then refresh the browser
```

### 5. Check API Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Get briefing data
curl http://localhost:8080/briefing | jq '.'

# Check data stats
curl http://localhost:8080/data/stats | jq '.'
```

## 🎯 Expected UI Features

1. **Header Section**
   - Title: "Startup Intelligence Dashboard"
   - Briefing date
   - Refresh button

2. **Statistics Cards**
   - News Articles count
   - Funding Rounds count
   - Launches count
   - Trends Identified count

3. **Content Sections**
   - Today's Summary
   - Top Trends (with confidence badges)
   - Recent Funding Rounds (with amounts)
   - Recent Product Launches
   - Opportunities for Founders
   - Opportunities for Investors
   - Intelligence Threads (expandable)

## 🐛 Troubleshooting

### Dashboard shows "Failed to load briefing"
- Check server is running: `curl http://localhost:8080/health`
- Check if briefing exists: `curl http://localhost:8080/briefing`
- Trigger workflow if no briefing exists

### No data displayed
- Trigger workflow: `curl -X POST http://localhost:8080/orchestrator/run?days_back=7`
- Wait for completion (check status: `curl http://localhost:8080/orchestrator/status`)
- Refresh browser

### Server not accessible
- Verify server is running on port 8080
- Check firewall settings
- Try `http://127.0.0.1:8080/` instead

## 📸 Screenshots for Demo

Take screenshots of:
1. Dashboard overview
2. Statistics cards
3. Trends section
4. Funding rounds
5. Opportunities sections

## 🔗 GitHub Repository

**Repository:** https://github.com/oabolade/figma_mcp_server_actor

**Direct Link for Hackathon:**
https://github.com/oabolade/figma_mcp_server_actor

