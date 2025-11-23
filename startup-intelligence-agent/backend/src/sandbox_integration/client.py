"""E2B Client - High-level client for E2B sandbox operations."""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict
from .sandbox_manager import SandboxManager

from config.settings import settings

logger = logging.getLogger(__name__)


class E2BClient:
    """High-level client for E2B sandbox operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize E2B client.
        
        Args:
            api_key: E2B API key. If None, uses E2B_API_KEY from settings.
        """
        self.manager = SandboxManager(api_key=api_key)
        self.sandbox_url: Optional[str] = None
    
    async def deploy(
        self,
        backend_path: Optional[Path] = None,
        template: Optional[str] = None,
        reconnect_to_existing: bool = False
    ) -> str:
        """
        Deploy backend to E2B sandbox.
        
        Args:
            backend_path: Path to backend directory. If None, uses default.
            template: E2B template name. If None, uses E2B_TEMPLATE from settings.
            reconnect_to_existing: If True, reconnect to existing sandbox (from SANDBOX_ID)
            
        Returns:
            Sandbox URL for accessing the server
        """
        try:
            # Determine backend path
            if backend_path is None:
                # Default: startup-intelligence-agent/backend/src
                current_file = Path(__file__)
                backend_path = current_file.parent.parent.parent.parent / "backend" / "src"
            
            # Create new sandbox (E2B doesn't support reconnecting to existing sandboxes)
            # Note: SANDBOX_ID is kept for future compatibility but not currently used
            if reconnect_to_existing and settings.SANDBOX_ID:
                logger.info(
                    f"Note: E2B SDK doesn't support reconnecting to existing sandboxes. "
                    f"Creating a new sandbox instead. (Requested ID: {settings.SANDBOX_ID})"
                )
            else:
                logger.info("Creating new sandbox")
            
            await self.manager.create_sandbox(template=template)
            
            # Upload backend code
            await self.manager.upload_code(
                source_path=backend_path,
                target_path="/app"
            )
            
            # Upload requirements.txt
            requirements_path = backend_path.parent / "requirements.txt"
            if requirements_path.exists():
                await self.manager.upload_file(
                    local_path=requirements_path,
                    sandbox_path="/app/requirements.txt"
                )
            else:
                logger.warning(f"Requirements file not found: {requirements_path}")
            
            # Set environment variables
            env_vars = {
                "LLM_PROVIDER": settings.LLM_PROVIDER,
                "LLM_MODEL": settings.LLM_MODEL,
                "NEWS_SCRAPER_URL": settings.NEWS_SCRAPER_URL,
                "STARTUP_API_URL": settings.STARTUP_API_URL,
                "GITHUB_MONITOR_URL": settings.GITHUB_MONITOR_URL,
                "PORT": str(settings.PORT),
                "HOST": settings.HOST,
                # Set database path to /app/storage (writable location in sandbox)
                "DATABASE_PATH": "/app/storage/intelligence.db",
            }
            
            # Add API keys if available
            if settings.OPENAI_API_KEY:
                env_vars["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            if settings.ANTHROPIC_API_KEY:
                env_vars["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
            
            await self.manager.set_environment_variables(env_vars)
            
            # Create storage directory with proper permissions before starting server
            logger.info("Creating storage directory for database...")
            try:
                # Create /app/storage directory
                self.manager.sandbox.files.make_dir("/app/storage")
                logger.info("Storage directory created successfully")
            except Exception as e:
                logger.warning(f"Could not create storage directory (may already exist): {e}")
            
            # Install dependencies
            await self.manager.install_dependencies()
            
            # Start server
            # Note: Files are uploaded to /app, so main.py is at /app/main.py (not /app/src/main.py)
            self.sandbox_url = await self.manager.start_server(
                command="python3 /app/main.py",
                ports=[8080]
            )
            
            logger.info(f"✅ Deployment complete! Server running at: https://{self.sandbox_url}")
            return self.sandbox_url
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise
    
    async def close(self) -> None:
        """Close sandbox connection."""
        await self.manager.close()
        self.sandbox_url = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

