# Server Setup and Troubleshooting

## ✅ Fixes Applied

### Issue Fixed: Address/Port Error

**Problem:** Server was trying to bind to `0.0.0.0:8080` which was causing issues:
1. Port 8080 was already in use by another process
2. `0.0.0.0` can cause compatibility issues on macOS

**Solution Applied:**
1. ✅ Changed default HOST from `0.0.0.0` to `127.0.0.1` for better macOS compatibility
2. ✅ Added port availability checking before server startup
3. ✅ Added automatic HOST conversion on macOS (`0.0.0.0` → `127.0.0.1`)
4. ✅ Added helpful error messages with fix instructions

## 🚀 Starting the Server

### Quick Start
```bash
cd startup-intelligence-agent/backend/src
source ../venv/bin/activate
python3 main.py
```

The server will now:
- ✅ Check if port is available before starting
- ✅ Use `127.0.0.1` on macOS for compatibility
- ✅ Provide clear error messages if port is in use

### Expected Output
```
Starting server on http://127.0.0.1:8080
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:
```env
# Server Configuration
HOST=127.0.0.1  # Use 127.0.0.1 for local dev, 0.0.0.0 for Docker/production
PORT=8080       # Change if port is in use
```

### Port Options

- **127.0.0.1** (recommended for local dev): Only accessible from your machine
- **0.0.0.0**: Accessible from any network interface (use for Docker/production)
- **localhost**: Same as 127.0.0.1

## ⚠️ Common Issues

### Issue: Port Already in Use

**Error:**
```
ERROR: Port 8080 is already in use!
```

**Solutions:**

**Option 1: Stop the existing process**
```bash
# Find what's using the port
lsof -i :8080

# Kill the process (replace PID with actual process ID)
kill <PID>

# Or kill all Python processes using the port
kill $(lsof -t -i:8080)
```

**Option 2: Use a different port**
```bash
# Edit .env file
nano .env

# Change PORT to something else
PORT=8081

# Restart server
python3 main.py
```

**Option 3: Change port temporarily**
```bash
# Run with different port via environment variable
PORT=8081 python3 main.py
```

### Issue: Address Already in Use (macOS)

**Problem:** On macOS, `0.0.0.0` can sometimes cause binding issues.

**Solution:** The code now automatically uses `127.0.0.1` on macOS. If you see this error:
1. Check that HOST in `.env` is `127.0.0.1` (or leave default)
2. The server will auto-convert `0.0.0.0` to `127.0.0.1` on macOS

### Issue: Cannot Access Server from Other Machines

**Problem:** Server is on `127.0.0.1` which only allows local access.

**Solution:** For production or Docker, use `0.0.0.0`:
```env
HOST=0.0.0.0
```

## 🧪 Testing the Server

### Health Check
```bash
curl http://127.0.0.1:8080/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "startup-intelligence-agent",
  "version": "1.0.0",
  "timestamp": "2024-11-21T..."
}
```

### Get Server Info
```bash
curl http://127.0.0.1:8080/info
```

### Test API Endpoints
```bash
# Get latest briefing
curl http://127.0.0.1:8080/briefing

# Get analysis results
curl http://127.0.0.1:8080/analysis

# Get data stats
curl http://127.0.0.1:8080/data/stats

# Trigger workflow
curl -X POST http://127.0.0.1:8080/orchestrator/run
```

## 📋 Server Endpoints

### GET `/health`
Health check endpoint.

### GET `/info`
Server and system information.

### GET `/briefing`
Get latest daily briefing (returns 404 if no briefing exists).

### GET `/analysis`
Get latest analysis results.

### POST `/orchestrator/run`
Trigger full workflow (collect → enrich → analyze → summarize).

### POST `/orchestrator/collect`
Trigger data collection only.

### GET `/data/stats`
Get data statistics.

## 🔍 Debugging

### Check Server Status
```bash
# Check if server is running
lsof -i :8080

# Check server logs
# (Logs are printed to console when running)
```

### View Server Configuration
```bash
cd startup-intelligence-agent/backend/src
source ../venv/bin/activate
python3 << 'PYEOF'
from config.settings import settings
print(f"HOST: {settings.HOST}")
print(f"PORT: {settings.PORT}")
PYEOF
```

### Test Port Availability
```bash
# Try to connect to port
nc -zv 127.0.0.1 8080

# If port is available, you'll see "Connection refused"
# If port is in use, you'll see "succeeded"
```

## 🐳 Docker/Production

For Docker or production deployment:

```env
HOST=0.0.0.0  # Allow external connections
PORT=8080
```

The server will bind to all network interfaces.

## ✅ Verification

After starting the server:

1. **Check server is running:**
   ```bash
   curl http://127.0.0.1:8080/health
   ```

2. **Check server logs** show:
   ```
   Starting server on http://127.0.0.1:8080
   INFO:     Uvicorn running on http://127.0.0.1:8080
   ```

3. **No error messages** about address/port binding

---

**Your server should now start without address/port errors!** 🚀

