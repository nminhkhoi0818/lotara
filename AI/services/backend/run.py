"""
Proper entry point for the backend server.

Usage:
    cd services/backend
    python run.py

Or from project root:
    python services/backend/run.py
"""

import sys
import os
from pathlib import Path

# Add the backend directory and project root to Python path
backend_dir = Path(__file__).parent.resolve()
services_dir = backend_dir.parent
project_root = services_dir.parent

# Add paths in correct order
sys.path.insert(0, str(backend_dir))  # For local imports (api, core)
sys.path.insert(0, str(project_root))  # For travel_lotara imports

print("=" * 60)
print("🚀 Travel Lotara AI Backend")
print("=" * 60)
print(f"Backend directory: {backend_dir}")
print(f"Project root: {project_root}")
print(f"Python path configured ✓")
print()

if __name__ == "__main__":
    import uvicorn
    
    # Import the app after path is set
    from main import app
    
    # Configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    print(f"Starting server on {host}:{port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print()
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
