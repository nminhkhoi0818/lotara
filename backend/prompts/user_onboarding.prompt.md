# Lorata Backend – Feature Prompt: User Onboarding

## Feature Name

**User Onboarding & Preference Modeling**

---

## 1. Feature Purpose

This feature is responsible for **collecting user travel preferences** and converting them into a **normalized vibe vector** that can be used by the recommendation engine.

The output of this feature is a **persisted user record** containing:

* A validated vibe vector
* Budget preference
* Travel style

This feature **does not involve AI** and must remain fully deterministic.

---

## 2. Responsibilities (Backend)

The backend must:

1. Accept onboarding data from the frontend
2. Transform qualitative answers into numeric vibe values
3. Validate the resulting vibe vector
4. Persist the user data
5. Return a `userId` for future requests

The backend must **not**:

* Perform authentication
* Use AI or LLMs
* Infer preferences beyond provided answers

---

## 3. Input Contract

### API Endpoint

```
POST /users/onboarding
```

### Request Payload

```json
{
  "budget": "medium",
  "travelStyle": "solo",
  "answers": {
    "quiet_or_lively": "quiet",
    "nature_or_city": "nature",
    "crowd_tolerance": 2
  }
}
```

---

## 4. Supported Answer Schema

The backend only supports the following onboarding questions:

| Question Key    | Description                       | Expected Value      |
| --------------- | --------------------------------- | ------------------- |
| quiet_or_lively | Preference for environment energy | `quiet` or `lively` |
| nature_or_city  | Environment preference            | `nature` or `city`  |
| crowd_tolerance | Crowd tolerance level             | Integer (0–10)      |

Any unsupported keys must be ignored or rejected.

---

## 5. Vibe Mapping Rules

### Vibe Keys (Frozen)

```
lowkey
nature
crowds
social
```

### Mapping Logic

| Answer          | Vibe Effect             |
| --------------- | ----------------------- |
| quiet           | lowkey = 8, social = 3  |
| lively          | lowkey = 2, social = 8  |
| nature          | nature = 9              |
| city            | nature = 3              |
| crowd_tolerance | crowds = provided value |

Missing vibe keys must be **derived or defaulted** so that all keys exist.

---

## 6. Vibe Normalization Rules

* All vibe values must be integers
* All values must be in the range **0–10**
* All vibe keys must be present

If validation fails, the backend must return **400 Bad Request**.

---

## 7. Data Persistence

### User Entity (Relevant Fields)

```
User
- id (uuid)
- vibe_vector (jsonb)
- budget_range (enum: low | medium | high)
- travel_style (enum: solo | couple | group)
- created_at (timestamp)
```

---

## 8. Output Contract

### Success Response

```json
{
  "userId": "uuid"
}
```

### Error Responses

* 400: Invalid input or vibe values
* 500: Persistence failure

---

## 9. Determinism & Testing Rules

* The same input must always produce the same vibe vector
* Mapping logic must be implemented as a **pure function**
* Unit tests should cover:

  * Valid input
  * Missing answers
  * Out-of-range values

---

## 10. Explicit Non-Goals

* ❌ AI personality inference
* ❌ Dynamic question generation
* ❌ User authentication
* ❌ Session handling

---

## 11. Definition of Done

This feature is complete when:

* A user can be onboarded via API
* A valid vibe vector is stored
* An ID is returned to the frontend
* Invalid inputs are rejected consistently

---

## Guiding Principle

> User onboarding defines the **truth** about user preferences. All downstream logic depends on this data being clean, validated, and deterministic.
