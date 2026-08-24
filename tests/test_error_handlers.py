import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from app.middleware.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

class DummyItem(BaseModel):
    name: str

@app.get("/404-error")
async def error_404():
    raise HTTPException(status_code=404, detail="Not found custom")

@app.post("/422-error")
async def error_422(item: DummyItem):
    return item

@app.get("/500-error")
async def error_500():
    raise ValueError("Something unexpected broke")

client = TestClient(app, raise_server_exceptions=False)

def test_404_error_contains_request_id():
    response = client.get("/404-error")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "HTTP_404"
    assert "request_id" in data
    assert data["request_id"] == response.headers.get("x-request-id")

def test_422_error_contains_request_id():
    response = client.post("/422-error", json={"invalid": "payload"})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "request_id" in data
    assert data["request_id"] == response.headers.get("x-request-id")

def test_500_error_contains_request_id():
    response = client.get("/500-error")
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INTERNAL_SERVER_ERROR"
    assert data["message"] == "Internal server error"
    assert "request_id" in data
    assert data["request_id"] == response.headers.get("x-request-id")
