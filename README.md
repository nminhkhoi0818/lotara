# Lotara - AI-Powered Personalized Vietnam Travel Planning

![Lotara](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-Proprietary-blue) ![Deploy](https://img.shields.io/badge/Deployed-Vercel-success)

> **Your Perfect Vietnam Trip, Designed for You** — Stop settling for generic recommendations. Lotara uses AI and personality-based matching to craft the perfect itinerary tailored to your unique travel style.

**Live Demo:** [https://lotara.vercel.app](https://lotara.vercel.app)

---

## 📖 Table of Contents
- [What is Lotara?](#-what-is-lotara)
- [What Problem Does It Solve?](#-what-problem-does-it-solve)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)

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

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                        │
│                     (Next.js Frontend)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Onboarding │  │   Results    │  │  Saved Trips     │  │
│  │    Chat     │  │  Dashboard   │  │   & Personas     │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API SERVER                      │
│                      (NestJS TypeScript)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Controllers Layer                        │  │
│  │  ┌─────────┐  ┌────────────┐  ┌─────────────────┐  │  │
│  │  │  Users  │  │   Places   │  │ Recommendations │  │  │
│  │  └─────────┘  └────────────┘  └─────────────────┘  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐    │
│  │              Services Layer                         │    │
│  │  ┌──────────────┐  ┌──────────────────────────┐   │    │
│  │  │Vibe Mapping  │  │  Match Scoring Engine    │   │    │
│  │  │   Service    │  │  (Personality Algorithm) │   │    │
│  │  └──────────────┘  └──────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI SERVICE LAYER                        │
│                  (Python Multi-Agent System)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Mother Agent (Orchestrator)             │   │
│  └───┬────────┬────────┬────────┬────────┬────────────┘   │
│      │        │        │        │        │                  │
│  ┌───▼──┐ ┌──▼───┐ ┌──▼────┐ ┌─▼─────┐ ┌▼──────┐         │
│  │Flight│ │Hotel │ │Activity│ │Budget │ │ Visa  │         │
│  │Agent │ │Agent │ │ Agent  │ │ Agent │ │ Agent │         │
│  └──────┘ └──────┘ └────────┘ └───────┘ └───────┘         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Guardrails Layer (Safety & Validation)              │  │
│  │  • Input sanitization • Output validation            │  │
│  │  • Hallucination prevention • Budget constraints     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
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

## 📁 Project Structure

```
lotara/
├── frontend/              # Next.js React application
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   │   ├── onboarding/    # Chat-based questionnaire
│   │   │   ├── persona/       # Travel personality results
│   │   │   ├── result/        # Recommended destinations
│   │   │   ├── saved/         # Saved trips
│   │   │   └── explain/       # Recommendation explanations
│   │   ├── components/   # Reusable UI components
│   │   │   ├── chat-bubble.tsx
│   │   │   ├── chat-onboarding.tsx
│   │   │   └── ...
│   │   ├── lib/          # Utilities and API client
│   │   └── styles/       # Global styles
│   ├── package.json
│   └── tsconfig.json
│
├── backend/              # NestJS TypeScript API server
│   ├── src/
│   │   ├── users/        # User management & onboarding
│   │   │   ├── controllers/   # HTTP endpoints
│   │   │   ├── services/      # Business logic
│   │   │   │   └── vibe-mapping.service.ts  # Core algorithm
│   │   │   └── entities/      # User data models
│   │   ├── places/       # Vietnam destination data
│   │   │   ├── entities/      # Place models with vibe vectors
│   │   │   └── services/      # Mock data (12 destinations)
│   │   ├── recommendations/  # Matching engine
│   │   │   ├── services/
│   │   │   │   ├── match-scoring.service.ts    # Core scoring algorithm
│   │   │   │   └── recommendations.service.ts  # Orchestration
│   │   │   └── controllers/
│   │   ├── hotels/       # Hotel recommendations (future)
│   │   └── migrations/   # Database schema (TypeORM)
│   ├── test/             # E2E and integration tests
│   ├── data/             # Mock data files
│   ├── prompts/          # AI prompt templates
│   └── package.json
│
├── AI/                   # Python AI service
│   ├── src/
│   │   └── travel_lotara/
│   │       ├── agents/        # 5 specialized AI agents
│   │       ├── core/          # State machine & orchestration
│   │       ├── guardrails/    # Safety & validation layers
│   │       ├── tools/         # Agent capabilities
│   │       └── tracking/      # Opik integration
│   ├── services/
│   │   └── backend/      # FastAPI wrapper (alternative deployment)
│   ├── api/              # Vercel serverless entry point
│   ├── requirements.txt
│   └── README.md
│
└── README.md            # This file
```

---

## 🧠 How It Works

### **Step 1: Personality Discovery** (5 minutes)

Users engage with an interactive chat-based questionnaire that asks about:
- **Trip Basics** — Duration, companions, budget range
- **Travel Pace** — Rushed vs. relaxed, structured vs. spontaneous
- **Environment Preferences** — Nature vs. city, quiet vs. lively, crowds vs. solitude
- **Activity Level** — Adventure sports vs. leisurely exploration
- **Cultural Interests** — Museums, food scenes, nightlife, local experiences
- **Work Needs** — For digital nomads: deadlines, workspace requirements

**Behind the Scenes:** The Vibe Mapping Service converts these answers into a multi-dimensional personality vector. For example:
```javascript
{
  lowkey: 7,      // Preference for quiet over busy (0-10 scale)
  nature: 9,      // Nature over urban environments
  crowds: 3,      // Low tolerance for crowds
  social: 5       // Balanced social vs. solo activities
}
```

### **Step 2: Travel Persona Assignment**

Based on your vibe profile, Lotara assigns you a travel persona, such as:
- **🌿 Nature Seeker** — Loves outdoor adventures and tranquil landscapes
- **🎭 Cultural Explorer** — Passionate about history, museums, and local traditions
- **🌃 Urban Adventurer** — Thrives in bustling cities and nightlife
- **🧘 Zen Traveler** — Seeks relaxation, wellness, and peaceful retreats
- **💼 Digital Nomad** — Balances productivity with exploration

### **Step 3: Smart Destination Matching**

The Match Scoring Engine compares your vibe vector against every destination's vibe profile.

**Scoring Algorithm:**
```typescript
// For each destination
matchScore = 100 - (average of all dimension differences) × 10

// Example: User (lowkey: 7) vs. Sapa (lowkey: 8)
difference = |7 - 8| = 1
// After averaging all dimensions: score = 95/100
```

Destinations are ranked by compatibility, and the top matches are selected.

### **Step 4: Curated Recommendations with Explanations**

You receive:
- **Top 5-10 Destinations** — Vietnamese cities perfectly matched to your personality
- **Hotel Recommendations** — Properties that fit both your vibe and budget
- **Detailed Itineraries** — Day-by-day plans with activities, dining, and free time
- **Transparent Explanations** — Why each place was chosen for *you specifically*

**Example Explanation:**
> "Sapa scored 95% compatibility with your profile. You prefer peaceful, nature-focused experiences (Nature: 9/10), and Sapa's terraced rice paddies and mountain trails align perfectly. Its low tourist density (Crowds: 4/10) matches your preference for quieter destinations."

### **Step 5: Save, Customize, and Book** (Coming Soon)

- Save favorite itineraries to your account
- Adjust dates and activities
- Book hotels and experiences directly through the platform

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
