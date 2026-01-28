# Fixing 429 Rate Limit Errors - Complete Guide

## 🔴 Problem: 429 RESOURCE_EXHAUSTED

You're hitting Google Gemini API rate limits. This guide provides comprehensive solutions.

## ✅ Solutions Implemented

### 1. **Request Queuing** (New!)
- **Max Concurrent Requests**: Limited to 2 simultaneous itinerary generations
- **Rate Limit**: Max 3 requests per minute
- **Automatic Waiting**: Requests queue automatically when limit reached
- **Status Endpoint**: Check queue status at `GET /api/itinerary/queue-status`

### 2. **Smarter Retry Logic** (Improved!)
- **7 retry attempts** (increased from 5)
- **Different backoff for 429 vs 503**:
  - 429 (rate limit): 10s, 20s, 40s, 80s, 160s, 320s
  - 503 (overload): 3s, 6s, 12s, 24s, 48s, 96s
- **Total max wait**: Up to ~11 minutes before giving up

### 3. **Model Switch** (Critical!)
- **Changed to**: `gemini-1.5-flash` (more stable, higher quota)
- **From**: `gemini-2.5-flash` (newer, more rate limited)

### 4. **Better Error Messages**
- Clear distinction between 429 and 503 errors
- Actionable suggestions in API response
- Links to check quota and status

## 🚀 Quick Fixes

### Option 1: Wait and Retry (Easiest)
```bash
# Wait 5-10 minutes
# The rate limit resets over time
```

### Option 2: Check Your Quota
1. Visit: https://aistudio.google.com/app/apikey
2. Check:
   - Requests per minute (RPM)
   - Requests per day (RPD)
   - Tokens per minute (TPM)
3. Consider upgrading to paid tier if needed

### Option 3: Switch Model (Recommended)
Already done in `.env`:
```bash
# Current setting (good for rate limits)
LOTARA_MODEL=gemini-1.5-flash

# If still issues, try:
# LOTARA_MODEL=gemini-1.5-pro  # Higher quota but slower
```

### Option 4: Monitor Queue Status
```bash
curl http://localhost:8000/api/itinerary/queue-status
```

Response shows:
```json
{
  "available_slots": 2,
  "max_concurrent": 2,
  "requests_last_minute": 1,
  "requests_per_minute_limit": 3,
  "queue_utilization": "33.3%"
}
```

## 🔧 Configuration

### Adjust Queue Settings
Edit `services/backend/api/middleware/rate_limiter.py`:

```python
request_queue = RequestQueue(
    max_concurrent=2,      # Change to 1 for more conservative
    requests_per_minute=3  # Change to 2 for stricter limit
)
```

### Adjust Retry Settings
Edit `src/travel_lotara/main.py`:

```python
max_retries = 7              # Increase for more patience
base_delay_429 = 10          # Increase for longer waits
base_delay_503 = 3
```

## 📊 Understanding Rate Limits

### Google Gemini API Limits (Free Tier)
| Model | RPM | RPD | TPM |
|-------|-----|-----|-----|
| gemini-1.5-flash | 15 | 1,500 | 1M |
| gemini-1.5-pro | 2 | 50 | 32K |
| gemini-2.5-flash | 10* | 500* | 4M* |

*Approximate, subject to change

### Our Queue Settings
| Setting | Value | Reason |
|---------|-------|--------|
| Max Concurrent | 2 | Prevents overwhelming API |
| RPM Limit | 3 | Well below API limit |
| Retry Attempts | 7 | Enough time for limits to reset |

## 🎯 Best Practices

### For Development
1. **Use `gemini-1.5-flash`** - Most stable
2. **Test with small requests** - Short duration trips
3. **Monitor queue status** - Check before multiple requests
4. **Space out tests** - Wait 20s between manual tests

### For Production
1. **Implement user-level rate limiting** - Prevent abuse
2. **Add request caching** - Return cached results when possible
3. **Background job processing** - Queue requests, process async
4. **Multiple API keys** - Rotate keys for higher limits
5. **Upgrade to paid tier** - Get 10x higher limits

## 🐛 Debugging

### Check Current Bottleneck
```bash
# 1. Check queue status
curl http://localhost:8000/api/itinerary/queue-status

# 2. Check API health
curl http://localhost:8000/health

# 3. Monitor logs for retry attempts
# Look for: [RETRY] or [RATE LIMIT] in output
```

### Common Error Patterns

**Error**: `429 RESOURCE_EXHAUSTED` immediately
- **Cause**: Hit daily quota
- **Fix**: Wait until tomorrow or upgrade

**Error**: `429` after several retries
- **Cause**: Too many requests in short time
- **Fix**: Queue is working, just wait longer

**Error**: `503` errors
- **Cause**: Google's servers overloaded
- **Fix**: Different issue, not rate limit

## 📈 Monitoring

### Server Logs to Watch
```
[QUEUE] Request waited 5.2s in queue     ← Queue is working
[RETRY] Attempt 3/7 - waiting 40s...     ← Retrying 429
[WARNING] Model 429 (rate limited)       ← Hit rate limit
[INFO] Next retry in 80s...              ← Long wait for 429
```

### Success Indicators
```
[INFO] Starting agent execution...       ← Request started
[INFO] Agent execution completed...      ← Success!
No [RETRY] or [QUEUE] messages           ← No issues
```

## 🚨 Emergency Actions

### If Everything Fails

1. **Stop all requests for 1 hour**
2. **Check quota**: https://aistudio.google.com/app/apikey
3. **Switch model to gemini-1.5-flash** (already done)
4. **Reduce queue limits**:
   ```python
   max_concurrent=1,
   requests_per_minute=1
   ```
5. **Contact Google Support** if quota seems wrong

### Alternative: Use Different API Key
```bash
# In .env, try a different key if you have one
GOOGLE_API_KEY=your-alternative-key-here
```

## ✨ New Features Added

### Queue Status Endpoint
```bash
GET /api/itinerary/queue-status
```
Returns real-time queue metrics

### Enhanced Error Responses
```json
{
  "error": "RateLimitExceeded",
  "message": "Google Gemini API rate limit exceeded...",
  "suggestions": [
    "Wait 5-10 minutes before retrying",
    "Check API quota at https://aistudio.google.com/app/apikey",
    "Consider switching to gemini-1.5-flash model"
  ],
  "retry_after": 300
}
```

## 📚 Additional Resources

- **Gemini API Docs**: https://ai.google.dev/gemini-api/docs/quota
- **Rate Limits Guide**: https://google.github.io/adk-docs/agents/models/#error-code-429-resource_exhausted
- **Status Page**: https://status.cloud.google.com/
- **Upgrade Info**: https://ai.google.dev/pricing

## 🎉 Summary

Your API now has:
- ✅ Request queuing (prevents overload)
- ✅ Smart retry logic (429 vs 503 aware)
- ✅ More stable model (gemini-1.5-flash)
- ✅ Better error messages
- ✅ Queue monitoring endpoint
- ✅ Up to 11 minutes of automatic retries

**Most issues should be resolved automatically now!**
