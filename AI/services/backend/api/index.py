"""
Vercel serverless entry point for FastAPI application
"""
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))

from mangum import Mangum
from services.backend.api.app import app

# Mangum handler for Vercel serverless
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
