# Lotara - AI-Powered Personalized Vietnam Travel Planning

![Lotara](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-Proprietary-blue) ![Deploy](https://img.shields.io/badge/Deployed-Vercel-success)

> **Your Perfect Vietnam Trip, Designed for You** — Stop settling for generic recommendations. Lotara uses AI and personality-based matching to craft the perfect itinerary tailored to your unique travel style.

**Live Demo:** [https://lotara.vercel.app](https://lotara.vercel.app)

---

## 🎯 What is Lotara?

Lotara is an AI-powered travel planning platform that creates personalized Vietnam itineraries based on your unique personality, travel style, budget, and preferences. In just 5 minutes, users answer a profile questionnaire, discover their travel persona, and receive AI-curated recommendations including cities, hotels, and detailed itineraries—all explained and transparent.

### Key Features

✨ **Personality-Based Planning** — Your trip reflects your unique travel personality, not generic algorithms

💼 **Workcation Mode** — Seamlessly blend work and travel with schedules that respect your deadlines

💰 **Budget-Smart Matching** — Perfect hotels within your budget with transparent pricing

🤖 **Explainable AI** — Understand exactly why each recommendation was chosen for you

⚡ **Fast & Easy** — Get personalized recommendations in just 5 minutes, no credit card required

---

## 📁 Project Structure

```
lotara/
├── frontend/              # Next.js React application
│   ├── src/
│   │   ├── app/          # Pages (onboarding, results, saved, etc.)
│   │   └── components/   # Reusable UI components
│   ├── package.json
│   └── tsconfig.json
│
├── backend/              # NestJS TypeScript API server
│   ├── src/
│   │   ├── users/        # User onboarding & vibe mapping
│   │   ├── places/       # Vietnam destination data & entities
│   │   ├── recommendations/  # Match scoring & recommendations logic
│   │   └── common/       # Shared utilities & pipes
│   ├── test/             # E2E tests
│   ├── package.json
│   └── tsconfig.json
│
├── AI/                   # AI-related documentation and prompts
│   └── README.md
│
└── README.md            # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Git** for version control

### Installation

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

### Running Locally

#### Backend (NestJS)

```bash
cd backend

# Development mode with watch
npm run start:dev

# Production build
npm run build
npm run start:prod
```

The API will be available at `http://localhost:3000`

#### Frontend (Next.js)

```bash
cd frontend

# Development mode with Turbopack
npm run dev

# Production build
npm run build
npm start
```

The frontend will be available at `http://localhost:3000`

---

## 🔧 Tech Stack

### Frontend
- **Framework:** Next.js 15 with React 19
- **Styling:** Tailwind CSS
- **Components:** Radix UI, Lucide React icons
- **Charts:** Recharts
- **Language:** TypeScript

### Backend
- **Framework:** NestJS 11 (Node.js)
- **Language:** TypeScript
- **Validation:** class-validator, class-transformer
- **Testing:** Jest
- **Database:** (Mock data currently, extensible architecture)

---

## 📚 Core Features & Architecture

### 1. **User Onboarding Flow**
Located in `backend/src/users/` and `frontend/src/app/onboarding/`

- Chat-based questionnaire interface
- Captures travel preferences (budget, style, duration, etc.)
- Generates personalized travel persona

### 2. **Vibe Mapping Service**
`backend/src/users/services/vibe-mapping.service.ts`

- Maps user responses to a personality-based "vibe" profile
- Scores dimensions like adventure, comfort, culture, relaxation
- Fully tested with comprehensive test coverage

### 3. **Place Management**
`backend/src/places/`

- 12 mock Vietnamese destinations (Ho Chi Minh City, Hanoi, Da Nang, etc.)
- Each place has associated vibe/personality attributes
- Extensible for database integration

### 4. **Recommendation Engine**
`backend/src/recommendations/services/`

- **Match Scoring:** Deterministic algorithm comparing user vibe to place vibe
- **Ranking:** Places sorted by compatibility score
- **Explainability:** Each recommendation includes detailed explanation
- Formula: `score = 100 - avg(|difference|) * 10`

### 5. **API Endpoints**

**Users:**
- `POST /users/onboarding` — Create user with onboarding data
- `GET /users/:id` — Retrieve user profile

**Recommendations:**
- `GET /recommendations/:userId` — Get personalized place recommendations with explanations

**Places:**
- `GET /places` — List all available destinations

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
npm test

# Watch mode
npm test:watch

# Coverage report
npm test:cov

# E2E tests
npm run test:e2e
```

**Test Coverage:**
- ✅ 60+ tests across 6 test suites
- ✅ Vibe mapping logic
- ✅ Match scoring algorithm
- ✅ Recommendation ranking
- ✅ User onboarding flow

### Manual API Testing

```bash
# Start the backend
npm run start:dev

# In another terminal, test onboarding
curl -X POST http://localhost:3000/users/onboarding \
  -H "Content-Type: application/json" \
  -d '{"name":"John","travelStyle":"adventure","budget":5000,...}'

# Get recommendations
curl http://localhost:3000/recommendations/<userId>
```

See [RECOMMENDATIONS_QUICKSTART.md](backend/RECOMMENDATIONS_QUICKSTART.md) for detailed API examples.

---

## 📋 Available Scripts

### Backend
- `npm run start` — Start production server
- `npm run start:dev` — Start development with watch
- `npm run build` — Build for production
- `npm test` — Run tests
- `npm run lint` — Lint and fix code
- `npm run format` — Format code with Prettier

### Frontend
- `npm run dev` — Start development server
- `npm run build` — Build for production
- `npm start` — Start production server
- `npm run lint` — Run ESLint

---

## 🎨 Pages & User Flow

### Frontend Routes

1. **Home** (`/`) — Landing page with feature overview
2. **Onboarding** (`/onboarding`) — Chat-based preference questionnaire
3. **Persona** (`/persona`) — Display user's travel personality profile
4. **Results** (`/result`) — Recommended cities with explanations
5. **Saved Trips** (`/saved`) — User's saved itineraries
6. **Explain** (`/explain`) — Detailed explanation of recommendations
7. **Admin** (`/admin`) — Dashboard and management interface

---

## 🧠 How It Works

### Step 1: Profile
Users chat with our AI to provide:
- Travel style (adventure, comfort, culture-focused, etc.)
- Budget constraints
- Duration of trip
- Interests and preferences
- Work requirements (for workcation mode)

### Step 2: Persona
The system analyzes responses and determines:
- Travel personality type
- Vibe profile (scored across multiple dimensions)
- Best-match destinations

### Step 3: Recommendations
AI returns:
- ✅ Curated Vietnamese cities
- ✅ Hand-picked hotels within budget
- ✅ Detailed daily itineraries
- ✅ Full transparency on why each recommendation was chosen

---

## 📦 Deployment

The project is deployed on **Vercel** for the frontend.

### Frontend Deployment
- Platform: Vercel
- Branch: main
- URL: https://lotara.vercel.app

### Backend Deployment
- Can be deployed to any Node.js hosting (Vercel, Railway, Render, etc.)
- Environment variables may be required for production

---

## 📝 Documentation

- [Frontend README](frontend/README.md)
- [Backend README](backend/README.md)
- [Recommendations Quick Start](backend/RECOMMENDATIONS_QUICKSTART.md)
- [Users Module Documentation](backend/src/users/README.md)
- [Recommendations Module Documentation](backend/src/recommendations/README.md)
- [AI Prompts & Instructions](backend/prompts/user_onboarding.md)

---

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

---

## 📄 License

This project is proprietary and all rights are reserved.

---

## 💬 Support & Contact

For questions, issues, or feedback:
- Visit: https://lotara.vercel.app
- Email: contact@lotara.app (coming soon)
- Demo: Schedule a demo on the website

---

## 🎓 Learning Resources

### Architecture & Design Patterns
- Built with NestJS dependency injection pattern
- Modular monolithic architecture for easy scaling
- Service-oriented design for business logic separation

### Key Concepts
- **Personality Scoring:** Multi-dimensional vibe matching algorithm
- **Deterministic Recommendations:** Reproducible results based on user input
- **Explainable AI:** Every recommendation includes reasoning

---

## 🎯 Roadmap

Future enhancements:
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real hotel & price data integration
- [ ] Multi-country support
- [ ] User authentication & accounts
- [ ] Itinerary customization UI
- [ ] Payment integration for bookings
- [ ] Mobile app (React Native)

---

**Made with ❤️ for travelers who want personalized adventures** ✈️
