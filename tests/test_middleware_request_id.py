import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.request_logging import RequestLoggingMiddleware
from app.core.request_context import get_request_id

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)

@app.get("/test-request-id")
async def test_endpoint():
    request_id = get_request_id()
    return {"request_id": request_id}

client = TestClient(app)

def test_request_id_generated_if_missing():
    response = client.get("/test-request-id")
    assert response.status_code == 200
    
    # Check if request_id is in response headers
    assert "x-request-id" in response.headers
    request_id_header = response.headers["x-request-id"]
    
    # Check if the endpoint got the same request_id from context
    data = response.json()
    assert data["request_id"] == request_id_header
    assert len(request_id_header) > 10  # It's a uuid

def test_request_id_reused_if_provided():
    custom_id = "test-custom-id-12345"
    response = client.get("/test-request-id", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    
    assert response.headers["x-request-id"] == custom_id
    data = response.json()
    assert data["request_id"] == custom_id

def test_request_id_sanitized_if_too_long():
    very_long_id = "a" * 100
    response = client.get("/test-request-id", headers={"X-Request-ID": very_long_id})
    assert response.status_code == 200
    
    # We truncate to 64 chars
    expected_id = "a" * 64
    assert response.headers["x-request-id"] == expected_id
    data = response.json()
    assert data["request_id"] == expected_id
