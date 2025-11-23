# Test Suite Documentation

## Overview

This directory contains comprehensive tests for the Startup Intelligence Agent system, organized into three categories:

- **Unit Tests** (`unit/`) - Fast, isolated tests for individual components
- **Integration Tests** (`integration/`) - Tests for component interactions
- **End-to-End Tests** (`e2e/`) - Full system tests requiring running services

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_database.py
│   ├── test_enrichment_agent.py
│   ├── test_analysis_agent.py
│   └── test_summarizer_agent.py
├── integration/             # Integration tests
│   ├── test_orchestrator_workflow.py
│   └── test_api_endpoints.py
└── e2e/                     # End-to-end tests
│   ├── test_full_system.py
│   └── test_data_quality.py
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
cd startup-intelligence-agent/backend
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run by Category

**Unit tests only (fast):**
```bash
pytest tests/unit/ -v -m unit
```

**Integration tests:**
```bash
pytest tests/integration/ -v -m integration
```

**End-to-end tests (requires running services):**
```bash
pytest tests/e2e/ -v -m e2e
```

### Run Specific Test Files

```bash
# Test database operations
pytest tests/unit/test_database.py -v

# Test orchestrator workflow
pytest tests/integration/test_orchestrator_workflow.py -v

# Test full system
pytest tests/e2e/test_full_system.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Test Markers

Tests are marked with categories for easy filtering:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow tests (may take minutes)
- `@pytest.mark.requires_llm` - Tests requiring LLM API key
- `@pytest.mark.requires_agents` - Tests requiring data collector agents

### Filter by Marker

```bash
# Run only fast unit tests
pytest -m unit -v

# Skip slow tests
pytest -m "not slow" -v

# Run only tests that don't require external services
pytest -m "unit and not requires_agents" -v
```

## Test Requirements

### Unit Tests
- No external dependencies
- Use mocked services
- Run in isolation
- Fast execution (< 1 second each)

### Integration Tests
- May require database
- Use mocked HTTP clients
- Test component interactions
- Moderate execution time

### End-to-End Tests
- **Require running services:**
  - FastAPI server running on `http://localhost:8080`
  - Data collector agents (optional, some tests skip if unavailable)
- Test complete workflows
- Longer execution time (minutes)

## Setting Up for E2E Tests

1. **Start the server:**
   ```bash
   cd startup-intelligence-agent/backend/src
   python main.py
   ```

2. **Start data collector agents (optional):**
   ```bash
   cd data-collector-agents
   docker-compose up -d
   ```

3. **Run E2E tests:**
   ```bash
   pytest tests/e2e/ -v -m e2e
   ```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_db` - Temporary database for testing
- `sample_news_article` - Sample news article data
- `sample_funding_round` - Sample funding round data
- `sample_launch` - Sample product launch data
- `sample_github_repo` - Sample GitHub repository data
- `sample_github_signal` - Sample GitHub signal data
- `mock_httpx_client` - Mocked HTTP client
- `mock_llm_client` - Mocked LLM client
- `mock_data_collector_responses` - Mocked agent responses

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd startup-intelligence-agent/backend
    pip install -r requirements.txt
    pytest tests/unit tests/integration -v --cov=src
```

## Troubleshooting

### Tests Fail with Import Errors

Ensure you're running tests from the `backend` directory:
```bash
cd startup-intelligence-agent/backend
pytest tests/ -v
```

### E2E Tests Fail with Connection Errors

1. Verify server is running: `curl http://localhost:8080/health`
2. Check data collector agents are accessible
3. Review test markers - some tests skip if services unavailable

### Database Lock Errors

Tests use temporary databases, but if you see lock errors:
- Ensure no other processes are using the test database
- Check for leftover test database files

## Adding New Tests

1. **Unit Tests** - Test individual component methods
2. **Integration Tests** - Test component interactions
3. **E2E Tests** - Test complete workflows

Follow existing test patterns and use appropriate fixtures.

## Test Coverage Goals

- **Unit Tests:** > 80% coverage
- **Integration Tests:** Cover all major workflows
- **E2E Tests:** Cover critical user paths

