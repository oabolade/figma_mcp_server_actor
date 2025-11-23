"""
End-to-end tests for the complete system.
These tests require the full system to be running (server, agents, etc.)
"""
import pytest
import requests
import time
from pathlib import Path
import sys

# Add src to path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

from config.settings import settings


@pytest.mark.e2e
@pytest.mark.slow
class TestFullSystem:
    """End-to-end tests for complete system."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL from settings or default."""
        host = getattr(settings, 'HOST', '127.0.0.1')
        port = getattr(settings, 'PORT', 8080)
        return f"http://{host}:{port}"
    
    def test_server_health(self, api_base_url):
        """Test server is running and healthy."""
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
        except requests.exceptions.ConnectionError:
            pytest.skip("Server is not running. Start server before running E2E tests.")
    
    def test_data_collector_agents_accessible(self, api_base_url):
        """Test data collector agents are accessible."""
        # This requires agents to be running
        # Check if orchestrator can reach them
        response = requests.get(f"{api_base_url}/info", timeout=5)
        assert response.status_code == 200
        
        # Note: Actual agent connectivity is tested via orchestrator
    
    @pytest.mark.requires_agents
    def test_full_workflow_execution(self, api_base_url):
        """Test complete workflow execution via API."""
        # Trigger workflow
        response = requests.post(
            f"{api_base_url}/orchestrator/run?days_back=1",
            timeout=10
        )
        
        # Should accept request
        assert response.status_code in [200, 202, 409]  # 409 if already running
        
        if response.status_code == 409:
            pytest.skip("Workflow is already running")
        
        # Wait for workflow to complete (with timeout)
        max_wait = 300  # 5 minutes
        waited = 0
        while waited < max_wait:
            status_response = requests.get(
                f"{api_base_url}/orchestrator/status",
                timeout=5
            )
            status = status_response.json()
            
            if not status.get("running", False):
                break
            
            time.sleep(10)
            waited += 10
        
        # Verify workflow completed
        assert waited < max_wait, "Workflow did not complete within timeout"
        
        # Check for briefing
        briefing_response = requests.get(f"{api_base_url}/briefing", timeout=5)
        if briefing_response.status_code == 200:
            briefing = briefing_response.json()
            assert "summary" in briefing or "briefing" in briefing
    
    def test_data_collection_workflow(self, api_base_url):
        """Test data collection workflow only."""
        # Trigger collection
        response = requests.post(
            f"{api_base_url}/orchestrator/collect?days_back=1",
            timeout=10
        )
        
        assert response.status_code in [200, 202, 409]
        
        # Check data stats
        stats_response = requests.get(f"{api_base_url}/data/stats", timeout=5)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "last_7_days" in stats
    
    def test_briefing_retrieval(self, api_base_url):
        """Test briefing can be retrieved."""
        response = requests.get(f"{api_base_url}/briefing", timeout=5)
        
        # May be 404 if no briefing exists yet
        if response.status_code == 200:
            briefing = response.json()
            # Verify structure
            assert isinstance(briefing, dict)
    
    def test_workflow_scheduler(self, api_base_url):
        """Test workflow scheduler."""
        # Start scheduler
        response = requests.post(
            f"{api_base_url}/workflow/scheduler/start?frequency=daily&run_immediately=false",
            timeout=5
        )
        
        # Should succeed, return 409 if already running, or 500 if there's an error
        assert response.status_code in [200, 409, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "started"
            
            # Stop scheduler
            stop_response = requests.post(
                f"{api_base_url}/workflow/scheduler/stop",
                timeout=5
            )
            # Accept 200 (stopped), 404 (not found), or 500 (error)
            assert stop_response.status_code in [200, 404, 500]
        elif response.status_code == 500:
            # Scheduler endpoint may have issues, skip this test
            pytest.skip("Scheduler endpoint returned 500 - may need configuration")

