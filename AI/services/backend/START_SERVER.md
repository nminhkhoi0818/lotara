# Backend Quick Start

## Option 1: Using run.py (Recommended)

```bash
# From services/backend directory
cd services/backend
python run.py
```

## Option 2: Using uvicorn directly

```bash
# From services/backend directory
cd services/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** Option 2 requires the Python path to be set up correctly. If you get import errors, use Option 1.

## Option 3: From project root

```bash
# From AI directory (project root)
cd AI
python services/backend/run.py
```

## Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# View API docs
# Open browser: http://localhost:8000/docs
```

## Test API

```bash
# Start a planning job
curl -X POST http://localhost:8000/v1/plan \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "query": "Plan Tokyo trip for $3000", "constraints": {}}'

# Check job status (replace {job_id} with actual ID)
curl http://localhost:8000/v1/status/{job_id}
```

## Troubleshooting

### Import Errors
If you see `ImportError: attempted relative import with no known parent package`:
- Use `python run.py` instead of `uvicorn main:app` directly
- OR ensure you're in the `services/backend` directory

### Redis Connection Errors
```bash
# Start Redis with Docker
docker run -d --name lotara-redis -p 6379:6379 redis:7-alpine

# Verify Redis is running
redis-cli ping
```

### Port Already in Use
```bash
# Kill existing process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```
