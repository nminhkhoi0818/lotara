# Backend Server - Import Fix Summary

## Problem

When running `uvicorn main:app`, the server crashed with:
```
ImportError: attempted relative import with no known parent package
```

## Root Cause

The `main.py` file used relative imports:
```python
from .api.models import PlanRequest
from .core.job_manager import JobManager
```

When uvicorn loads `main:app` directly, Python treats `main.py` as a standalone script, not as part of a package, causing relative imports to fail.

## Solution

### 1. Changed Imports in main.py ✅

**Before:**
```python
from .api.models import (...)
from .core.job_manager import JobManager
from .core.workflow_executor import WorkflowExecutor
```

**After:**
```python
from api.models import (...)
from core.job_manager import JobManager
from core.workflow_executor import WorkflowExecutor
```

### 2. Created run.py Entry Point ✅

A proper entry point that:
- Sets up Python path correctly
- Adds both backend directory and project root to sys.path
- Runs uvicorn programmatically

```python
# services/backend/run.py
sys.path.insert(0, str(backend_dir))  # For local imports
sys.path.insert(0, str(project_root))  # For travel_lotara imports
```

## How to Run the Server

### ✅ Recommended: Use run.py

```bash
cd services/backend
python run.py
```

This automatically:
- Sets up Python paths
- Starts uvicorn
- Enables hot reload
- Shows helpful startup messages

### ⚠️ Alternative: Direct uvicorn (requires correct directory)

```bash
cd services/backend
uvicorn main:app --reload
```

**Important:** You MUST be in the `services/backend` directory for this to work.

## Verification

```bash
# Test imports work
cd services/backend
python -c "from api.models import PlanRequest; print('✓ OK')"

# Test server starts
python run.py

# In another terminal:
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T...",
  "version": "1.0.0"
}
```

## Files Modified

1. **services/backend/main.py**
   - Changed relative imports to absolute imports
   - Lines 27, 40, 41

2. **services/backend/run.py** (NEW)
   - Proper entry point with path setup
   - Better UX with startup messages

3. **services/backend/START_SERVER.md** (NEW)
   - Quick start guide
   - Troubleshooting tips

## Related Files (No Changes Needed)

These files still use relative imports, which is correct:
- `services/backend/core/job_manager.py`
- `services/backend/core/workflow_executor.py`
- `services/backend/scheduler/proactive_scheduler.py`

They are imported by `main.py`, not loaded directly, so relative imports work fine.

## Testing Checklist

- [x] Imports resolve correctly
- [x] Server starts without errors
- [x] Health endpoint responds
- [x] API docs accessible at /docs
- [ ] POST /v1/plan endpoint works (needs Redis)
- [ ] Workflow execution completes (needs Redis + API keys)

## Next Steps

1. **Start Redis:**
   ```bash
   docker run -d --name lotara-redis -p 6379:6379 redis:7-alpine
   ```

2. **Configure API keys:**
   ```bash
   # Edit services/backend/.env
   GOOGLE_API_KEY=your_key
   OPIK_API_KEY=your_key
   ```

3. **Test full workflow:**
   ```bash
   curl -X POST http://localhost:8000/v1/plan \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "query": "Tokyo trip $3000", "constraints": {}}'
   ```

## Status

✅ **FIXED** - Server now starts successfully with either method
