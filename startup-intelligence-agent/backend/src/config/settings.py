"""Configuration manager for Startup Intelligence Agent."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
# Try multiple possible locations for .env file
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # startup-intelligence-agent/.env
    Path(__file__).parent.parent.parent.parent.parent / ".env",  # Alternative location
    Path.cwd() / ".env",  # Current working directory
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        env_loaded = True
        break

# If no .env found, try loading from current directory without path
if not env_loaded:
    load_dotenv()  # Load from current directory or parent directories

class Settings:
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def LLM_API_KEY(self) -> Optional[str]:
        """Get the appropriate LLM API key based on provider."""
        if self.LLM_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        elif self.LLM_PROVIDER == "anthropic":
            return self.ANTHROPIC_API_KEY
        return None
    
    # Docker MCP Hub Agent URLs
    NEWS_SCRAPER_URL: str = os.getenv("NEWS_SCRAPER_URL", "http://localhost:3001")
    STARTUP_API_URL: str = os.getenv("STARTUP_API_URL", "http://localhost:3002")
    GITHUB_MONITOR_URL: str = os.getenv("GITHUB_MONITOR_URL", "http://localhost:3003")
    
    # Database
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH", 
        str(Path(__file__).parent.parent.parent.parent.parent / "storage" / "intelligence.db")
    )
    
    # E2B Sandbox
    E2B_API_KEY: Optional[str] = os.getenv("E2B_API_KEY")
    E2B_TEMPLATE: str = os.getenv("E2B_TEMPLATE", "base")  # Default to 'base' template
    SANDBOX_ID: Optional[str] = os.getenv("SANDBOX_ID")
    
    # Server
    PORT: int = int(os.getenv("PORT", "8080"))
    # Default to 127.0.0.1 for better macOS compatibility (0.0.0.0 can cause issues)
    HOST: str = os.getenv("HOST", "127.0.0.1")

# Create global settings instance
settings = Settings()

