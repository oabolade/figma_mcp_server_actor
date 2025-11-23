"""
Pytest fixtures and configuration for all tests.
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from database.db import Database
from config.settings import settings


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    db = Database(path)
    yield db
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def sample_news_article():
    """Sample news article data."""
    from datetime import datetime, timedelta
    # Use recent date to ensure it's within the 7-day window
    recent_date = datetime.now() - timedelta(days=1)
    return {
        "title": "Test Startup Raises $10M Series A",
        "url": f"https://example.com/news/test-startup-{datetime.now().timestamp()}",
        "source": "techcrunch",
        "timestamp": recent_date.isoformat(),
        "summary": "A test startup has raised $10M in Series A funding."
    }


@pytest.fixture
def sample_funding_round():
    """Sample funding round data."""
    from datetime import datetime, timedelta
    recent_date = datetime.now() - timedelta(days=1)
    return {
        "company_name": "Test Startup",
        "amount": "$10M",
        "type": "Series A",
        "date": recent_date.strftime("%Y-%m-%d"),
        "source": "crunchbase",
        "link": f"https://example.com/funding/test-startup-{datetime.now().timestamp()}"
    }


@pytest.fixture
def sample_launch():
    """Sample product launch data."""
    from datetime import datetime, timedelta
    recent_date = datetime.now() - timedelta(days=1)
    return {
        "name": "Test Product",
        "description": "A revolutionary test product",
        "date": recent_date.strftime("%Y-%m-%d"),
        "source": "producthunt",
        "link": f"https://example.com/launch/test-product-{datetime.now().timestamp()}"
    }


@pytest.fixture
def sample_github_repo():
    """Sample GitHub repository data."""
    from datetime import datetime, timedelta
    recent_date = datetime.now() - timedelta(days=1)
    return {
        "name": f"test-repo-{datetime.now().timestamp()}",
        "full_name": f"testuser/test-repo-{datetime.now().timestamp()}",
        "description": "A test repository",
        "url": f"https://github.com/testuser/test-repo-{datetime.now().timestamp()}",
        "stars": 100,
        "language": "Python",
        "created_at": recent_date.isoformat(),
        "updated_at": recent_date.isoformat()
    }


@pytest.fixture
def sample_github_signal():
    """Sample GitHub signal data."""
    return {
        "repository_id": "test-repo-id",
        "signal_type": "trending",
        "description": "Repository is trending",
        "detected_at": "2024-01-15T10:00:00Z",
        "date": "2024-01-15",
        "indicator": "trending",
        "confidence": 0.8,
        "metadata": {"stars_today": 50}
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_client.return_value.__aexit__.return_value = None
        yield mock_instance


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    with patch('llm.client.LLMClient') as mock_client:
        mock_instance = MagicMock()
        mock_instance.generate.return_value = {
            "content": '{"trends": [], "opportunities": []}',
            "model": "test-model",
            "usage": {"total_tokens": 100}
        }
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_data_collector_responses():
    """Mock responses from data collector agents."""
    return {
        "news": {
            "total": 2,
            "sources": {
                "techcrunch": {
                    "count": 1,
                    "articles": [{
                        "title": "Test Article",
                        "url": "https://example.com/article",
                        "source": "techcrunch",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "summary": "Test summary"
                    }]
                }
            }
        },
        "startup": {
            "funding": [{
                "company_name": "Test Company",
                "amount": "$10M",
                "round_type": "Series A",
                "date": "2024-01-15",
                "source": "crunchbase",
                "url": "https://example.com/funding"
            }],
            "launches": [{
                "name": "Test Product",
                "description": "Test description",
                "date": "2024-01-15",
                "source": "producthunt",
                "url": "https://example.com/launch"
            }]
        },
        "github": {
            "trending": [{
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "description": "Test repo",
                "url": "https://github.com/testuser/test-repo",
                "stars": 100,
                "language": "Python"
            }],
            "signals": [{
                "repository_id": "test-repo-id",
                "signal_type": "trending",
                "description": "Repository is trending",
                "detected_at": "2024-01-15T10:00:00Z"
            }]
        }
    }


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings to defaults before each test."""
    # Store original values
    original_db_path = settings.DATABASE_PATH
    
    yield
    
    # Restore original values
    settings.DATABASE_PATH = original_db_path

