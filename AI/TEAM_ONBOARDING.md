# 🚀 Team Member Quick Start Guide

Welcome to the Lotara AI team! This guide will get you up and running quickly.

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Python 3.10 or higher installed
- [ ] Git installed
- [ ] A Google Account (for Gemini API)
- [ ] An Opik account (sign up at https://www.comet.com)
- [ ] A code editor (VS Code recommended)

## ⚡ 5-Minute Setup

### Step 1: Get API Keys

**Google API Key** (Required):
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

**Opik API Key** (Required):
1. Go to https://www.comet.com/opik
2. Sign up or log in
3. Go to Settings → API Keys
4. Create a new key and copy it

**Zilliz Cloud** (Optional - for production):
1. Go to https://zilliz.com/cloud
2. Sign up for free tier
3. Create a cluster
4. Note the URI and API key

### Step 2: Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd lotara/AI

# Install uv (recommended package manager)
pip install uv

# Install dependencies
uv pip install -e .

# Or using regular pip
pip install -e .
```

### Step 3: Configure Environment

Create `.env` file in the `AI` directory:

```bash
# Copy the example (if available)
cp .env.example .env

# Or create manually
touch .env
```

Add your keys to `.env`:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here
OPIK_API_KEY=your_opik_api_key_here
OPIK_PROJECT_NAME=lotara-travel

# Optional (for production vector DB)
ZILLIZ_CLOUD_URI=https://xxx.api.gcp-us-west1.zillizcloud.com
ZILLIZ_CLOUD_API_KEY=your_zilliz_api_key
```

### Step 4: Setup Vector Database

```bash
# Load Vietnam tourism data (420+ locations)
python -m src.travel_lotara.tools.shared_tools.setup_milvus

# This will take ~5 minutes
# It creates embeddings and indexes all locations
```

Expected output:
```
✓ Collection 'lotara_travel' created with HNSW index
✓ Loaded 420 locations
✓ Total locations inserted: 420
✓ Embedding dimension: 768
```

### Step 5: Verify Installation

```bash
# Test vector search with image URLs
python tests/example_nested_image_urls.py
```

You should see:
```
✅ Milvus connection established
📍 Temple of Literature - National Tu Giam (Hanoi)
🖼️ Main Attraction Image: https://...
📌 Destinations with places, cuisines, hotels
```

### Step 6: Run Your First Query

```bash
# Demo script 
python demo.py

# Expected: Complete itinerary for Japan trip
```

## 🎯 What You Should Know

### Project Structure (Key Folders)

```
AI/
├── data/                    # 420+ Vietnamese locations
├── src/travel_lotara/
│   ├── agents/             # Multi-agent system
│   ├── tools/              # Milvus vector search
│   ├── core/               # Orchestrator & evaluation
│   └── config/             # Settings & logging
├── services/backend/       # FastAPI REST API
├── tests/                  # Test files
└── docs/                   # Documentation
```

### Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Edit code
   - Add tests
   - Update docs if needed

3. **Test locally**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run specific test
   python tests/test_milvus.py
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub
   - Create PR from your branch
   - Add description
   - Request review

### Common Development Tasks

**Run the FastAPI server locally:**
```bash
cd services/backend
uvicorn api.main:app --reload --port 8000

# API available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

**Test vector search:**
```bash
python -m src.travel_lotara.tools.shared_tools.milvus_engine
```

**Re-ingest data (if VN_tourism.json changes):**
```bash
python -m src.travel_lotara.tools.shared_tools.reingest_with_image_urls
```

**View Opik traces:**
1. Go to https://www.comet.com/opik
2. Select your project: `lotara-travel`
3. View traces, metrics, evaluations

### Code Standards

**Python Style:**
- Follow PEP 8
- Use type hints (`def func(name: str) -> dict:`)
- Use docstrings (Google style)
- Maximum line length: 100 characters

**Example:**
```python
def search_locations(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for locations using semantic similarity.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        
    Returns:
        List of location dictionaries with similarity scores
    """
    # Implementation here
```

**Logging:**
```python
from src.travel_lotara.config.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Processing request")
logger.error("Error occurred", exc_info=True)
```

**Testing:**
```python
import pytest

def test_location_search():
    """Test that location search returns results."""
    results = search_locations("beach resorts", top_k=3)
    assert len(results) == 3
    assert "Location name" in results[0]
```

## 🔍 Understanding Key Components

### 1. Vector Search (Milvus)

**What it does:** Finds relevant Vietnamese locations based on semantic similarity

**File:** `src/travel_lotara/tools/shared_tools/milvus_engine.py`

**How it works:**
1. User query → Gemini embedding (768-dim vector)
2. Search Milvus with COSINE similarity
3. Return top-K most similar locations
4. Each location has attractions, hotels, restaurants, activities

**Try it:**
```python
from src.travel_lotara.tools.shared_tools.milvus_engine import search_locations

results = search_locations("romantic beach resorts", top_k=3)
print(results[0]['Location name'])
print(results[0]['Hotels'])
```

### 2. Multi-Agent System

**What it does:** Coordinates specialized agents to build complete itineraries

**File:** `src/travel_lotara/core/orchestrator/mother_agent.py`

**Agents:**
- **Inspiration Agent:** Recommends regions
- **Planning Agent:** Retrieves attractions/hotels
- **Budget Agent:** Calculates costs
- **Formatting Agent:** Creates JSON output
- **Feedback Agent:** Handles user questions

**Flow:**
```
User Request → Mother Agent → Agents (parallel) → Formatted Itinerary
```

### 3. Image URL Fields (NEW!)

**What it is:** Rich visual data for places, restaurants, hotels

**Structure:**
```json
{
  "Destinations": [
    {
      "place": {"image_url": "https://..."},
      "cuisine": {"image_url": "https://..."}
    }
  ],
  "Hotels": [
    {"image_url": "https://..."}
  ]
}
```

**See:** [IMAGE_URL_UPDATES.md](IMAGE_URL_UPDATES.md) for details

### 4. Opik Evaluation

**What it does:** Tracks and evaluates agent performance

**How to use:**
```python
from src.travel_lotara.tracking import trace_tool

@trace_tool(name="my_function", tags=["custom"])
def my_function(input_data):
    # Opik automatically tracks:
    # - Input/output
    # - Execution time
    # - Errors
    # - Token usage (for LLM calls)
    return result
```

**View results:** https://www.comet.com/opik

## 🐛 Troubleshooting

### Issue: "Milvus connection failed"

**Solution:**
```bash
# Check if local Milvus is running
# If using Zilliz, verify .env credentials
cat .env | grep ZILLIZ

# Re-run setup
python -m src.travel_lotara.tools.shared_tools.setup_milvus
```

### Issue: "Google API key invalid"

**Solution:**
```bash
# Verify key in .env
cat .env | grep GOOGLE_API_KEY

# Test directly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### Issue: "No module named 'src'"

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Verify installation
python -c "import src.travel_lotara; print('Success!')"
```

### Issue: "Tests failing"

**Solution:**
```bash
# Update dependencies
pip install -e . --upgrade

# Clear cache
rm -rf __pycache__ .pytest_cache

# Run specific test
pytest tests/test_milvus.py -v
```

## 📖 Learning Resources

### Must-Read Documentation

1. **[README.md](README.md)** - Complete project overview
2. **[IMAGE_URL_UPDATES.md](IMAGE_URL_UPDATES.md)** - New image field guide
3. **[QUICK_START.md](docs/QUICK_START.md)** - Detailed setup
4. **[OPIK_EVALUATION_COMPLETE_GUIDE.md](docs/OPIK_EVALUATION_COMPLETE_GUIDE.md)** - Evaluation system

### Code Examples

**Example 1: Search locations**
```python
from src.travel_lotara.tools.shared_tools.milvus_engine import search_locations

results = search_locations("cultural attractions in Hanoi", top_k=5)
for loc in results:
    print(f"{loc['Location name']} - Rating: {loc['Rating']}")
```

**Example 2: Access nested image URLs**
```python
location = results[0]

# Main image
print(location['Image'])

# Place image
if location['Destinations']:
    place = location['Destinations'][0]['place']
    print(place.get('image_url', 'No image'))

# Hotel image
if location['Hotels']:
    hotel = location['Hotels'][0]
    print(hotel.get('image_url', 'No image'))
```

**Example 3: Run agent**
```python
from src.travel_lotara.agents.sub_agents.planning_agent import PlanningAgent

agent = PlanningAgent()
result = await agent.run({
    "destination": "Hoi An",
    "budget": "medium",
    "interests": ["culture", "food"]
})
print(result)
```

## 🎯 Your First Contribution

### Beginner Tasks

Pick one to get started:

1. **Add a test case**
   - File: `tests/test_milvus.py`
   - Add a new test for specific location search
   - Run: `pytest tests/test_milvus.py`

2. **Improve documentation**
   - Pick any doc file in `docs/`
   - Add examples or clarify sections
   - Submit PR

3. **Add logging**
   - Find a function without logging
   - Add `logger.info()`, `logger.debug()`
   - Test it works

4. **Fix a TODO**
   - Search codebase: `grep -r "TODO" src/`
   - Pick a simple one
   - Implement and test

### Intermediate Tasks

1. **Add new location data**
   - Edit `data/VN_tourism.json`
   - Add 5-10 new locations
   - Re-ingest: `python -m src.travel_lotara.tools.shared_tools.reingest_with_image_urls`

2. **Create new Opik evaluator**
   - File: `src/travel_lotara/core/eval/judges.py`
   - Add a custom judge (e.g., "ActivityQualityJudge")
   - Test it

3. **Optimize vector search**
   - File: `src/travel_lotara/tools/shared_tools/milvus_engine.py`
   - Improve caching or query logic
   - Benchmark performance

## 🚀 Next Steps

Once you're comfortable:

1. **Read the full architecture**
   - [architecture.md](docs/architecture.md)
   - Understand agent flow
   - Study state machine

2. **Explore Opik dashboard**
   - https://www.comet.com/opik
   - View traces from your tests
   - Create custom experiments

3. **Try deployment**
   - [VERCEL_SIMPLIFIED.md](VERCEL_SIMPLIFIED.md)
   - Deploy to Vercel
   - Test API endpoints

4. **Join team discussions**
   - Ask questions in Slack/Discord
   - Review PRs from teammates
   - Share what you learned

## 💬 Getting Help

- **Questions?** Ask in team chat or create GitHub issue
- **Bugs?** Create issue with reproduction steps
- **Ideas?** Discuss in team meetings or docs/ROADMAP.md

---

**Welcome to the team! Let's build something amazing together! 🎉**
