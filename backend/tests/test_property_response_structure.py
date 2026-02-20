"""
Property-based tests for response structure completeness.

Feature: ai-waifu-cross-platform
Property 2: Response Structure Completeness

**Validates: Requirements 1.3**

For any valid chat request, the response should contain reply, affection_level,
and mood fields.
"""

from hypothesis import given, strategies as st
import pytest
from fastapi.testclient import TestClient
from main import app

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
def test_response_contains_all_required_fields(request_data):
    """
    Property 2: Response Structure Completeness
    
    For any valid chat request, the response should contain reply,
    affection_level, and mood fields.
    
    **Validates: Requirements 1.3**
    """
    response = client.post("/chat", json=request_data)
    
    # Valid requests should return 200
    assert response.status_code == 200, \
        f"Expected 200 status code, got {response.status_code}"
    
    # Parse response JSON
    data = response.json()
    
    # Verify all required fields are present
    assert "reply" in data, \
        "Response missing required field 'reply'"
    assert "affection_level" in data, \
        "Response missing required field 'affection_level'"
    assert "mood" in data, \
        "Response missing required field 'mood'"


@given(request_data=valid_chat_request)
@pytest.mark.property_test
def test_response_reply_is_string(request_data):
    """
    Property 2: Response Structure Completeness (reply type)
    
    For any valid chat request, the response reply field should be a string.
    
    **Validates: Requirements 1.3**
    """
    response = client.post("/chat", json=request_data)
    
    assert response.status_code == 200, \
        f"Expected 200 status code, got {response.status_code}"
    
    data = response.json()
    
    # Verify reply is a string
    assert isinstance(data["reply"], str), \
        f"Expected reply to be string, got {type(data['reply'])}"
    
    # Verify reply is not empty
    assert len(data["reply"]) > 0, \
        "Expected reply to be non-empty string"


@given(request_data=valid_chat_request)
@pytest.mark.property_test
def test_response_affection_level_is_valid_integer(request_data):
    """
    Property 2: Response Structure Completeness (affection_level type and range)
    
    For any valid chat request, the response affection_level field should be
    an integer between 0 and 100 (inclusive).
    
    **Validates: Requirements 1.3**
    """
    response = client.post("/chat", json=request_data)
    
    assert response.status_code == 200, \
        f"Expected 200 status code, got {response.status_code}"
    
    data = response.json()
    
    # Verify affection_level is an integer
    assert isinstance(data["affection_level"], int), \
        f"Expected affection_level to be int, got {type(data['affection_level'])}"
    
    # Verify affection_level is in valid range (0-100)
    assert 0 <= data["affection_level"] <= 100, \
        f"Expected affection_level in range [0, 100], got {data['affection_level']}"


@given(request_data=valid_chat_request)
@pytest.mark.property_test
def test_response_mood_is_string(request_data):
    """
    Property 2: Response Structure Completeness (mood type)
    
    For any valid chat request, the response mood field should be a string.
    
    **Validates: Requirements 1.3**
    """
    response = client.post("/chat", json=request_data)
    
    assert response.status_code == 200, \
        f"Expected 200 status code, got {response.status_code}"
    
    data = response.json()
    
    # Verify mood is a string
    assert isinstance(data["mood"], str), \
        f"Expected mood to be string, got {type(data['mood'])}"
    
    # Verify mood is not empty
    assert len(data["mood"]) > 0, \
        "Expected mood to be non-empty string"


@given(request_data=valid_chat_request)
@pytest.mark.property_test
def test_response_has_no_extra_required_fields(request_data):
    """
    Property 2: Response Structure Completeness (field count)
    
    For any valid chat request, the response should contain exactly the
    required fields (reply, affection_level, mood) and no additional
    required fields.
    
    **Validates: Requirements 1.3**
    """
    response = client.post("/chat", json=request_data)
    
    assert response.status_code == 200, \
        f"Expected 200 status code, got {response.status_code}"
    
    data = response.json()
    
    # Verify response has at least the required fields
    required_fields = {"reply", "affection_level", "mood"}
    actual_fields = set(data.keys())
    
    # Check that all required fields are present
    missing_fields = required_fields - actual_fields
    assert len(missing_fields) == 0, \
        f"Response missing required fields: {missing_fields}"
    
    # Note: Extra fields are allowed, we just verify required ones are present
    assert required_fields.issubset(actual_fields), \
        f"Expected required fields {required_fields} to be subset of {actual_fields}"


@given(
    user_id=st.text(min_size=1, max_size=100),
    message=st.text(min_size=1, max_size=1000),
    platform=st.sampled_from(["web", "discord"])
)
@pytest.mark.property_test
def test_response_structure_consistent_across_platforms(user_id, message, platform):
    """
    Property 2: Response Structure Completeness (platform consistency)
    
    For any valid chat request from any platform (web or discord), the
    response structure should be consistent and contain all required fields.
    
    **Validates: Requirements 1.3**
    """
    request_data = {
        "user_id": user_id,
        "message": message,
        "platform": platform
    }
    
    response = client.post("/chat", json=request_data)
    
    assert response.status_code == 200, \
        f"Expected 200 status code for platform '{platform}', got {response.status_code}"
    
    data = response.json()
    
    # Verify all required fields are present regardless of platform
    assert "reply" in data, \
        f"Response from platform '{platform}' missing 'reply' field"
    assert "affection_level" in data, \
        f"Response from platform '{platform}' missing 'affection_level' field"
    assert "mood" in data, \
        f"Response from platform '{platform}' missing 'mood' field"
    
    # Verify field types are correct
    assert isinstance(data["reply"], str), \
        f"Platform '{platform}': Expected reply to be string"
    assert isinstance(data["affection_level"], int), \
        f"Platform '{platform}': Expected affection_level to be int"
    assert isinstance(data["mood"], str), \
        f"Platform '{platform}': Expected mood to be string"
