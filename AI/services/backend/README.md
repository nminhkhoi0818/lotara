# Lotara Travel Agent - FastAPI Backend

FastAPI backend for deploying the Lotara AI travel agent system.

## Features

- **AI-Powered Itinerary Generation**: Multi-agent system using Google ADK
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Observability**: Integrated Opik tracing
- **Error Handling**: Automatic retry logic for 503/429 errors
- **CORS Support**: Configurable cross-origin requests

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../../.env.example ../../.env
# Edit .env with your API keys

# Run the server
python run.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Using UV (Recommended)

```bash
# From AI directory
cd ../..
uv run python services/backend/run.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Generate Itinerary
```bash
POST /api/itinerary/generate

# Example request:
curl -X POST http://localhost:8000/api/itinerary/generate \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "duration": "medium",
    "companions": "solo",
    "budget": "midrange",
    "pace": "balanced",
    "travelStyle": "cultural",
    "activity": "medium",
    "crowds": "mixed",
    "accommodation": "standard",
    "remote": false,
    "timing": "flexible"
  }'
```

## Environment Variables

Required variables (from `../../.env`):

```bash
# AI Model
LOTARA_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your-google-api-key

# Opik Tracking
OPIK_API_KEY=your-opik-key
OPIK_PROJECT=Lotara

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: Database
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
```

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

### Render

1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r services/backend/requirements.txt`
4. Set start command: `python services/backend/run.py`
5. Add environment variables

### Docker

```bash
# Build (from AI directory)
docker build -t lotara-api -f services/backend/Dockerfile .

# Run
docker run -p 8000:8000 --env-file .env lotara-api
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test itinerary generation
curl -X POST http://localhost:8000/api/itinerary/generate \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user",
    "duration": "short",
    "companions": "solo",
    "budget": "budget",
    "pace": "balanced",
    "travelStyle": "cultural",
    "activity": "medium",
    "crowds": "mixed",
    "accommodation": "standard",
    "remote": false,
    "timing": "flexible"
  }'
```

## Performance Notes

- Itinerary generation typically takes 30-120 seconds
- Uses retry logic for 503/429 errors (5 attempts with exponential backoff)
- Recommended deployment: Railway or Render (not Vercel serverless)
- For high load: increase `API_WORKERS` in .env

## Troubleshooting

**503 Service Unavailable**:
- Google Gemini API is overloaded
- Try switching model in .env: `LOTARA_MODEL=gemini-1.5-flash`
- Wait 2-5 minutes and retry

**429 Rate Limit**:
- Check API quota at https://aistudio.google.com/
- Implement request queueing if needed

**Import Errors**:
- Ensure you're running from correct directory
- Check PYTHONPATH includes parent directories

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
