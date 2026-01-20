"""
Local development server for Travel Lotara API.

Run this to test locally without Vercel:
    pip install uvicorn
    python run_local.py

Then visit:
    http://localhost:8000/docs - Swagger UI
    http://localhost:8000/health - Health check
"""

import os
import sys

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set development environment
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")

if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Install it with:")
        print("  pip install uvicorn")
        sys.exit(1)
    
    print("=" * 60)
    print("Travel Lotara AI Backend - Local Development Server")
    print("=" * 60)
    print()
    print("Starting server...")
    print()
    print("Endpoints:")
    print("  - API Docs:    http://localhost:8000/docs")
    print("  - Health:      http://localhost:8000/health")
    print("  - Plan Trip:   POST http://localhost:8000/v1/plan")
    print("  - Plan (Sync): POST http://localhost:8000/v1/plan/sync")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Import the app
    from api.app import app
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
