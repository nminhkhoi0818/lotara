# Lorata Backend – Project Overview & Feature Scope

## 1. Project Overview

**Lorata** is a backend system that powers a **personality-driven travel recommendation app** for Vietnam.

Instead of recommending places based on popularity, Lorata matches **user vibe** (personality, habits, budget) with **place vibe** (crowds, nature, social energy) to produce **highly personalized travel suggestions**.

The backend is designed to be:

* Deterministic and explainable
* AI-assisted but not AI-dependent
* Modular and extensible

---

## 2. Backend Responsibilities

The backend is responsible for:

* Modeling users and places
* Defining and validating vibe data
* Matching users with suitable places
* Providing clean APIs for frontend consumption
* Integrating AI **only as an enrichment layer** (never decision-making)

Out of scope for backend MVP:

* UI / frontend
* Payments & booking
* Real-time pricing
* Social features

---

## 3. Core Concept: Vibe Matching

### 3.1 User Vibe

User vibe represents personality and travel preferences, expressed as a **numeric vector (0–10)**.

Example:

```json
{
  "lowkey": 8,
  "nature": 9,
  "crowds": 2,
  "social": 3
}
```

User vibe is collected during onboarding and stored permanently.

---

### 3.2 Place Vibe

Place vibe represents the *experience* a location offers.

Each place has:

* Descriptive metadata (region, description)
* A vibe vector using the same keys as user vibe

This allows direct mathematical comparison.

---

## 4. Feature Breakdown (Backend)

### Feature 1: Place Management

**Purpose:** Store and serve structured travel destinations.

Responsibilities:

* Persist places in Postgres
* Validate vibe vectors
* Activate / deactivate places

Core data fields:

* Name, region, description
* Vibe vector (jsonb)
* Budget range
* Best travel style (solo, couple, group)

APIs:

* Create place (internal/admin)
* List active places
* Get place detail

---

### Feature 2: User Onboarding & Preference Modeling

**Purpose:** Convert user answers into a normalized vibe vector.

Responsibilities:

* Accept onboarding answers
* Transform answers into numeric vibe values
* Validate and store user preferences

Important rules:

* All vibe keys are mandatory
* No AI required for onboarding

Output:

* `userId` used for future recommendations

---

### Feature 3: Recommendation Engine (Core Logic)

**Purpose:** Match users with the most suitable places.

Responsibilities:

* Load user and place data
* Filter places by budget and travel style
* Calculate match score per place
* Rank and return top results

Design principles:

* Fully deterministic
* Testable pure functions
* AI-independent

---

### Feature 4: Match Scoring System

**Purpose:** Quantify how well a place fits a user.

Logic:

* Compare user vibe and place vibe per key
* Use absolute difference
* Convert difference into a 0–100 score

Example:

```
score = 100 - avg(|userVibe - placeVibe|) * 10
```

Lower difference means better match.

---

### Feature 5: AI Explanation Layer (Optional / Phase 2)

**Purpose:** Explain *why* a place was recommended.

Responsibilities:

* Generate human-readable explanations
* Summarize vibe compatibility

Strict rule:

> AI must never influence ranking or filtering logic.

If AI fails, the system must still return recommendations.

---

### Feature 6: Data Import & Automation (Future)

**Purpose:** Scale place data without manual input.

Approach:

* External tools (e.g., n8n) crawl and clean data
* Backend exposes ingestion APIs
* Backend validates and stores normalized data

This feature is **not required for MVP**.

---

## 5. System Boundaries

### Backend Owns:

* Business logic
* Data consistency
* Recommendation correctness

### Backend Does Not Own:

* UI/UX decisions
* Hotel booking
* Price comparison
* Affiliate logic

---

## 6. Architectural Principles

1. **Determinism first** – core logic must be predictable
2. **AI as assistant** – never as decision maker
3. **Schema stability** – vibe keys should rarely change
4. **Explainability** – every recommendation should be justifiable

---

## 7. Definition of Backend Success

The backend is considered successful when:

* Users receive recommendations that match their personality
* Recommendations are consistent and explainable
* New places can be added without logic changes
* AI can be added or removed without breaking the system

---

## 8. One-Line Summary

> Lorata backend matches people with places using personality-based vibe scoring, not popularity or trends.
