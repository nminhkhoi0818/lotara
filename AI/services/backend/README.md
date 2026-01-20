# 🚀 Travel Lotara AI Backend

**Serverless FastAPI backend for autonomous multi-agent travel concierge**

---

## 📋 **Overview**

This is the **AI backend** for Travel Lotara, designed for **Vercel Serverless** deployment with **Supabase** as the database.

✅ Multi-agent workflow orchestration (Google ADK)  
✅ Serverless execution on Vercel  
✅ Supabase PostgreSQL database (free tier)  
✅ Proactive trip suggestions  
✅ Full Opik observability  

**Deployment:**
- 🚀 **Vercel** - Serverless Python functions
- 🗄️ **Supabase** - PostgreSQL database (free tier)
- 📊 **Opik** - Observability & tracing

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────┐
│              Next.js/TS Product Backend             │
│         (auth, billing, user management)            │
└────────────────────┬────────────────────────────────┘
                     │ HTTP
         ┌───────────▼─────────────┐
         │   FastAPI on Vercel     │
         │  (Serverless Functions) │
         ├─────────────────────────┤
         │  /v1/plan               │  ← Trip planning
         │  /v1/plan/sync          │  ← Sync planning (demo)
         │  /v1/suggest            │  ← Proactive suggestions
         │  /v1/status/{job_id}    │  ← Job status
         │  /v1/approve            │  ← HITL approval
         │  /v1/feedback           │  ← User feedback
         │  /v1/preferences        │  ← User preferences
         │  /health                │  ← Health check
         └────────────┬────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Supabase │   │  Google  │   │  Opik    │
│(Postgres)│   │   ADK    │   │ (Traces) │
└──────────┘   └──────────┘   └──────────┘
```

---

## 🚀 **Quick Start**

### **Option A: Deploy to Vercel (Recommended)**

```bash
cd AI/services/backend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Set environment variables in Vercel Dashboard:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

### **Option B: Local Development**

```bash
cd AI/services/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install uvicorn  # For local server

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run locally
python run_local.py
# Or: uvicorn api.app:app --reload --port 8000
```

### **Database Setup (Supabase)**

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Run the migration: `src/travel_lotara/database/migrations/001_initial_schema.sql`
4. Copy your API keys from Settings → API

---

## 📡 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check with DB status |
| `/docs` | GET | Swagger UI |
| `/v1/plan` | POST | Start trip planning |
| `/v1/plan/sync` | POST | Sync planning (demo) |
| `/v1/suggest` | POST | Proactive suggestions |
| `/v1/status/{job_id}` | GET | Check job status |
| `/v1/jobs/{user_id}` | GET | List user jobs |
| `/v1/approve` | POST | Approve recommendation |
| `/v1/feedback` | POST | Submit feedback |
| `/v1/preferences/{user_id}` | GET/PUT | User preferences |

### **Example: Plan a Trip**

**Request:**
```json
POST /v1/plan
{
  "user_id": "user123",
  "query": "Plan a 5-day trip to Tokyo for under $3000",
  "constraints": {
    "budget_usd": 3000,
    "duration_days": 5,
    "interests": ["food", "culture"],
    "departure_city": "LAX"
  }
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started"
}
```

**Usage:**
```javascript
// Next.js/TS Product Backend
const response = await fetch('http://ai-backend:8000/v1/plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: session.user.id,
    query: userInput,
    constraints: { budget_usd: 3000 }
  })
});

const { job_id } = await response.json();

// Connect to SSE stream
const eventSource = new EventSource(`http://ai-backend:8000/v1/stream/${job_id}`);
```

---

### **2. POST /v1/suggest** - Trigger Proactive Suggestion

System-triggered workflows when opportunities detected.

**Request:**
```json
{
  "user_id": "user123",
  "trigger_type": "price_drop",
  "context": {
    "route": "LAX->NRT",
    "old_price": 850,
    "new_price": 650,
    "savings": 200
  }
}
```

**When to call:**
- Price drop detected (product backend monitors Amadeus API)
- Calendar gap identified (product backend checks Google Calendar)
- Budget surplus found (product backend tracks spending)

---

### **3. GET /v1/status/{job_id}** - Poll Job Status

Check current job progress.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "executing",
  "mode": "reactive",
  "created_at": "2026-01-17T10:30:00Z",
  "updated_at": "2026-01-17T10:35:00Z",
  "progress": {
    "current_state": "execution",
    "tasks_total": 5,
    "tasks_completed": 3
  },
  "current_output": {
    "flights": [...],
    "hotels": [...]
  },
  "opik_trace_url": "https://app.opik.ai/traces/abc123"
}
```

**Polling frequency:** Every 2-5 seconds  
**Better alternative:** Use `/v1/stream` for real-time updates

---

### **4. GET /v1/stream/{job_id}** - Stream Events (SSE)

Real-time updates as workflow executes.

**Event Types:**
- `state_change` - Workflow state updated
- `task_start` - Agent started working
- `task_complete` - Agent finished
- `agent_output` - Partial results available
- `complete` - Job finished
- `error` - Something failed

**Frontend Usage:**
```javascript
const eventSource = new EventSource(`/v1/stream/${job_id}`);

eventSource.addEventListener('agent_output', (e) => {
  const { key, value } = JSON.parse(e.data);
  console.log(`Got ${key}:`, value);
  
  // Update UI with partial results
  if (key === 'flights') {
    setFlights(value);
  }
});

eventSource.addEventListener('complete', (e) => {
  const { result } = JSON.parse(e.data);
  console.log('Complete itinerary:', result);
  eventSource.close();
});

eventSource.addEventListener('error', (e) => {
  console.error('Stream error:', e);
  eventSource.close();
});
```

---

### **5. POST /v1/approve** - HITL Approval

Approve/reject critical actions.

**Request:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved": true,
  "notes": "Looks good, proceed with booking"
}
```

**When required:**
- Booking confirmation (charge money)
- Budget override (exceed limit)
- Legal acknowledgment (visa requirements)

---

### **6. POST /v1/feedback** - Submit Feedback

User feedback for evaluation.

**Request:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "rating": 5,
  "comment": "Perfect itinerary!",
  "helpful_aspects": ["budget_accuracy", "creative_suggestions"],
  "improvement_areas": ["flight_times"]
}
```

**Logged to Opik for:**
- LLM-as-judge evaluation
- A/B testing
- Performance dashboards

---

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | ✅ | `redis://localhost:6379` | Redis connection |
| `OPIK_API_KEY` | ✅ | - | Opik API key |
| `OPIK_PROJECT` | ❌ | `travel-lotara-prod` | Opik project name |
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key |
| `ENVIRONMENT` | ❌ | `development` | `development`, `staging`, `production` |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `CORS_ORIGINS` | ❌ | `http://localhost:3000` | Allowed origins (comma-separated) |
| `API_WORKERS` | ❌ | `4` | Uvicorn workers |

---

## 🐳 **Docker Deployment**

### **Development**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ai-backend

# Stop services
docker-compose down
```

### **Production**

```bash
# Build image
docker build -t lotara-ai-backend -f Dockerfile ../..

# Run container
docker run -d \
  -p 8000:8000 \
  -e REDIS_URL=redis://redis:6379 \
  -e OPIK_API_KEY=xxx \
  -e OPENAI_API_KEY=yyy \
  --name lotara-ai-backend \
  lotara-ai-backend
```

---

## 🧪 **Testing**

### **Unit Tests**

```bash
pytest tests/ -v
```

### **API Tests**

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test plan endpoint
curl -X POST http://localhost:8000/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "query": "Plan a trip to Tokyo",
    "constraints": {"budget_usd": 3000}
  }'
```

### **Load Testing**

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## 📊 **Monitoring**

### **Health Check**

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "redis": "healthy",
    "opik": "healthy"
  }
}
```

### **Opik Dashboard**

All workflows are traced to Opik:

1. Go to https://app.opik.ai
2. Select project `travel-lotara-prod`
3. View traces, metrics, feedback

---

## 🔒 **Security Notes**

### **What This Backend Does NOT Handle:**

- ❌ User authentication (product backend responsibility)
- ❌ API rate limiting (API gateway responsibility)
- ❌ Input sanitization beyond Pydantic validation

### **Recommendations for Production:**

1. **Deploy behind API gateway** (NGINX, Kong, AWS API Gateway)
2. **Add authentication middleware** in product backend
3. **Enable rate limiting** at gateway level
4. **Use HTTPS only** in production
5. **Rotate API keys** regularly
6. **Monitor Opik logs** for suspicious activity

---

## 🚦 **Integration with Product Backend**

### **Next.js/TS Example**

```typescript
// lib/ai-backend.ts
export class AIBackend {
  private baseUrl = process.env.AI_BACKEND_URL || 'http://localhost:8000';
  
  async planTrip(userId: string, query: string, constraints: any) {
    const response = await fetch(`${this.baseUrl}/v1/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, query, constraints })
    });
    
    const { job_id } = await response.json();
    return job_id;
  }
  
  streamResults(jobId: string): EventSource {
    return new EventSource(`${this.baseUrl}/v1/stream/${jobId}`);
  }
  
  async getStatus(jobId: string) {
    const response = await fetch(`${this.baseUrl}/v1/status/${jobId}`);
    return await response.json();
  }
}
```

---

## 📈 **Performance**

### **Expected Metrics**

- **Latency (p50):** <1s (job creation)
- **Latency (p95):** <3s (full workflow)
- **Throughput:** 100 jobs/sec
- **Concurrent jobs:** 1000+
- **Redis memory:** ~100MB per 1000 active jobs

### **Scaling**

```yaml
# docker-compose.yml
ai-backend:
  deploy:
    replicas: 4
    resources:
      limits:
        cpus: "2"
        memory: 4G
```

---

## 🐛 **Debugging**

### **View Logs**

```bash
# Docker
docker-compose logs -f ai-backend

# Local
tail -f logs/backend.log
```

### **Check Redis State**

```bash
redis-cli

# List all jobs
KEYS job:*

# Get job state
GET job:550e8400-e29b-41d4-a716-446655440000

# List events
KEYS events:*
```

### **Opik Traces**

Each job has an Opik trace URL in the status response:

```bash
curl http://localhost:8000/v1/status/{job_id} | jq .opik_trace_url
```

---

## 📚 **File Structure**

```
services/backend/
├── main.py                    # FastAPI app
├── requirements.txt           # Dependencies
├── Dockerfile                 # Production image
├── docker-compose.yml         # Local development
├── .env.example               # Environment template
├── README.md                  # This file
├── api/
│   ├── __init__.py
│   └── models.py              # Pydantic schemas
├── core/
│   ├── __init__.py
│   ├── job_manager.py         # Redis job management
│   └── workflow_executor.py  # MotherAgent wrapper
├── scheduler/
│   ├── __init__.py
│   └── proactive_scheduler.py # Background tasks
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_workflows.py
```

---

## ✅ **Production Checklist**

- [ ] Redis cluster configured
- [ ] Environment variables set
- [ ] Opik integration tested
- [ ] Health checks working
- [ ] Docker image built
- [ ] API gateway configured
- [ ] HTTPS enabled
- [ ] Monitoring alerts set
- [ ] Load testing completed
- [ ] Documentation reviewed

---

## 🎯 **Next Steps**

1. **Test locally:** `uvicorn main:app --reload`
2. **Integrate with product backend:** Update API URLs
3. **Deploy to staging:** Test with real users
4. **Monitor in Opik:** Track performance
5. **Optimize:** Based on metrics

---

## 📞 **Support**

- **Documentation:** [docs/](../../docs/)
- **Issues:** GitHub Issues
- **Opik Dashboard:** https://app.opik.ai

---

**🚀 Ready to serve 1000s of concurrent travel planning requests!**
