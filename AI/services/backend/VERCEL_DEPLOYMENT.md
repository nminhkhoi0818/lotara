# Vercel Deployment Guide

## Overview

This backend is configured for **Vercel Serverless Functions** using FastAPI.

**Key Points:**
- Vercel **natively supports ASGI** - no Mangum adapter needed
- Python 3.12 runtime (Vercel default)
- Just export an `app` variable from FastAPI
- Zero configuration required for basic deployment

## Quick Deploy

### 1. Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed (v48.1.8+)
- Supabase project created (free tier)
- Environment variables ready

### 2. Set Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |

### 3. Deploy

```bash
# Navigate to backend directory
cd AI/services/backend

# Login to Vercel
vercel login

# Deploy (first time - creates project)
vercel

# Deploy to production
vercel --prod
```

Or use Vercel CLI init:
```bash
vc init fastapi
vc deploy
```

## Project Structure

```
services/backend/
├── api/
│   ├── app.py            # Main FastAPI app (exports `app`)
│   ├── models.py         # Pydantic models
│   └── repositories.py   # Supabase data access
├── vercel.json           # Vercel configuration
├── pyproject.toml        # Python dependencies (preferred)
└── requirements.txt      # Alternative dependencies file
```

## API Endpoints

All endpoints are served from the Vercel serverless function:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |
| `/v1/plan` | POST | Plan a trip |
| `/v1/suggest` | POST | Get suggestions |
| `/v1/status/{job_id}` | GET | Check job status |
| `/v1/jobs/{user_id}` | GET | List user jobs |
| `/v1/approve` | POST | Approve recommendation |
| `/v1/feedback` | POST | Submit feedback |
| `/v1/preferences/{user_id}` | GET/PUT | User preferences |

## Configuration

### vercel.json

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "functions": {
    "api/**/*.py": {
      "maxDuration": 60,
      "memory": 1024,
      "excludeFiles": "{tests/**,__pycache__/**,*.pyc}"
    }
  },
  "rewrites": [
    { "source": "/v1/:path*", "destination": "/api/app" },
    { "source": "/health", "destination": "/api/app" }
  ]
}
```

### pyproject.toml (Preferred)

```toml
[project]
name = "lotara-ai-backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.117.1",
    "supabase>=2.0.0",
    "pydantic>=2.6.0",
]

[project.scripts]
app = "api.app:app"
```

### Function Limits

| Plan | Max Duration | Memory |
|------|-------------|--------|
| Hobby (Free) | 10 seconds | 1024 MB |
| Pro | 60 seconds | 1024 MB |
| Enterprise | 900 seconds | 3008 MB |

## Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run with Vercel CLI (recommended)
vercel dev

# Or use uvicorn (requires: pip install uvicorn)
uvicorn api.app:app --reload --port 8000
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Use relative imports: `from .models import ...`
   - Check `__init__.py` exists in api folder

2. **Timeout Errors (Free Tier)**
   - Hobby plan has 10s limit
   - Optimize database queries
   - Use lazy loading for clients

3. **Cold Starts**
   - First request may be slow (~1-2s)
   - Supabase client is lazy-loaded
   - Keep dependencies minimal

4. **Bundle Size (250MB limit)**
   - Use `excludeFiles` in vercel.json
   - Remove unused dependencies
   - No `__pycache__` or `.pyc` files

### Logs

View function logs:
1. Vercel Dashboard → Project → Deployments
2. Click deployment → Functions tab
3. View real-time logs

## Database Setup (Supabase)

Run migrations in Supabase SQL Editor:

1. Go to Supabase Dashboard → SQL Editor
2. Run the migration SQL files from `migrations/`
3. Verify tables in Table Editor

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Client    │────▶│  Vercel Edge    │────▶│  Serverless │
│  (Browser)  │     │   (Global CDN)  │     │  Function   │
└─────────────┘     └─────────────────┘     └──────┬──────┘
                                                    │
                                                    ▼
                                           ┌─────────────┐
                                           │  Supabase   │
                                           │ (PostgreSQL)│
                                           └─────────────┘
```

## Important Notes

- **No Mangum needed** - Vercel natively supports ASGI/FastAPI
- **No uvicorn needed** - Vercel handles the server
- Docker/Dockerfile are **NOT** used for Vercel deployment
- The entry point is `api/app.py` following Vercel conventions
- Environment variables are set in Vercel Dashboard, not in vercel.json
