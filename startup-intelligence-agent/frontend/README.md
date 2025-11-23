# Frontend UI - Startup Intelligence Dashboard

## Overview

A modern, responsive dashboard for displaying startup intelligence briefings. Built with HTML5, Tailwind CSS, and vanilla JavaScript.

## Features

- ✅ Real-time briefing display
- ✅ Responsive design (mobile-friendly)
- ✅ Auto-refresh every 30 minutes
- ✅ Loading and error states
- ✅ All intelligence sections:
  - Today's Summary
  - Statistics
  - Top Trends
  - Funding Rounds
  - Product Launches
  - Competitor Moves
  - Opportunities for Founders
  - Opportunities for Investors
  - Intelligence Threads

## Quick Start

### Option 1: Serve with Python

```bash
cd frontend
python3 -m http.server 3000
```

Then open: http://localhost:3000

### Option 2: Serve with Node.js

```bash
cd frontend
npx http-server -p 3000
```

### Option 3: Serve with FastAPI (Recommended)

Add static file serving to your FastAPI server:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

Then access at: http://localhost:8080

## Configuration

### API URL

The frontend automatically detects the API URL:
- If served from `localhost:3000`, it connects to `http://localhost:8080`
- If served from the same origin as the API, it uses the same origin

To manually configure, edit `index.html`:

```javascript
const API_BASE_URL = 'http://your-api-url:8080';
```

## Testing

1. **Start the API server:**
   ```bash
   cd backend/src
   python3 main.py
   ```

2. **Serve the frontend:**
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

3. **Open in browser:**
   http://localhost:3000

4. **Test with mock data:**
   - If no briefing exists, you'll see an error message
   - Trigger a workflow first: `curl -X POST http://localhost:8080/orchestrator/run`
   - Then refresh the frontend

## Troubleshooting

### Issue: "Failed to load briefing"

**Causes:**
- API server not running
- CORS issues (if served from different origin)
- No briefing exists yet

**Solutions:**
1. Ensure API server is running on port 8080
2. Check browser console for errors
3. Generate a briefing first: `POST /orchestrator/run`

### Issue: CORS Errors

If serving from a different origin, add CORS headers in FastAPI (already configured in `api/server.py`).

### Issue: Blank Page

- Check browser console for JavaScript errors
- Verify API_BASE_URL is correct
- Ensure API server is accessible

## File Structure

```
frontend/
├── index.html    # Main dashboard (single file)
└── README.md     # This file
```

## Next Steps

After frontend is working:
1. Test with real data from orchestrator workflow
2. Customize styling if needed
3. Add additional features (search, filters, etc.)
4. Deploy to production

---

**Ready to use!** Start the API server and serve the frontend to see your intelligence dashboard! 🚀

