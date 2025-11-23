"""E2B Sandbox Manager - Manages sandbox lifecycle and deployment."""
import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from e2b import Sandbox  # This now correctly imports from the E2B SDK package

from config.settings import settings

logger = logging.getLogger(__name__)


class SandboxManager:
    """Manages E2B sandbox lifecycle and deployment."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize sandbox manager.
        
        Args:
            api_key: E2B API key. If None, uses E2B_API_KEY from settings.
        """
        self.api_key = api_key or settings.E2B_API_KEY
        if not self.api_key:
            raise ValueError(
                "E2B_API_KEY not configured. Please set E2B_API_KEY environment variable."
            )
        self.sandbox: Optional[Sandbox] = None
        self.sandbox_id: Optional[str] = None
    
    async def create_sandbox(
        self,
        template: Optional[str] = None,
        cwd: str = "/app",
        fallback_templates: Optional[List[str]] = None
    ) -> Sandbox:
        """
        Create a new E2B sandbox.
        
        Args:
            template: E2B template name. If None, uses E2B_TEMPLATE from settings.
            cwd: Working directory in sandbox
            fallback_templates: List of alternative templates to try if primary fails.
                               Default: ["base", "ubuntu", "python3"]
            
        Returns:
            Sandbox instance
            
        Raises:
            ValueError: If API key is invalid
            RuntimeError: If all template attempts fail
        """
        # Use template from settings if not provided
        if template is None:
            template = settings.E2B_TEMPLATE
        
        # Default fallback templates (try base first, then python3)
        # Note: "ubuntu" is not a standard E2B template name
        if fallback_templates is None:
            fallback_templates = ["base", "python3"]
        
        # Remove the primary template from fallback list if it's already there
        if template in fallback_templates:
            fallback_templates = [t for t in fallback_templates if t != template]
        
        # Combine primary template with fallbacks
        templates_to_try = [template] + fallback_templates
        
        logger.info(f"Creating E2B sandbox. Will try templates in order: {templates_to_try}")
        
        # Validate API key before attempting to create sandbox
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "E2B_API_KEY is empty or not set. Please set a valid E2B_API_KEY environment variable."
            )
        
        # Check API key format (E2B API keys typically start with specific prefixes)
        if len(self.api_key.strip()) < 20:
            logger.warning(
                f"E2B_API_KEY appears to be too short ({len(self.api_key.strip())} chars). "
                "Please verify your API key is correct."
            )
        
        # Try each template until one succeeds
        last_error = None
        for attempt_template in templates_to_try:
            try:
                logger.info(f"Attempting to create sandbox with template: {attempt_template}")
                
                # E2B SDK uses Sandbox.create() method, not direct instantiation
                # The create method accepts template and api_key
                # Note: E2B SDK may also check E2B_API_KEY environment variable if api_key is not provided
                self.sandbox = Sandbox.create(
                    template=attempt_template,
                    api_key=self.api_key.strip()  # Strip whitespace in case of accidental spaces
                )
                self.sandbox_id = self.sandbox.sandbox_id
                logger.info(f"✅ Sandbox created successfully with template '{attempt_template}': {self.sandbox_id}")
                
                # Note: Working directory is set per-command via cwd parameter in process.start()
                # We don't need to set it globally here
                
                return self.sandbox
                
            except Exception as e:
                error_msg = str(e)
                last_error = e
                
                # Check if it's a template access error (403)
                if "403" in error_msg or "does not have access" in error_msg.lower():
                    logger.warning(
                        f"❌ Template '{attempt_template}' not accessible (403). "
                        f"Error: {error_msg}. Trying next template..."
                    )
                    # Clean up failed sandbox if it was created
                    if self.sandbox:
                        try:
                            await self.close()
                        except Exception:
                            pass
                    # Continue to next template
                    continue
                else:
                    # For other errors, check if sandbox was actually created
                    # If sandbox was created but we got an error accessing its methods,
                    # that's a different issue - don't treat it as template failure
                    if self.sandbox and self.sandbox_id:
                        # Sandbox was created successfully, but we hit an error using it
                        # This is likely an SDK API issue, not a template access issue
                        logger.warning(
                            f"⚠️  Sandbox created but encountered error: {error_msg}. "
                            f"This may be an SDK API compatibility issue."
                        )
                        # Don't continue to next template - return the sandbox we created
                        return self.sandbox
                    else:
                        # Sandbox creation actually failed
                        logger.warning(
                            f"❌ Failed to create sandbox with template '{attempt_template}': {error_msg}. "
                            f"Trying next template..."
                        )
                        continue
        
        # If we get here, all templates failed
        error_summary = f"Failed to create sandbox with any of the attempted templates: {templates_to_try}"
        logger.error(f"❌ {error_summary}")
        logger.error(f"Last error: {last_error}")
        logger.info(
            "\n💡 Troubleshooting tips:\n"
            "1. Check your E2B API key is valid: python scripts/verify_e2b_key.py\n"
            "2. Verify your E2B account has access to the templates\n"
            "3. Try setting E2B_TEMPLATE in .env to a template you have access to\n"
            "4. Check E2B dashboard for available templates: https://e2b.dev/dashboard\n"
            "5. Contact E2B support if template access issues persist"
        )
        raise RuntimeError(f"{error_summary}. Last error: {last_error}")
    
    async def connect_to_sandbox(self, sandbox_id: str) -> Sandbox:
        """
        Connect to an existing sandbox.
        
        Note: E2B SDK doesn't support reconnecting to existing sandboxes directly.
        This method will create a new sandbox instead. The sandbox_id parameter
        is kept for API compatibility but is not used.
        
        Args:
            sandbox_id: Existing sandbox ID (not used, kept for compatibility)
            
        Returns:
            Sandbox instance
        """
        logger.warning(
            f"E2B SDK doesn't support reconnecting to existing sandboxes. "
            f"Creating a new sandbox instead. (Requested ID: {sandbox_id})"
        )
        
        # E2B sandboxes are ephemeral - we need to create a new one
        # The sandbox_id parameter is kept for API compatibility
        return await self.create_sandbox()
    
    async def upload_code(
        self,
        source_path: Path,
        target_path: str = "/app",
        exclude_patterns: Optional[List[str]] = None
    ) -> None:
        """
        Upload backend code to sandbox.
        
        Args:
            source_path: Local path to backend code
            target_path: Target directory in sandbox
            exclude_patterns: Patterns to exclude (e.g., ["__pycache__", "*.pyc"])
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create_sandbox() first.")
        
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "*.pyc", "*.db", "venv", ".venv"]
        
        logger.info(f"Uploading code from {source_path} to {target_path}")
        
        try:
            # E2B SDK uses sandbox.files, not sandbox.filesystem
            if not hasattr(self.sandbox, 'files'):
                raise RuntimeError("E2B Sandbox files API not available")
            
            # Upload all Python files
            for file_path in source_path.rglob("*.py"):
                # Skip excluded patterns
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                
                relative_path = file_path.relative_to(source_path)
                sandbox_path = f"{target_path}/{relative_path}"
                
                # Create directory if needed
                dir_path = str(Path(sandbox_path).parent)
                try:
                    self.sandbox.files.make_dir(dir_path)
                except Exception as e:
                    # Directory might already exist, that's okay
                    logger.debug(f"Directory creation (may already exist): {dir_path} - {e}")
                
                # Upload file - E2B SDK files.write() expects bytes or string
                with open(file_path, "rb") as f:
                    content = f.read()
                    # E2B SDK files.write() accepts bytes
                    self.sandbox.files.write(sandbox_path, content)
                
                logger.debug(f"Uploaded: {relative_path} -> {sandbox_path}")
            
            logger.info("Code upload completed")
        except Exception as e:
            logger.error(f"Failed to upload code: {e}")
            raise
    
    async def upload_file(self, local_path: Path, sandbox_path: str) -> None:
        """
        Upload a single file to sandbox.
        
        Args:
            local_path: Local file path
            sandbox_path: Target path in sandbox
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create_sandbox() first.")
        
        logger.info(f"Uploading file: {local_path} -> {sandbox_path}")
        
        try:
            # E2B SDK uses sandbox.files, not sandbox.filesystem
            if not hasattr(self.sandbox, 'files'):
                raise RuntimeError("E2B Sandbox files API not available")
            
            # Create directory if needed
            dir_path = str(Path(sandbox_path).parent)
            try:
                self.sandbox.files.make_dir(dir_path)
            except Exception as e:
                # Directory might already exist, that's okay
                logger.debug(f"Directory creation (may already exist): {dir_path} - {e}")
            
            with open(local_path, "rb") as f:
                content = f.read()
                # E2B SDK files.write() accepts bytes
                self.sandbox.files.write(sandbox_path, content)
            
            logger.info(f"File uploaded: {sandbox_path}")
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    async def set_environment_variables(self, env_vars: Dict[str, str]) -> None:
        """
        Set environment variables in sandbox.
        
        Args:
            env_vars: Dictionary of environment variables
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create_sandbox() first.")
        
        logger.info(f"Setting {len(env_vars)} environment variables")
        
        try:
            # E2B SDK doesn't have sandbox.env.set() method
            # Instead, we can:
            # 1. Create a .env file and upload it
            # 2. Use commands to export variables (but they won't persist)
            # 3. Set them in the shell profile files
            
            # Best approach: Create a .env file and upload it
            # This ensures variables are available for all processes
            env_file_content = "\n".join([f"{key}={value}" for key, value in env_vars.items()])
            
            # Upload .env file to /app/.env
            self.sandbox.files.write("/app/.env", env_file_content.encode('utf-8'))
            
            # Also set them in the current shell session via commands
            # This makes them available immediately
            if hasattr(self.sandbox, 'commands') and hasattr(self.sandbox.commands, 'run'):
                # Export variables for current session
                export_commands = "\n".join([f"export {key}='{value}'" for key, value in env_vars.items()])
                # Write to .bashrc or .profile so they're available in future sessions
                profile_content = f"\n# Environment variables set by deployment\n{export_commands}\n"
                
                # Append to .bashrc
                try:
                    # Read existing .bashrc if it exists
                    try:
                        existing_bashrc = self.sandbox.files.read("/root/.bashrc")
                        profile_content = existing_bashrc.decode('utf-8') + profile_content
                    except Exception:
                        pass  # .bashrc doesn't exist, that's okay
                    
                    self.sandbox.files.write("/root/.bashrc", profile_content.encode('utf-8'))
                except Exception as e:
                    logger.debug(f"Could not write to .bashrc: {e}")
            
            logger.info("Environment variables set (via .env file and shell profile)")
            for key, value in env_vars.items():
                logger.debug(f"Set {key}={value[:20]}..." if len(value) > 20 else f"Set {key}={value}")
            
        except Exception as e:
            logger.error(f"Failed to set environment variables: {e}")
            raise
    
    async def install_dependencies(self, requirements_path: str = "/app/requirements.txt") -> None:
        """
        Install Python dependencies in sandbox.
        
        Args:
            requirements_path: Path to requirements.txt in sandbox
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create_sandbox() first.")
        
        logger.info("Installing dependencies...")
        
        try:
            # E2B SDK uses commands.run() for executing commands
            if hasattr(self.sandbox, 'commands') and hasattr(self.sandbox.commands, 'run'):
                result = self.sandbox.commands.run(
                    f"pip install -r {requirements_path}",
                    cwd="/app"
                )
                exit_code = result.exit_code if hasattr(result, 'exit_code') else 0
                error_output = result.stderr if hasattr(result, 'stderr') else ""
                stdout = result.stdout if hasattr(result, 'stdout') else ""
            elif hasattr(self.sandbox, 'process'):
                # Fallback to process API if available
                process = self.sandbox.process.start(
                    f"pip install -r {requirements_path}",
                    cwd="/app"
                )
                process.wait()
                exit_code = process.exit_code
                error_output = process.stderr.read() if hasattr(process, 'stderr') else ""
            else:
                raise RuntimeError("E2B Sandbox commands API not available")
            
            if exit_code != 0:
                raise RuntimeError(f"Failed to install dependencies (exit code {exit_code}): {error_output}")
            
            logger.info("Dependencies installed successfully")
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise
    
    async def start_server(
        self,
        command: str = "python3 /app/main.py",
        ports: List[int] = [8080],
        cwd: str = "/app"
    ) -> str:
        """
        Start the API server in sandbox.
        
        Args:
            command: Command to start server
            ports: List of ports to expose
            cwd: Working directory
            
        Returns:
            Sandbox URL for accessing the server
        """
        if not self.sandbox:
            raise RuntimeError("Sandbox not created. Call create_sandbox() first.")
        
        logger.info(f"Starting server: {command}")
        
        try:
            # Start server process in background - E2B SDK commands.run() times out for long-running processes
            # Use nohup and & to run server in background, then redirect output
            background_command = f"nohup {command} > /app/server.log 2>&1 &"
            
            if hasattr(self.sandbox, 'commands') and hasattr(self.sandbox.commands, 'run'):
                # Run server in background using nohup
                # This prevents the blocking timeout issue with long-running servers
                logger.info(f"Starting server in background: {command}")
                
                # Try with timeout parameter first, fallback without if not supported
                try:
                    result = self.sandbox.commands.run(
                        background_command,
                        cwd=cwd,
                        timeout=10  # Short timeout just to start the background process
                    )
                except TypeError:
                    # timeout parameter not supported, try without it
                    result = self.sandbox.commands.run(
                        background_command,
                        cwd=cwd
                    )
                
                if result.exit_code != 0:
                    # Check if server.log exists and show error
                    try:
                        log_content = self.sandbox.files.read("/app/server.log")
                        error_msg = log_content.decode('utf-8') if isinstance(log_content, bytes) else log_content
                        logger.error(f"Server startup error:\n{error_msg}")
                    except Exception:
                        pass
                    raise RuntimeError(f"Server failed to start: {result.stderr}")
                
                # Give server a moment to start
                import time
                time.sleep(2)
                
                # Check if server process is running
                check_result = self.sandbox.commands.run("ps aux | grep 'python3 /app/main.py' | grep -v grep", cwd=cwd)
                if check_result.exit_code == 0 and check_result.stdout:
                    logger.info("✅ Server process is running")
                else:
                    # Check server.log for errors
                    try:
                        log_content = self.sandbox.files.read("/app/server.log")
                        error_msg = log_content.decode('utf-8') if isinstance(log_content, bytes) else log_content
                        logger.warning(f"Server may not have started. Log content:\n{error_msg}")
                    except Exception as e:
                        logger.warning(f"Could not read server.log: {e}")
            else:
                raise RuntimeError("E2B Sandbox commands API not available for starting server")
            
            # Expose ports - E2B SDK may use different method
            if hasattr(self.sandbox, 'expose_port'):
                for port in ports:
                    self.sandbox.expose_port(port)
            elif hasattr(self.sandbox, 'ports') and hasattr(self.sandbox.ports, 'expose'):
                for port in ports:
                    self.sandbox.ports.expose(port)
            else:
                logger.warning("Could not expose ports - port exposure API not found")
            
            # Get sandbox URL - E2B SDK provides get_host() method
            if hasattr(self.sandbox, 'get_host'):
                # E2B SDK get_host() returns the hostname for a specific port
                sandbox_url = self.sandbox.get_host(ports[0])
            elif hasattr(self.sandbox, 'get_hostname'):
                sandbox_url = self.sandbox.get_hostname(ports[0])
            elif hasattr(self.sandbox, 'get_url'):
                sandbox_url = self.sandbox.get_url(ports[0])
            elif hasattr(self.sandbox, 'hostname'):
                sandbox_url = self.sandbox.hostname
            elif hasattr(self.sandbox, 'sandbox_domain'):
                # Use sandbox_domain if available
                domain = self.sandbox.sandbox_domain
                sandbox_url = f"{domain}:{ports[0]}" if ":" not in domain else domain
            else:
                # Fallback: E2B sandboxes typically use e2b.dev domain
                # Format: {sandbox_id}.e2b.dev or similar
                sandbox_url = f"{self.sandbox_id}.e2b.dev"
            
            logger.info(f"Server started in background. Access at: https://{sandbox_url}")
            logger.info(f"Server logs available at: /app/server.log")
            
            return sandbox_url
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    async def close(self) -> None:
        """Close and cleanup sandbox."""
        if self.sandbox:
            logger.info(f"Closing sandbox: {self.sandbox_id}")
            try:
                # E2B SDK may use different methods for closing
                # Try multiple approaches based on SDK version
                closed = False
                
                # Method 1: Try close() method
                if hasattr(self.sandbox, 'close'):
                    try:
                        if asyncio.iscoroutinefunction(self.sandbox.close):
                            await self.sandbox.close()
                        else:
                            self.sandbox.close()
                        closed = True
                        logger.debug("Sandbox closed using close() method")
                    except Exception as e:
                        logger.debug(f"close() method failed: {e}")
                
                # Method 2: Try kill() method
                if not closed and hasattr(self.sandbox, 'kill'):
                    try:
                        if asyncio.iscoroutinefunction(self.sandbox.kill):
                            await self.sandbox.kill()
                        else:
                            self.sandbox.kill()
                        closed = True
                        logger.debug("Sandbox closed using kill() method")
                    except Exception as e:
                        logger.debug(f"kill() method failed: {e}")
                
                # Method 3: Try using context manager or del
                if not closed:
                    # E2B SDK may handle cleanup automatically via context manager
                    # or when the object is deleted
                    logger.debug("No explicit close method found - sandbox may auto-cleanup")
                    # Set to None to allow garbage collection
                    self.sandbox = None
                    closed = True
                
                if closed:
                    logger.info("Sandbox closed successfully")
                else:
                    logger.warning("Could not explicitly close sandbox - it may auto-cleanup")
                    
            except Exception as e:
                logger.error(f"Error closing sandbox: {e}")
            finally:
                self.sandbox = None
                self.sandbox_id = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        import asyncio
        asyncio.run(self.close())

