"""Main entry point for Startup Intelligence Agent."""
import uvicorn
from config.settings import settings
import socket
import sys

def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding by attempting to bind to it."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return True  # Port is available if bind succeeds
            except OSError:
                return False  # Port is in use if bind fails
    except Exception:
        # Fallback: try to connect to check if port is in use
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True  # If we can't check, assume it's available

if __name__ == "__main__":
    # Determine actual binding host (apply macOS conversion first)
    host = settings.HOST
    if host == "0.0.0.0":
        # On macOS, 0.0.0.0 can cause issues. Use 127.0.0.1 for local dev
        import platform
        if platform.system() == "Darwin":  # macOS
            host = "127.0.0.1"
            print(f"Note: Using 127.0.0.1 instead of 0.0.0.0 on macOS for compatibility")
    
    # Check if port is available BEFORE allocating resources
    # This prevents resource leaks if the port is already in use
    if not is_port_available(host, settings.PORT):
        print(f"ERROR: Port {settings.PORT} on {host} is already in use!")
        print(f"\nTo fix this:")
        print(f"  1. Stop the process using port {settings.PORT}")
        print(f"  2. Or change PORT in .env file to a different port")
        print(f"\nTo find what's using the port:")
        print(f"  lsof -i :{settings.PORT}")
        print(f"  # or")
        print(f"  sudo lsof -i :{settings.PORT}")
        sys.exit(1)
    
    # Only import and create app AFTER port check passes
    # This ensures expensive resources (HTTP clients, DB connections) are only
    # allocated when we're sure the server can start
    from api.server import create_app
    
    app = create_app()
    
    print(f"Starting server on http://{host}:{settings.PORT}")
    uvicorn.run(
        app,
        host=host,
        port=settings.PORT
    )

