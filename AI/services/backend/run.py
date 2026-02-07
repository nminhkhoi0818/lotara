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


def main_run_app():
    """Run the FastAPI application with uvicorn."""
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # IMPORTANT: Use 1 worker for in-memory cache to work properly
    # For production with multiple workers, use Redis for caching
    workers = 1  # Force single worker for cache consistency
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    if os.getenv("API_WORKERS"):
        print(f"[WARNING] API_WORKERS env var ignored. Using workers=1 for cache consistency.")
        print(f"[INFO] For multi-worker setup, implement Redis cache sharing.")
    
    print(f"[INIT] Starting Lotara Travel Agent API")
    print(f"[INIT] Host: {host}:{port}")
    print(f"[INIT] Workers: {workers}")
    print(f"[INIT] Reload: {reload}")
    print(f"[INIT] Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"[INIT] Model: {os.getenv('LOTARA_MODEL', 'gemini-2.5-flash')}")
    
    # Configure reload directories to avoid scanning non-existent paths
    reload_dirs = None
    if reload:
        project_root = backend_dir.parent.parent
        reload_dirs = [
            str(project_root / "services" / "backend"),
            str(project_root / "src"),
        ]
        # Only add existing directories
        reload_dirs = [d for d in reload_dirs if Path(d).exists()]
        print(f"[INIT] Watching directories: {reload_dirs}")
    
    uvicorn.run(
        "services.backend.api.app:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,  # Single worker for reload mode
        reload=reload,
        reload_dirs=reload_dirs,
        log_level="info"
    )


if __name__ == "__main__":
    main_run_app()

    # To run the app, use the command:
    # uv run services/backend/run.py
