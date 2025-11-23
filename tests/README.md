# Test Files Directory

This directory contains all test files for the Startup Intelligence Agent system.

## Test Files

### Integration Tests

- **`test_workflow_reporting.py`** - Tests workflow reporting endpoints
  - Tests `/workflow/health`
  - Tests `/workflow/report`
  - Tests `/workflow/daily-report`
  - Usage: `python3 test_workflow_reporting.py`

- **`test_full_workflow.py`** - Tests the complete end-to-end workflow
  - Tests data collection from all agents
  - Tests data storage
  - Tests enrichment, analysis, and summarization
  - Usage: `python3 test_full_workflow.py`

- **`test_data_collectors.sh`** - Tests data collector agent health endpoints
  - Tests news-scraper agent
  - Tests startup-api agent
  - Tests github-monitor agent
  - Usage: `./test_data_collectors.sh`

### Unit Tests (from startup-intelligence-agent/)

- **`test_server.py`** - Tests server imports and basic functionality
- **`test_imports.py`** - Tests all module imports
- **`test_orchestrator.py`** - Tests orchestrator workflow
- **`test_all_agents.py`** - Tests all agents (Enrichment, Analysis, Summarizer)
- **`test_endpoints.sh`** - Shell script to test API endpoints

## Running Tests

### Prerequisites

1. Ensure the server is running:
   ```bash
   cd ../startup-intelligence-agent/backend/src
   python3 main.py
   ```

2. Ensure data collector agents are running:
   ```bash
   cd ../../../
   ./start_services.sh
   ```

### Run All Tests

```bash
# From project root
cd tests

# Test workflow reporting
python3 test_workflow_reporting.py

# Test full workflow
python3 test_full_workflow.py

# Test data collectors
./test_data_collectors.sh
```

### Run Individual Tests

```bash
# Workflow reporting
python3 test_workflow_reporting.py

# Full workflow
python3 test_full_workflow.py

# Data collectors
./test_data_collectors.sh
```

## Test Results

Test results and documentation are stored in:
- `../startup-intelligence-agent/TEST_RESULTS.md`
- `../startup-intelligence-agent/ORCHESTRATOR_TEST_RESULTS.md`
- `../startup-intelligence-agent/AGENTS_IMPLEMENTATION_STATUS.md`

## Notes

- All test files assume the server is running on `http://localhost:8080`
- Data collector agents should be running on ports 3001, 3002, 3003
- Some tests require LLM API keys to be configured (see `../startup-intelligence-agent/LLM_API_SETUP.md`)

