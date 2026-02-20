"""
Integration tests for FastAPI main application.

Tests the complete application startup, endpoint functionality,
and service integration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock the Config and ServiceContainer before importing main
with patch('main.Config'), patch('main.ServiceContainer'):
    from main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_service_container():
    """Create mock service container."""
    container = Mock()
    
    # Mock health check
    container.health_check.return_value = {
        "firestore": "connected",
        "llm": "available",
        "memory_engine": "ready"
    }
    
    # Mock response pipeline
    mock_pipeline = Mock()
    container.get_response_pipeline.return_value = mock_pipeline
    
    return container


def test_health_check_before_initialization(client):
    """Test health check endpoint before service initialization."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "initializing"
    assert data["service"] == "AI Waifu Backend"
    assert data["version"] == "1.0.0"


def test_health_check_with_services(client, mock_service_container):
    """Test health check endpoint with initialized services."""
    # Inject mock service container
    import main
    main.service_container = mock_service_container
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Waifu Backend"
    assert "services" in data
    assert data["services"]["firestore"] == "connected"
    assert data["services"]["llm"] == "available"
    assert data["services"]["memory_engine"] == "ready"
    
    # Cleanup
    main.service_container = None


def test_health_check_degraded_services(client, mock_service_container):
    """Test health check endpoint with degraded services."""
    # Mock degraded health status
    mock_service_container.health_check.return_value = {
        "firestore": "error: connection failed",
        "llm": "available",
        "memory_engine": "ready"
    }
    
    # Inject mock service container
    import main
    main.service_container = mock_service_container
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    
    # Cleanup
    main.service_container = None


def test_chat_endpoint_before_initialization(client):
    """Test chat endpoint before service initialization."""
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "Hello!",
        "platform": "web"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "starting up" in data["reply"].lower()
    assert data["affection_level"] == 10
    assert data["mood"] == "neutral"


@pytest.mark.asyncio
async def test_chat_endpoint_with_services(client, mock_service_container):
    """Test chat endpoint with initialized services."""
    from models import ChatResponse
    from unittest.mock import AsyncMock
    
    # Mock response pipeline with async method
    mock_pipeline = mock_service_container.get_response_pipeline.return_value
    mock_pipeline.process_message = AsyncMock(return_value=ChatResponse(
        reply="H-hey! Don't get the wrong idea, baka!",
        affection_level=25,
        mood="flustered"
    ))
    
    # Inject mock service container
    import main
    main.service_container = mock_service_container
    
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "You're cute!",
        "platform": "web"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "H-hey! Don't get the wrong idea, baka!"
    assert data["affection_level"] == 25
    assert data["mood"] == "flustered"
    
    # Verify pipeline was called correctly
    mock_pipeline.process_message.assert_called_once()
    call_args = mock_pipeline.process_message.call_args
    assert call_args[1]["user_id"] == "test_user"
    assert call_args[1]["message"] == "You're cute!"
    assert call_args[1]["platform"] == "web"
    
    # Cleanup
    main.service_container = None


def test_chat_endpoint_invalid_request(client):
    """Test chat endpoint with invalid request data."""
    response = client.post("/chat", json={
        "user_id": "",  # Invalid: empty user_id
        "message": "Hello!",
        "platform": "web"
    })
    
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_invalid_platform(client):
    """Test chat endpoint with invalid platform."""
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "Hello!",
        "platform": "invalid_platform"  # Invalid platform
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_chat_endpoint_error_handling(client, mock_service_container):
    """Test chat endpoint error handling."""
    from unittest.mock import AsyncMock
    
    # Mock response pipeline to raise exception
    mock_pipeline = mock_service_container.get_response_pipeline.return_value
    mock_pipeline.process_message = AsyncMock(side_effect=Exception("Test error"))
    
    # Inject mock service container
    import main
    main.service_container = mock_service_container
    
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "Hello!",
        "platform": "web"
    })
    
    # Should return graceful error response
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "went wrong" in data["reply"].lower()
    assert data["affection_level"] == 10
    assert data["mood"] == "neutral"
    
    # Cleanup
    main.service_container = None


def test_cors_middleware_configured(client):
    """Test that CORS middleware is properly configured."""
    response = client.options("/health", headers={
        "Origin": "http://localhost:4200",
        "Access-Control-Request-Method": "GET"
    })
    
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_api_metadata():
    """Test API metadata is correctly configured."""
    assert app.title == "AI Waifu Cross-Platform System"
    assert app.version == "1.0.0"
    assert "Mimi" in app.description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
