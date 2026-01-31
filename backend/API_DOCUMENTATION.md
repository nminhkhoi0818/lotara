# Lotara API Documentation

## Base URL
```
http://localhost:3000
```

## Table of Contents
- [Authentication](#authentication)
- [Users Endpoints](#users-endpoints)
- [Questions Endpoints](#questions-endpoints)
- [Recommendations Endpoints](#recommendations-endpoints)
- [Error Handling](#error-handling)

---

## Authentication
Currently, the API does not require authentication. All endpoints are public.

---

## Users Endpoints

### 1. Create User from Onboarding
**POST** `/users/onboarding`

Creates a new user from initial onboarding data (legacy endpoint).

#### Request Body
```json
{
  "budget": "medium",
  "travelStyle": "solo",
  "answers": {
    "quiet_or_lively": "quiet",
    "nature_or_city": "nature",
    "crowd_tolerance": 5
  }
}
```

#### Request Parameters
| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| budget | string | Yes | "low", "medium", "high" | User's budget range |
| travelStyle | string | Yes | "solo", "couple", "group" | User's travel style |
| answers | object | Yes | - | User's preference answers |
| answers.quiet_or_lively | string | No | "quiet", "lively" | Preference for atmosphere |
| answers.nature_or_city | string | No | "nature", "city" | Preference for environment |
| answers.crowd_tolerance | number | No | 0-10 | Tolerance for crowds (0=low, 10=high) |

#### Success Response (200 OK)
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Error Responses
- **400 Bad Request**: Invalid input or vibe values
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request"
}
```

- **500 Internal Server Error**: Persistence failure
```json
{
  "statusCode": 500,
  "message": "Failed to process user onboarding",
  "error": "Internal Server Error"
}
```

---

### 2. Submit User Onboarding (Persona Questionnaire)
**POST** `/users/onboarding/submit`

Submits comprehensive user onboarding answers from the persona questionnaire.

#### Request Body
```json
{
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
}
```

#### Request Parameters
| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| duration | string | Yes | "short", "medium", "long", "extended" | Trip duration preference |
| companions | string | Yes | "solo", "couple", "family_kids", "family_adults", "friends" | Travel companions |
| budget | string | Yes | "budget", "midrange", "comfortable", "luxury" | Budget category |
| pace | string | Yes | "slow", "balanced", "fast" | Travel pace |
| travelStyle | string | Yes | "adventure", "cultural", "nature", "food", "wellness", "photography" | Primary travel interest |
| activity | string | Yes | "low", "medium", "high" | Activity level |
| crowds | string | Yes | "avoid", "mixed", "embrace" | Crowd preference |
| accommodation | string | Yes | "hostel", "standard", "boutique", "premium" | Accommodation preference |
| remote | boolean | Yes | true, false | Interest in remote locations |
| timing | string | Yes | "morning", "flexible", "evening" | Preferred time of day |

#### Success Response (200 OK)
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
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
}
```

#### Error Responses
- **400 Bad Request**: Invalid input
- **500 Internal Server Error**: Persistence failure

---

### 3. Get User by ID
**GET** `/users/:id`

Retrieves a user by ID with all their data including persona answers.

#### URL Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| id | string (UUID) | User ID |

#### Success Response (200 OK)
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
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
}
```

#### Error Responses
- **404 Not Found**: User does not exist
```json
{
  "statusCode": 404,
  "message": "User with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "error": "Not Found"
}
```

- **500 Internal Server Error**: Database error

---

## Questions Endpoints

### 1. Get All Questions
**GET** `/questions`

Retrieves all onboarding questions.

#### Success Response (200 OK)
```json
[
  {
    "id": "q-1",
    "key": "quiet_or_lively",
    "question": "Do you prefer quiet, peaceful places or lively, energetic ones?",
    "type": "options",
    "options": [
      {
        "label": "Quiet & Peaceful",
        "value": "quiet"
      },
      {
        "label": "Lively & Energetic",
        "value": "lively"
      }
    ],
    "orderIndex": 1
  },
  {
    "id": "q-2",
    "key": "nature_or_city",
    "question": "Would you rather explore nature or dive into city life?",
    "type": "options",
    "options": [
      {
        "label": "Nature & Outdoors",
        "value": "nature"
      },
      {
        "label": "City Life & Culture",
        "value": "city"
      }
    ],
    "orderIndex": 2
  },
  {
    "id": "q-3",
    "key": "crowd_tolerance",
    "question": "How do you feel about crowds?",
    "type": "scale",
    "options": [],
    "orderIndex": 3
  }
]
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| id | string | Question ID |
| key | string | Question key for mapping answers |
| question | string | Question text |
| type | string | Question type ("options" or "scale") |
| options | array | Available options for the question |
| options[].label | string | Display label for the option |
| options[].value | string | Value to submit |
| orderIndex | number | Display order |

---

## Recommendations Endpoints

### 1. Get Personalized Recommendations
**GET** `/recommendations/:userId`

Get personalized place recommendations for a user based on their preferences.

#### URL Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string (UUID) | User ID |

#### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | number | No | 10 | Maximum number of recommendations (max: 50) |

#### Example Request
```
GET /recommendations/550e8400-e29b-41d4-a716-446655440000?limit=5
```

#### Success Response (200 OK)
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "recommendations": [
    {
      "placeId": "place-1",
      "placeName": "Halong Bay",
      "region": "Quang Ninh",
      "description": "UNESCO World Heritage site featuring emerald waters and thousands of towering limestone islands topped with rainforests.",
      "score": 92,
      "vibe_compatibility": {
        "lowkey": 3,
        "nature": 0,
        "crowds": 2,
        "social": 2
      }
    },
    {
      "placeId": "place-2",
      "placeName": "Hoi An Ancient Town",
      "region": "Quang Nam",
      "description": "Charming historic town with well-preserved architecture, lantern-lit streets, and artisan culture.",
      "score": 88,
      "vibe_compatibility": {
        "lowkey": 4,
        "nature": 1,
        "crowds": 3,
        "social": 3
      }
    }
  ],
  "totalMatches": 2
}
```

#### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| userId | string | User ID |
| recommendations | array | List of recommended places |
| recommendations[].placeId | string | Place ID |
| recommendations[].placeName | string | Place name |
| recommendations[].region | string | Geographic region |
| recommendations[].description | string | Place description |
| recommendations[].score | number | Match score (0-100) |
| recommendations[].vibe_compatibility | object | Vibe dimension scores |
| recommendations[].vibe_compatibility.lowkey | number | Lowkey vs lively score |
| recommendations[].vibe_compatibility.nature | number | Nature vs city score |
| recommendations[].vibe_compatibility.crowds | number | Crowd tolerance score |
| recommendations[].vibe_compatibility.social | number | Social vs solo score |
| totalMatches | number | Total number of matching places |

---

### 2. Get All Place Scores (Debug/Analytics)
**GET** `/recommendations/:userId/all`

Get scores for all places. Useful for debugging and analytics.

#### URL Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string (UUID) | User ID |

#### Example Request
```
GET /recommendations/550e8400-e29b-41d4-a716-446655440000/all
```

#### Success Response (200 OK)
Returns all places scored and ranked for the user. Same structure as the personalized recommendations endpoint but includes all places.

---

### 3. Generate AI-Powered Itinerary
**POST** `/recommendations/:userId/generate`

Generate an AI-powered travel itinerary based on the user's persona and preferences.

This endpoint:
1. Fetches the user's persona data from the database
2. Sends it to the AI service for itinerary generation
3. Returns the AI-generated itinerary

#### URL Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string (UUID) | User ID |

#### Example Request
```
POST /recommendations/550e8400-e29b-41d4-a716-446655440000/generate
```

#### Success Response (200 OK)
Returns the AI service response as-is. The exact structure depends on the AI service.

Example:
```json
{
  "itinerary": {
    "days": [...],
    "recommendations": [...],
    "summary": "..."
  }
}
```

#### Error Responses

**404 Not Found - User Not Found**
```json
{
  "statusCode": 404,
  "message": "User 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

**404 Not Found - Missing Persona Data**
```json
{
  "statusCode": 404,
  "message": "User 550e8400-e29b-41d4-a716-446655440000 does not have persona answers. Please complete onboarding first."
}
```

**503 Service Unavailable - AI Service Down**
```json
{
  "statusCode": 503,
  "message": "AI service did not respond",
  "error": "No response received from the AI service. Please try again later."
}
```

**500 Internal Server Error - AI Service Error**
```json
{
  "statusCode": 500,
  "message": "AI service returned an error",
  "error": {...}
}
```

---

## Error Handling

### Standard Error Response Format
All errors follow this structure:

```json
{
  "statusCode": 400,
  "message": "Error message or array of validation errors",
  "error": "Bad Request"
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input or validation error |
| 404 | Not Found - Resource does not exist |
| 500 | Internal Server Error - Server-side error |

### Common Validation Errors

#### Missing Required Fields
```json
{
  "statusCode": 400,
  "message": [
    "budget must be one of: low, medium, high",
    "travelStyle must be one of: solo, couple, group"
  ],
  "error": "Bad Request"
}
```

#### Invalid Enum Values
```json
{
  "statusCode": 400,
  "message": [
    "duration must be one of: short, medium, long, extended"
  ],
  "error": "Bad Request"
}
```

#### Invalid Data Type
```json
{
  "statusCode": 400,
  "message": [
    "remote must be a boolean"
  ],
  "error": "Bad Request"
}
```

#### Invalid Number Range
```json
{
  "statusCode": 400,
  "message": [
    "crowd_tolerance must be between 0 and 10"
  ],
  "error": "Bad Request"
}
```

---

## Integration Examples

### Frontend Integration Examples

#### 1. Fetch Questions for Onboarding
```typescript
async function fetchQuestions() {
  try {
    const response = await fetch('http://localhost:3000/questions');
    if (!response.ok) throw new Error('Failed to fetch questions');
    const questions = await response.json();
    return questions;
  } catch (error) {
    console.error('Error fetching questions:', error);
    throw error;
  }
}
```

#### 2. Submit User Onboarding
```typescript
async function submitOnboarding(answers: {
  duration: string;
  companions: string;
  budget: string;
  pace: string;
  travelStyle: string;
  activity: string;
  crowds: string;
  accommodation: string;
  remote: boolean;
  timing: string;
}) {
  try {
    const response = await fetch('http://localhost:3000/users/onboarding/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(answers),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }
    
    const result = await response.json();
    return result.userId;
  } catch (error) {
    console.error('Error submitting onboarding:', error);
    throw error;
  }
}
```

#### 3. Fetch User Data
```typescript
async function getUserData(userId: string) {
  try {
    const response = await fetch(`http://localhost:3000/users/${userId}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User not found');
      }
      throw new Error('Failed to fetch user data');
    }
    
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}
```

#### 4. Fetch Recommendations
```typescript
async function getRecommendations(userId: string, limit: number = 10) {
  try {
    const response = await fetch(
      `http://localhost:3000/recommendations/${userId}?limit=${limit}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    
    const recommendations = await response.json();
    return recommendations;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
}
```

#### 5. Complete Onboarding Flow Example
```typescript
async function completeOnboardingFlow() {
  try {
    // Step 1: Fetch questions
    const questions = await fetchQuestions();
    console.log('Questions loaded:', questions);
    
    // Step 2: User answers questions (collect via UI)
    const userAnswers = {
      duration: 'medium',
      companions: 'solo',
      budget: 'midrange',
      pace: 'balanced',
      travelStyle: 'cultural',
      activity: 'medium',
      crowds: 'mixed',
      accommodation: 'standard',
      remote: false,
      timing: 'flexible'
    };
    
    // Step 3: Submit onboarding
    const userId = await submitOnboarding(userAnswers);
    console.log('User created:', userId);
    
    // Step 4: Fetch recommendations
    const recommendations = await getRecommendations(userId, 5);
    console.log('Recommendations:', recommendations);
    
    return { userId, recommendations };
  } catch (error) {
    console.error('Onboarding flow error:', error);
    throw error;
  }
}
```

---

## CORS Configuration

The backend currently does not have CORS configured. For frontend integration, you may need to add CORS support in `main.ts`:

```typescript
app.enableCors({
  origin: 'http://localhost:3001', // Your frontend URL
  credentials: true,
});
```

---

## Data Types Reference

### VibeVector
```typescript
{
  lowkey: number;    // 0-10: quiet (0) to lively (10)
  nature: number;    // 0-10: nature (0) to city (10)
  crowds: number;    // 0-10: avoid (0) to embrace (10)
  social: number;    // 0-10: solo (0) to group (10)
}
```

### BudgetRange
```typescript
type BudgetRange = 'low' | 'medium' | 'high';
```

### TravelStyle
```typescript
type TravelStyle = 'solo' | 'couple' | 'group';
```

---

## Notes for Frontend Developers

1. **User ID Storage**: After creating a user via `/users/onboarding/submit`, store the returned `userId` in local storage or session storage for subsequent API calls.

2. **Validation**: The backend uses strict validation. Ensure all enum values match exactly (case-sensitive).

3. **Error Handling**: Always handle both network errors and API validation errors in your frontend.

4. **Recommendations**: Recommendations are calculated based on user's vibe vector. The more complete the user's onboarding data, the better the recommendations.

5. **Limit Parameter**: When fetching recommendations, the limit parameter is capped at 50 to prevent performance issues.

6. **UUID Format**: User IDs are UUIDs. Ensure your frontend can handle UUID strings.

---

## Development Tips

- **Local Testing**: Use tools like Postman or curl to test endpoints
- **TypeScript Types**: Consider generating TypeScript types from the DTOs for type safety
- **Environment Variables**: Configure the base URL based on environment (development/production)
- **Loading States**: Implement proper loading states for API calls
- **Retry Logic**: Consider implementing retry logic for failed requests

---

## Changelog

### Version 1.0 (Current)
- Initial API documentation
- User onboarding endpoints
- Questions endpoint
- Recommendations endpoints
- Basic error handling

---

For questions or issues, please contact the backend team or create an issue in the project repository.
