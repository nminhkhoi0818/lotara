# Lotara - AI-Powered Personalized Vietnam Travel Planning

![Lotara](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-Proprietary-blue) ![Deploy](https://img.shields.io/badge/Deployed-Vercel-success)

> **Your Perfect Vietnam Trip, Designed for You** — Stop settling for generic recommendations. Lotara uses AI and personality-based matching to craft the perfect itinerary tailored to your unique travel style.

**Live Demo:** [https://lotara.vercel.app](https://lotara.vercel.app)

---

## 📖 Table of Contents
- [What is Lotara?](#-what-is-lotara)
- [What Problem Does It Solve?](#-what-problem-does-it-solve)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)

---

## 🎯 What is Lotara?

**Lotara is an AI-powered travel planning platform that creates truly personalized Vietnam itineraries based on your personality, not just your preferences.**

Unlike traditional travel platforms that simply filter destinations by price or category, Lotara understands *who you are as a traveler*. Through an interactive 5-minute chat-based questionnaire, Lotara maps your travel personality across multiple dimensions (adventure vs. comfort, crowds vs. solitude, nature vs. culture, etc.) and matches you with destinations that align with your unique "vibe."

---

## 🔍 What Problem Does It Solve?

### The Problem: One-Size-Fits-All Travel Recommendations

Traditional travel planning suffers from several issues:

1. **Generic Recommendations** — Most travel sites recommend the same popular destinations to everyone, regardless of personality or travel style
2. **Personality Mismatch** — A bustling city hotel might be perfect for extroverts but exhausting for introverts. Standard filters can't capture this.
3. **Decision Fatigue** — Too many choices without personalized guidance leads to analysis paralysis

### The Solution: Personality-Driven Matching

Lotara solves these problems by:

- **Understanding Your Travel DNA** — Maps your personality to a multi-dimensional "vibe profile"
- **Smart Matching Algorithm** — Each destination has its own vibe profile; Lotara calculates compatibility scores
- **Explainable AI** — Every recommendation comes with a clear explanation of *why* it matches your personality

---

## 🏗 System Architecture

Lotara uses a **three-tier architecture** that separates concerns and enables scalability:

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE["Next.js Application<br/>• Onboarding & Quiz<br/>• Results & Saved Trips<br/>• Chat Interface"]
    end
    
    subgraph "Backend Layer"
        BE["NestJS API Server<br/>• User Management<br/>• Questions & Places<br/>• Recommendations Engine<br/>• PostgreSQL Database"]
    end
    
    subgraph "AI Service Layer (Python)"
        AI[FastAPI Server<br/>Google ADK]
        AI_Root["Root Agent<br/>Main Orchestrator"]
        AI_Sub["Sub-Agents"]
        AI_Sub_Itinerary["Itinerary Agent<br/>• Trip Planning<br/>• Activity Scheduling<br/>• Day-by-Day Planning"]
        AI_Sub_Hotel["Hotel Agent<br/>• Budget Matching<br/>• Preference Alignment<br/>• Location Optimization"]
        AI_Sub_Activity["Activity Agent<br/>• Interest Matching<br/>• Workcation Support<br/>• Time Allocation"]
        AI_Tools["Tools & Utilities<br/>• Web Search<br/>• Data Parsing<br/>• Validation Tools<br/>• Format Conversion"]
        AI_Guards["Guardrails<br/>• Safety Checks<br/>• Budget Validation<br/>• Itinerary Rules<br/>• Output Validation"]
        AI_Config["Configuration<br/>• Prompts<br/>• Agent Profiles<br/>• Model Settings"]
        AI_VDB[(Milvus Vector DB<br/>Semantic Search<br/>Embeddings)]
        AI_Trace["Opik Tracing<br/>• Performance Monitoring<br/>• Agent Tracking<br/>• Error Logging"]
        
        AI --> AI_Root
        AI_Root --> AI_Sub
        AI_Sub --> AI_Sub_Itinerary
        AI_Sub --> AI_Sub_Hotel
        AI_Sub --> AI_Sub_Activity
        AI_Sub_Itinerary --> AI_Tools
        AI_Sub_Hotel --> AI_Tools
        AI_Sub_Activity --> AI_Tools
        AI_Sub_Itinerary --> AI_Guards
        AI_Sub_Hotel --> AI_Guards
        AI_Sub_Activity --> AI_Guards
        AI_Root --> AI_Config
        AI --> AI_VDB
        AI --> AI_Trace
    end
    
    subgraph "External Services"
        Google["Google Generative AI<br/>• Gemini Models<br/>• Embeddings API<br/>• Text Generation"]
        Vercel["Vercel Platform<br/>• Frontend Hosting<br/>• AI Service Hosting<br/>• Serverless Functions"]
        Supabase["Supabase<br/>• Authentication<br/>• User Storage<br/>• Real-time DB"]
        OpenTel["OpenTelemetry<br/>• Distributed Tracing<br/>• Metrics Collection<br/>• Performance Data"]
    end
    
    FE -->|REST API Calls| BE
    BE -->|AI Generation Request| AI
    AI_Root -->|LLM Calls| Google
    AI -->|Vector Search & Store| AI_VDB
    AI_VDB -->|Embeddings| Google
    BE -->|Auth & Storage| Supabase
    AI_Trace -->|Telemetry Data| OpenTel
    
    FE -.->|Deployed on| Vercel
    AI -.->|Deployed on| Vercel
    
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#e0234e,stroke:#333,stroke-width:2px,color:#fff
    classDef ai fill:#4285f4,stroke:#333,stroke-width:2px,color:#fff
    classDef aiComponent fill:#7cb9ff,stroke:#333,stroke-width:2px,color:#000
    classDef database fill:#336791,stroke:#333,stroke-width:2px,color:#fff
    classDef external fill:#10b981,stroke:#333,stroke-width:2px,color:#fff
    
    class FE frontend
    class BE backend
    class AI ai
    class AI_Root,AI_Sub,AI_Sub_Itinerary,AI_Sub_Hotel,AI_Sub_Activity,AI_Tools,AI_Guards,AI_Config,AI_Trace aiComponent
    class AI_VDB database
    class Google,Vercel,Supabase,OpenTel external
```

### **Architecture Flow**

1. **User Interaction (Frontend)**
   - User answers personality questionnaire via chat interface
   - Frontend sends responses to Backend API

2. **Personality Processing (Backend)**
   - **Vibe Mapping Service** converts answers into multi-dimensional personality scores
   - Stores user profile with vibe vector (e.g., `{lowkey: 7, nature: 9, crowds: 3, social: 5}`)

3. **Recommendation Generation (Backend + AI)**
   - **Match Scoring Engine** compares user's vibe vector against destination vibe vectors
   - Calculates compatibility scores using formula: `score = 100 - avg(|user_vibe - place_vibe|) * 10`
   - Ranks destinations by match quality
   - For detailed itineraries, calls **AI Service Layer**

4. **AI Agents (AI Service)**
   - **Mother Agent** orchestrates workflow through 7 states
   - Specialized agents handle specific tasks (flights, hotels, activities, budget, visa)
   - **Guardrails** ensure outputs are safe, accurate, and budget-compliant
   - **Opik** traces all actions for observability

5. **Results Delivery (Frontend)**
   - User sees top-matched destinations with explanations
   - Detailed itineraries with hotels, activities, and schedules
   - Can save trips for future reference

---

## 🚀 Getting Started

### **Prerequisites**

- **Node.js** 18 or higher ([Download](https://nodejs.org/))
- **npm** or **yarn** (comes with Node.js)
- **Git** for version control ([Download](https://git-scm.com/))
- **Python** 3.10+ (for AI service development)

### **Installation**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lotara
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   npm install
   ```

3. **Install frontend dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Install AI service dependencies (optional):**
   ```bash
   cd ../AI
   pip install -e .
   # or
   pip install -r requirements.txt
   ```

### **Running the Application Locally**

#### **1. Start the Backend API**

```bash
cd backend

# Development mode with hot reload
npm run start:dev

# Production build
npm run build
npm run start:prod
```

The API will be available at **http://localhost:3000**

**Test the API:**
```bash
# Get all destinations
curl http://localhost:3000/places

# Create a test user
curl -X POST http://localhost:3000/users/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "budget": "medium",
    "travelStyle": "solo",
    "answers": {
      "quiet_or_lively": "quiet",
      "nature_or_city": "nature",
      "crowd_tolerance": 5
    }
  }'
```

#### **2. Start the Frontend**

```bash
cd frontend

# Development mode with Turbopack for fast refresh
npm run dev

# Production build
npm run build
npm start
```

The frontend will be available at **http://localhost:3001** (or 3000 if backend is on a different port)

Open [http://localhost:3001](http://localhost:3001) in your browser to see the app.

#### **3. Run the AI Service (Optional)**

```bash
cd AI

# Set up environment variables
export OPIK_API_KEY="your_opik_key"  # Get from comet.com

# Run a test query
python -m travel_lotara.main reactive "Plan a 7-day trip to Tokyo for $3000"

# Or run the demo
python demo.py
```

### **Environment Variables**

Create `.env.local` files in both `frontend/` and `backend/` directories:

**Backend `.env`:**
```env
PORT=3000
DATABASE_URL=postgresql://user:password@localhost:5432/lotara  # Optional
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:3000
```

**AI Service `.env`:**
```env
OPIK_API_KEY=your_opik_api_key
OPENAI_API_KEY=your_openai_key  # If using OpenAI models
```

---

## � Available Scripts & Commands

### **Backend Commands**
```bash
npm run start         # Start production server
npm run start:dev     # Development mode with hot reload
npm run build         # Build for production
npm test              # Run all tests
npm run test:watch    # Watch mode for testing
npm run test:cov      # Generate coverage report
npm run test:e2e      # Run E2E integration tests
npm run lint          # Lint and auto-fix code
npm run format        # Format code with Prettier
```

### **Frontend Commands**
```bash
npm run dev           # Development server with Turbopack
npm run build         # Production build
npm start             # Start production server
npm run lint          # Run ESLint
```

### **AI Service Commands**
```bash
python -m travel_lotara.main reactive "query"  # Run reactive query
python demo.py                                  # Run interactive demo
pytest                                          # Run tests
```

## 📦 Deployment

### **Production Deployment**

#### **Frontend (Vercel)**
- **Platform:** Vercel
- **Branch:** main
- **Live URL:** [https://lotara.vercel.app](https://lotara.vercel.app)
- **Auto-deploy:** Enabled on push to main

**Deploy Your Own:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel
```

#### **Backend (Multiple Options)**

**Option 1: Vercel**
```bash
cd backend
vercel
```

**Option 2: Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Option 3: Render / Fly.io / Digital Ocean**
- Follow platform-specific deployment guides
- Ensure Node.js 18+ runtime
- Set environment variables

#### **AI Service (Vercel Serverless)**
Already deployed as part of the main Vercel deployment via `/AI/api/index.py` endpoint.

**Alternative: Standalone FastAPI**
```bash
cd AI/services/backend
pip install -r requirements.txt
uvicorn run:app --host 0.0.0.0 --port 8000
```

---

## 📖 Documentation & Resources

### **Internal Documentation**
- [Backend API Documentation](backend/API_DOCUMENTATION.md) — Complete API reference
- [Frontend README](frontend/README.md) — Frontend setup and development
- [Backend README](backend/README.md) — Backend architecture details
- [AI Service README](AI/README.md) — Multi-agent system documentation
- [Recommendations Module](backend/src/recommendations/README.md) — Matching algorithm deep dive
- [Users Module](backend/src/users/README.md) — Onboarding flow documentation

### **Key Concepts**
- **Vibe Mapping** — How user personality is quantified
- **Match Scoring** — The compatibility algorithm explained
- **Multi-Agent System** — How 5 AI agents collaborate
- **Explainable AI** — Making recommendations transparent

### **Learning Resources**
- [NestJS Documentation](https://docs.nestjs.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Opik for Observability](https://www.comet.com/docs/opik)
- [TypeORM](https://typeorm.io/) (for database integration)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Development Workflow**

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/lotara.git
   cd lotara
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-amazing-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Write tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend
   cd backend
   npm test
   npm run lint
   
   # Frontend
   cd frontend
   npm run lint
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new personality dimension for adventure sports"
   ```

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-amazing-feature
   ```

### **Code Style Guidelines**
- **TypeScript:** Use strict type checking, avoid `any`
- **Python:** Follow PEP 8, use type hints
- **Naming:** Use descriptive variable and function names
- **Comments:** Explain *why*, not *what* (code should be self-documenting)
- **Tests:** Aim for >80% coverage on new code

### **Areas for Contribution**
- 🐛 Bug fixes and issue resolution
- ✨ New travel destinations and vibe data
- 🎨 UI/UX improvements
- 📝 Documentation enhancements
- 🧪 Additional test coverage
- 🌍 Internationalization (i18n)
- ♿ Accessibility improvements

---

## 🏆 Credits & Acknowledgments

**Built by the Lotara Team**

**Powered by:**
- [NestJS](https://nestjs.com/) — Backend framework
- [Next.js](https://nextjs.org/) — Frontend framework
- [Opik](https://www.comet.com/docs/opik) — AI observability
- [Vercel](https://vercel.com/) — Deployment platform
- [Radix UI](https://www.radix-ui.com/) — Accessible components
- [Tailwind CSS](https://tailwindcss.com/) — Styling framework

**Special Thanks:**
- All contributors and early users
- Open-source community for amazing tools

---

<div align="center">

**Made with ❤️ for travelers who want personalized adventures**

⭐ **Star this repo if you find it helpful!** ⭐

[Website](https://lotara.vercel.app) • [Demo](https://lotara.vercel.app) • [Docs](backend/API_DOCUMENTATION.md)

</div>
