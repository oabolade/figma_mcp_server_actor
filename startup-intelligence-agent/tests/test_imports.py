#!/usr/bin/env python3
"""Simple test to verify all imports work."""
import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    errors = []
    
    try:
        from config.settings import settings
        print(f"  ✓ Config loaded (PORT={settings.PORT}, LLM_PROVIDER={settings.LLM_PROVIDER})")
    except Exception as e:
        print(f"  ✗ Config import failed: {e}")
        errors.append("config")
    
    try:
        from api.server import app
        print(f"  ✓ FastAPI app loaded (title: {app.title})")
    except Exception as e:
        print(f"  ✗ FastAPI app import failed: {e}")
        errors.append("api")
    
    try:
        from orchestrator.agent import OrchestratorAgent
        agent = OrchestratorAgent()
        print("  ✓ OrchestratorAgent created")
    except Exception as e:
        print(f"  ✗ OrchestratorAgent import failed: {e}")
        errors.append("orchestrator")
    
    try:
        from analysis.agent import AnalysisAgent
        analysis = AnalysisAgent()
        print("  ✓ AnalysisAgent created")
    except Exception as e:
        print(f"  ✗ AnalysisAgent import failed: {e}")
        errors.append("analysis")
    
    try:
        from summarizer.agent import SummarizerAgent
        summarizer = SummarizerAgent()
        print("  ✓ SummarizerAgent created")
    except Exception as e:
        print(f"  ✗ SummarizerAgent import failed: {e}")
        errors.append("summarizer")
    
    try:
        from enrichment.agent import EnrichmentAgent
        enrichment = EnrichmentAgent()
        print("  ✓ EnrichmentAgent created")
    except Exception as e:
        print(f"  ✗ EnrichmentAgent import failed: {e}")
        errors.append("enrichment")
    
    try:
        from llm.client import LLMClient
        print("  ✓ LLMClient imported")
    except Exception as e:
        print(f"  ✗ LLMClient import failed: {e}")
        errors.append("llm")
    
    if errors:
        print(f"\n✗ Failed imports: {', '.join(errors)}")
        return False
    else:
        print("\n✓ All imports successful!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

