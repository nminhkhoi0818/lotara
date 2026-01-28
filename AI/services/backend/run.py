"""Entry point for running the FastAPI application."""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = backend_dir.parent.parent / ".env"
    load_dotenv(env_path)
    print(f"[INIT] Loaded environment from: {env_path}")
except ImportError:
    print("[INIT] python-dotenv not installed, using system environment")


def main():
    """Run the FastAPI application with uvicorn."""
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"[INIT] Starting Lotara Travel Agent API")
    print(f"[INIT] Host: {host}:{port}")
    print(f"[INIT] Workers: {workers}")
    print(f"[INIT] Reload: {reload}")
    print(f"[INIT] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INIT] Model: {os.getenv('LOTARA_MODEL', 'gemini-2.5-flash')}")
    
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,  # Single worker for reload mode
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

    # To run the app, use the command:
    # uv run services/backend/run.py
