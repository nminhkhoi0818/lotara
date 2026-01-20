# 🎯 AI Backend Integration Guide

**How to integrate Travel Lotara AI Backend with your Next.js/TypeScript product backend**

---

## 📋 **Architecture Overview**

```
┌─────────────────────────────────────────────────────┐
│             USER'S BROWSER                          │
│         (React/Next.js Frontend)                    │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────┐
│     Next.js/TS Product Backend (Port 3000)          │
│     ─────────────────────────────────────────       │
│     • User authentication (NextAuth.js)             │
│     • Billing/payments (Stripe)                     │
│     • Database (Prisma/PostgreSQL)                  │
│     • User preferences & history                    │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP/SSE (Internal)
                 ▼
┌─────────────────────────────────────────────────────┐
│     Python AI Backend (Port 8000)                   │
│     ───────────────────────────────                 │
│     • Multi-agent orchestration                     │
│     • Travel planning workflows                     │
│     • Opik observability                            │
│     • Redis job management                          │
└─────────────────────────────────────────────────────┘
```

---

## 🔌 **Integration Points**

### **1. Next.js API Routes → Python AI Backend**

The product backend calls the AI backend's HTTP APIs.

**File:** `app/api/travel/plan/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  // 1. Authenticate user (product backend responsibility)
  const session = await getServerSession();
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  // 2. Parse request
  const { query, constraints } = await req.json();
  
  // 3. Call AI Backend
  const response = await fetch(`${AI_BACKEND_URL}/v1/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: session.user.id,
      query,
      constraints
    })
  });
  
  const { job_id, status } = await response.json();
  
  // 4. Save job to database (for user's trip history)
  await prisma.tripPlanningJob.create({
    data: {
      id: job_id,
      userId: session.user.id,
      query,
      status,
      createdAt: new Date()
    }
  });
  
  // 5. Return job ID to frontend
  return NextResponse.json({ job_id, status });
}
```

---

### **2. Frontend → SSE Streaming**

The frontend connects directly to AI backend for real-time updates.

**File:** `components/TripPlanning.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';

interface TripPlanningProps {
  jobId: string;
}

export function TripPlanning({ jobId }: TripPlanningProps) {
  const [status, setStatus] = useState<string>('started');
  const [flights, setFlights] = useState<any[]>([]);
  const [hotels, setHotels] = useState<any[]>([]);
  const [itinerary, setItinerary] = useState<any>(null);
  
  useEffect(() => {
    const AI_BACKEND_URL = process.env.NEXT_PUBLIC_AI_BACKEND_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${AI_BACKEND_URL}/v1/stream/${jobId}`);
    
    eventSource.addEventListener('state_change', (e) => {
      const { status } = JSON.parse(e.data);
      setStatus(status);
      console.log('Workflow state:', status);
    });
    
    eventSource.addEventListener('agent_output', (e) => {
      const { key, value } = JSON.parse(e.data);
      
      if (key === 'flights') {
        setFlights(value);
      } else if (key === 'hotels') {
        setHotels(value);
      }
    });
    
    eventSource.addEventListener('complete', (e) => {
      const { result } = JSON.parse(e.data);
      setItinerary(result);
      setStatus('completed');
      eventSource.close();
    });
    
    eventSource.addEventListener('error', (e) => {
      console.error('Stream error:', e);
      eventSource.close();
    });
    
    return () => {
      eventSource.close();
    };
  }, [jobId]);
  
  return (
    <div>
      <h2>Planning Your Trip</h2>
      <p>Status: {status}</p>
      
      {flights.length > 0 && (
        <div>
          <h3>Flights Found</h3>
          {flights.map((flight, i) => (
            <FlightCard key={i} flight={flight} />
          ))}
        </div>
      )}
      
      {hotels.length > 0 && (
        <div>
          <h3>Hotels Found</h3>
          {hotels.map((hotel, i) => (
            <HotelCard key={i} hotel={hotel} />
          ))}
        </div>
      )}
      
      {itinerary && (
        <div>
          <h3>Complete Itinerary</h3>
          <ItineraryView itinerary={itinerary} />
        </div>
      )}
    </div>
  );
}
```

---

### **3. Proactive Suggestions (System-Triggered)**

Product backend monitors external events and triggers AI suggestions.

**File:** `lib/price-monitor.ts`

```typescript
import { prisma } from '@/lib/prisma';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://localhost:8000';

/**
 * Background job (runs via cron or queue)
 * Monitors flight prices for users' watchlists
 */
export async function checkPriceDrops() {
  // 1. Get all users with price alerts
  const watchlists = await prisma.priceWatchlist.findMany({
    include: { user: true }
  });
  
  for (const watchlist of watchlists) {
    // 2. Check current price (via Amadeus API)
    const currentPrice = await checkFlightPrice(
      watchlist.origin,
      watchlist.destination,
      watchlist.departureDate
    );
    
    // 3. If price dropped >15%
    if (currentPrice < watchlist.lastPrice * 0.85) {
      const savings = watchlist.lastPrice - currentPrice;
      
      // 4. Trigger AI backend suggestion
      await fetch(`${AI_BACKEND_URL}/v1/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: watchlist.userId,
          trigger_type: 'price_drop',
          context: {
            route: `${watchlist.origin}->${watchlist.destination}`,
            old_price: watchlist.lastPrice,
            new_price: currentPrice,
            savings,
            departure_date: watchlist.departureDate
          }
        })
      });
      
      // 5. Send notification to user
      await sendPushNotification(watchlist.userId, {
        title: 'Price Drop Alert!',
        body: `Save $${savings} on ${watchlist.origin}→${watchlist.destination}`,
        action: `/trips/suggestions/${watchlist.id}`
      });
      
      // 6. Update last price
      await prisma.priceWatchlist.update({
        where: { id: watchlist.id },
        data: { lastPrice: currentPrice }
      });
    }
  }
}
```

---

### **4. Human-in-the-Loop Approval**

Product backend shows approval UI and sends decision to AI backend.

**File:** `app/api/travel/approve/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const session = await getServerSession();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { job_id, approved, notes } = await req.json();
  
  // 1. Verify job belongs to user
  const job = await prisma.tripPlanningJob.findUnique({
    where: { id: job_id }
  });
  
  if (job.userId !== session.user.id) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }
  
  // 2. Send approval to AI backend
  const response = await fetch(`${AI_BACKEND_URL}/v1/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id, approved, notes })
  });
  
  // 3. Update database
  await prisma.tripPlanningJob.update({
    where: { id: job_id },
    data: {
      approved,
      approvalNotes: notes,
      approvedAt: new Date()
    }
  });
  
  return NextResponse.json({ success: true });
}
```

---

### **5. User Feedback Collection**

Product backend collects feedback and sends to AI backend for Opik logging.

**File:** `app/api/travel/feedback/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';

const AI_BACKEND_URL = process.env.AI_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const session = await getServerSession();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { job_id, rating, comment, helpful_aspects, improvement_areas } = await req.json();
  
  // 1. Save feedback to database
  await prisma.tripFeedback.create({
    data: {
      jobId: job_id,
      userId: session.user.id,
      rating,
      comment,
      helpfulAspects: helpful_aspects,
      improvementAreas: improvement_areas
    }
  });
  
  // 2. Send to AI backend (for Opik logging)
  await fetch(`${AI_BACKEND_URL}/v1/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_id,
      rating,
      comment,
      helpful_aspects,
      improvement_areas
    })
  });
  
  return NextResponse.json({ success: true });
}
```

---

## 🔐 **Security Considerations**

### **1. Internal Network Communication**

```yaml
# docker-compose.yml
services:
  next-backend:
    networks:
      - internal
    environment:
      - AI_BACKEND_URL=http://ai-backend:8000  # Internal hostname
  
  ai-backend:
    networks:
      - internal
    # Not exposed to public internet
```

### **2. API Key Authentication (Optional)**

If you want to secure AI backend:

```typescript
// Product backend
const response = await fetch(`${AI_BACKEND_URL}/v1/plan`, {
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.AI_BACKEND_API_KEY  // Shared secret
  },
  body: JSON.stringify(...)
});
```

```python
# AI backend (main.py)
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/v1/plan", dependencies=[Depends(verify_api_key)])
async def plan_trip(...):
    ...
```

---

## 📊 **Monitoring & Observability**

### **Product Backend Tracking**

```typescript
// Log job creation
await prisma.tripPlanningJob.create({
  data: {
    id: job_id,
    userId: session.user.id,
    query,
    status: 'started',
    createdAt: new Date()
  }
});

// Update status periodically
const interval = setInterval(async () => {
  const response = await fetch(`${AI_BACKEND_URL}/v1/status/${job_id}`);
  const { status } = await response.json();
  
  await prisma.tripPlanningJob.update({
    where: { id: job_id },
    data: { status }
  });
  
  if (status === 'completed' || status === 'failed') {
    clearInterval(interval);
  }
}, 5000);
```

### **Opik Dashboard Access**

Provide Opik trace URLs to users for debugging:

```typescript
// In job status API
const aiBackendStatus = await fetch(`${AI_BACKEND_URL}/v1/status/${job_id}`);
const { opik_trace_url } = await aiBackendStatus.json();

return NextResponse.json({
  job_id,
  status,
  debug_url: opik_trace_url  // Show to admins/power users
});
```

---

## 🚀 **Deployment**

### **Development**

```bash
# Terminal 1: Start AI backend
cd AI/services/backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start product backend
cd ../../..  # Back to root
npm run dev
```

### **Production (Docker)**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  next-backend:
    build: ./
    ports:
      - "3000:3000"
    environment:
      - AI_BACKEND_URL=http://ai-backend:8000
    networks:
      - lotara-network
  
  ai-backend:
    build: ./AI/services/backend
    environment:
      - REDIS_URL=redis://redis:6379
      - OPIK_API_KEY=${OPIK_API_KEY}
    networks:
      - lotara-network
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    networks:
      - lotara-network

networks:
  lotara-network:
```

---

## ✅ **Integration Checklist**

- [ ] AI backend URL configured (`AI_BACKEND_URL`)
- [ ] `/api/travel/plan` route created
- [ ] SSE streaming component implemented
- [ ] Proactive scheduler configured
- [ ] Approval workflow integrated
- [ ] Feedback collection working
- [ ] Database schema includes trip jobs
- [ ] Error handling for AI backend failures
- [ ] Monitoring/logging integrated
- [ ] Tested with real users

---

## 🎯 **Example User Flow**

1. **User:** "Plan a trip to Tokyo"
2. **Frontend:** Calls `/api/travel/plan` (product backend)
3. **Product Backend:** 
   - Authenticates user
   - Calls AI backend `/v1/plan`
   - Saves job to database
   - Returns job_id to frontend
4. **Frontend:** Connects to AI backend `/v1/stream/{job_id}`
5. **AI Backend:** 
   - Executes multi-agent workflow
   - Streams partial results (flights, hotels)
   - Logs to Opik
6. **Frontend:** Updates UI in real-time
7. **AI Backend:** Requests approval for $2500 booking
8. **Frontend:** Shows approval modal
9. **User:** Approves
10. **Product Backend:** Calls `/v1/approve`
11. **AI Backend:** Completes workflow
12. **Frontend:** Shows complete itinerary
13. **User:** Rates 5 stars
14. **Product Backend:** Calls `/v1/feedback`
15. **AI Backend:** Logs to Opik for evaluation

---

**🎉 You're ready to integrate! Start with `/api/travel/plan` and build from there.**
