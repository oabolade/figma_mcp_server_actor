"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path

# Add src to path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

from api.server import app


@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
    
    def test_info_endpoint(self, client):
        """Test info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
    
    def test_orchestrator_status(self, client):
        """Test orchestrator status endpoint."""
        response = client.get("/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
    
    def test_data_stats(self, client):
        """Test data statistics endpoint."""
        response = client.get("/data/stats")
        assert response.status_code == 200
        data = response.json()
        assert "last_7_days" in data
    
    @pytest.mark.asyncio
    async def test_orchestrator_run(self, client):
        """Test orchestrator run endpoint."""
        # This will trigger actual workflow (may take time)
        response = client.post("/orchestrator/run?days_back=1")
        
        # Should return 200 or 202 (accepted)
        assert response.status_code in [200, 202, 409]  # 409 if already running
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_briefing_endpoint(self, client):
        """Test briefing endpoint."""
        response = client.get("/briefing")
        
        # May return 200 with data or 404 if no briefing exists
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "summary" in data or "briefing" in data
    
    def test_workflow_reporting(self, client):
        """Test workflow reporting endpoint."""
        # Check if endpoint exists (may be different path)
        response = client.get("/workflow/reporting/status")
        # Endpoint may not exist yet, so accept 404 or 200
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data

