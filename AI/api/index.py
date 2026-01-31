"""
Vercel serverless entry point for FastAPI application
"""
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services/backend')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mangum import Mangum
from services.backend.api.app import app

# Mangum handler for Vercel serverless
handler = Mangum(app, lifespan="off")
