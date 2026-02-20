"""
Property-based tests for request validation.

Feature: ai-waifu-cross-platform
Property 1: Request Validation

**Validates: Requirements 1.2**

For any chat request, if it contains user_id, message, and platform fields,
then the API should accept it; if any required field is missing, the API
should reject it with a validation error.
"""

from hypothesis import given, strategies as st
import pytest
from fastapi.testclient import TestClient
from main import app
from models import ChatRequest

# Initialize test client
client = TestClient(app)


# Strategy for generating valid ChatRequest payloads
valid_chat_request = st.fixed_dictionaries({
    "user_id": st.text(min_size=1, max_size=100),
    "message": st.text(min_size=1, max_size=1000),
    "platform": st.sampled_from(["web", "discord"])
})


@given(request_data=valid_chat_request)
@pytest.mark.property_test
def test_valid_request_acceptance(request_data):
    """
    Property 1: Request Validation (Valid Requests)
    
    For any valid chat request containing user_id, message, and platform fields,
    the API should accept it and return a 200 status code.
    """
    response = client.post("/chat", json=request_data)
    
    # Valid requests should be accepted (200 OK)
    assert response.status_code == 200, \
        f"Expected 200 for valid request, got {response.status_code}"
    
    # Response should contain required fields
    data = response.json()
    assert "reply" in data, "Response missing 'reply' field"
    assert "affection_level" in data, "Response missing 'affection_level' field"
    assert "mood" in data, "Response missing 'mood' field"


@given(
    user_id=st.one_of(st.none(), st.just("")),
    message=st.text(min_size=1, max_size=1000),
    platform=st.sampled_from(["web", "discord"])
)
@pytest.mark.property_test
def test_missing_user_id_rejection(user_id, message, platform):
    """
    Property 1: Request Validation (Missing user_id)
    
    For any request with missing or empty user_id, the API should reject it
    with a 422 validation error.
    """
    request_data = {
        "message": message,
        "platform": platform
    }
    
    # Add user_id only if not None
    if user_id is not None:
        request_data["user_id"] = user_id
    
    response = client.post("/chat", json=request_data)
    
    # Invalid requests should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for missing/empty user_id, got {response.status_code}"


@given(
    user_id=st.text(min_size=1, max_size=100),
    message=st.one_of(st.none(), st.just("")),
    platform=st.sampled_from(["web", "discord"])
)
@pytest.mark.property_test
def test_missing_message_rejection(user_id, message, platform):
    """
    Property 1: Request Validation (Missing message)
    
    For any request with missing or empty message, the API should reject it
    with a 422 validation error.
    """
    request_data = {
        "user_id": user_id,
        "platform": platform
    }
    
    # Add message only if not None
    if message is not None:
        request_data["message"] = message
    
    response = client.post("/chat", json=request_data)
    
    # Invalid requests should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for missing/empty message, got {response.status_code}"


@given(
    user_id=st.text(min_size=1, max_size=100),
    message=st.text(min_size=1, max_size=1000),
    invalid_platform=st.text().filter(lambda x: x not in ["web", "discord"])
)
@pytest.mark.property_test
def test_invalid_platform_rejection(user_id, message, invalid_platform):
    """
    Property 1: Request Validation (Invalid platform)
    
    For any request with a platform value other than "web" or "discord",
    the API should reject it with a 422 validation error.
    """
    request_data = {
        "user_id": user_id,
        "message": message,
        "platform": invalid_platform
    }
    
    response = client.post("/chat", json=request_data)
    
    # Invalid platform should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for invalid platform '{invalid_platform}', got {response.status_code}"


@given(
    user_id=st.text(min_size=1, max_size=100),
    message=st.text(min_size=1, max_size=1000)
)
@pytest.mark.property_test
def test_missing_platform_rejection(user_id, message):
    """
    Property 1: Request Validation (Missing platform)
    
    For any request with missing platform field, the API should reject it
    with a 422 validation error.
    """
    request_data = {
        "user_id": user_id,
        "message": message
        # platform intentionally omitted
    }
    
    response = client.post("/chat", json=request_data)
    
    # Missing platform should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for missing platform, got {response.status_code}"


@pytest.mark.property_test
def test_completely_empty_request():
    """
    Property 1: Request Validation (Empty request)
    
    For a completely empty request, the API should reject it with a 422
    validation error.
    """
    response = client.post("/chat", json={})
    
    # Empty request should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for empty request, got {response.status_code}"


@pytest.mark.property_test
def test_null_request():
    """
    Property 1: Request Validation (Null request)
    
    For a null request body, the API should reject it with a 422
    validation error.
    """
    response = client.post("/chat", json=None)
    
    # Null request should be rejected with 422
    assert response.status_code == 422, \
        f"Expected 422 for null request, got {response.status_code}"
