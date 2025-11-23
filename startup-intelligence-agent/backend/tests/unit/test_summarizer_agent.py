"""
Unit tests for SummarizerAgent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from summarizer.agent import SummarizerAgent
from database.db import Database


@pytest.mark.unit
class TestSummarizerAgent:
    """Test summarizer agent operations."""
    
    @pytest.fixture
    def summarizer_agent(self, temp_db, mock_llm_client):
        """Create summarizer agent with test database and mocked LLM."""
        with patch('summarizer.agent.Database', return_value=temp_db):
            with patch('summarizer.agent.LLMClient', return_value=mock_llm_client):
                agent = SummarizerAgent()
                agent.db = temp_db
                agent.llm_client = mock_llm_client
                return agent
    
    def test_summarizer_agent_initialization(self, summarizer_agent):
        """Test summarizer agent can be initialized."""
        assert summarizer_agent is not None
        assert summarizer_agent.db is not None
    
    @pytest.mark.asyncio
    async def test_create_briefing(self, summarizer_agent, mock_llm_client):
        """Test creating a briefing."""
        # Mock analysis result
        analysis_result = {
            "results": {
                "trends": [{"title": "Test Trend"}],
                "opportunities_for_founders": [],
                "opportunities_for_investors": []
            }
        }
        
        # Mock LLM response
        mock_llm_client.generate.return_value = {
            "content": "Test summary text",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }
        
        briefing = await summarizer_agent.create_briefing(analysis_result, days_back=7)
        
        assert briefing is not None
        assert 'summary' in briefing
        assert 'trends' in briefing
        assert 'funding_rounds' in briefing
        assert 'product_launches' in briefing
    
    @pytest.mark.asyncio
    async def test_create_briefing_without_llm(self, summarizer_agent):
        """Test creating briefing when LLM fails."""
        analysis_result = {
            "results": {
                "trends": [],
                "opportunities_for_founders": [],
                "opportunities_for_investors": []
            }
        }
        
        # Make LLM fail
        summarizer_agent.llm_client.generate.side_effect = Exception("LLM error")
        
        briefing = await summarizer_agent.create_briefing(analysis_result, days_back=7)
        
        # Should still create briefing with fallback summary
        assert briefing is not None
        assert 'summary' in briefing
    
    def test_format_trends(self, summarizer_agent):
        """Test formatting trends."""
        trends = [{"title": "Test Trend", "description": "Test"}]
        formatted = summarizer_agent._format_trends(trends)
        
        assert isinstance(formatted, list)
        assert len(formatted) == 1
    
    def test_parse_funding_amount(self, summarizer_agent):
        """Test parsing funding amounts."""
        assert summarizer_agent._parse_funding_amount("$10M") == 10000000
        assert summarizer_agent._parse_funding_amount("$1.5B") == 1500000000
        assert summarizer_agent._parse_funding_amount("$500K") == 500000
        assert summarizer_agent._parse_funding_amount("invalid") == 0

