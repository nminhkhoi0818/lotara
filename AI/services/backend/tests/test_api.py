"""
API Tests for Travel Lotara Backend

Tests all API endpoints with real workflows.
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import Mock, patch

from ..main import app
from ..api.models import JobStatus


@pytest.fixture
async def client():
    """HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "services" in data
    assert "redis" in data["services"]


@pytest.mark.asyncio
async def test_plan_trip(client):
    """Test reactive planning endpoint."""
    request_data = {
        "user_id": "test_user",
        "query": "Plan a trip to Tokyo for $3000",
        "constraints": {
            "budget_usd": 3000,
            "duration_days": 5,
        }
    }
    
    response = await client.post("/v1/plan", json=request_data)
    
    assert response.status_code == 202
    data = response.json()
    
    assert "job_id" in data
    assert data["status"] == JobStatus.STARTED.value


@pytest.mark.asyncio
async def test_suggest_proactive(client):
    """Test proactive suggestion endpoint."""
    request_data = {
        "user_id": "test_user",
        "trigger_type": "price_drop",
        "context": {
            "route": "LAX->NRT",
            "old_price": 850,
            "new_price": 650,
            "savings": 200
        }
    }
    
    response = await client.post("/v1/suggest", json=request_data)
    
    assert response.status_code == 202
    data = response.json()
    
    assert "job_id" in data
    assert data["status"] == JobStatus.STARTED.value


@pytest.mark.asyncio
async def test_get_status(client):
    """Test job status endpoint."""
    # First create a job
    plan_response = await client.post("/v1/plan", json={
        "user_id": "test_user",
        "query": "Test query",
        "constraints": {}
    })
    
    job_id = plan_response.json()["job_id"]
    
    # Get status
    response = await client.get(f"/v1/status/{job_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"] == job_id
    assert "status" in data
    assert "mode" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_status_not_found(client):
    """Test status for non-existent job."""
    response = await client.get("/v1/status/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stream_events(client):
    """Test SSE streaming endpoint."""
    # Create job first
    plan_response = await client.post("/v1/plan", json={
        "user_id": "test_user",
        "query": "Test query",
        "constraints": {}
    })
    
    job_id = plan_response.json()["job_id"]
    
    # Connect to stream
    async with client.stream("GET", f"/v1/stream/{job_id}") as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Read first event
        chunk = await response.aiter_bytes().__anext__()
        assert b"event:" in chunk


@pytest.mark.asyncio
async def test_approve_action(client):
    """Test approval endpoint."""
    # Note: This needs a job in waiting_approval state
    # For now, test error case
    
    request_data = {
        "job_id": "nonexistent",
        "approved": True,
        "notes": "Test approval"
    }
    
    response = await client.post("/v1/approve", json=request_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_submit_feedback(client):
    """Test feedback endpoint."""
    # Create and complete a job first
    plan_response = await client.post("/v1/plan", json={
        "user_id": "test_user",
        "query": "Test query",
        "constraints": {}
    })
    
    job_id = plan_response.json()["job_id"]
    
    # Submit feedback
    request_data = {
        "job_id": job_id,
        "rating": 5,
        "comment": "Great job!",
        "helpful_aspects": ["speed", "accuracy"],
        "improvement_areas": []
    }
    
    response = await client.post("/v1/feedback", json=request_data)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_validation_error(client):
    """Test Pydantic validation."""
    # Missing required field
    request_data = {
        "query": "Test query",
        # Missing user_id
    }
    
    response = await client.post("/v1/plan", json=request_data)
    
    assert response.status_code == 422
    data = response.json()
    
    assert "error" in data
    assert data["error"] == "ValidationError"


@pytest.mark.asyncio
async def test_concurrent_jobs(client):
    """Test multiple concurrent jobs."""
    # Create 10 jobs simultaneously
    tasks = [
        client.post("/v1/plan", json={
            "user_id": f"user_{i}",
            "query": f"Test query {i}",
            "constraints": {}
        })
        for i in range(10)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r.status_code == 202 for r in responses)
    
    # All should have unique job IDs
    job_ids = [r.json()["job_id"] for r in responses]
    assert len(set(job_ids)) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
