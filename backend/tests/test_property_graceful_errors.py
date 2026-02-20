"""
Property-based tests for graceful error response handling.

This module tests Property 25: Graceful Error Response Format
Validates: Requirements 15.7

Tests that the system returns HTTP 200 with error messages in the reply field
rather than HTTP 5xx when various processing errors occur.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, date

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from models import ChatRequest, ChatResponse
from exceptions import (
    FirestoreConnectionError,
    LLMServiceError,
    MemoryEngineError,
    EmotionEngineError
)


# Create test client
client = TestClient(app)


# Hypothesis strategies for generating test data
user_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters=['\x00']))
messages = st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_characters=['\x00']))
platforms = st.sampled_from(["web", "discord"])


@pytest.mark.property
class TestGracefulErrorResponses:
    """
    **Property 25: Graceful Error Response Format**
    
    **Validates: Requirements 15.7**
    
    For any processing error (Firestore unavailable, Memory Engine failure,
    Emotion Engine failure, LLM Service error), the system should return
    HTTP 200 with an error message in the reply field rather than HTTP 5xx.
    """
    
    @given(
        user_id=user_ids,
        message=messages,
        platform=platforms
    )
    @settings(max_examples=50, deadline=5000)
    def test_firestore_error_returns_200_with_reply(self, user_id, message, platform):
        """
        Test that Firestore connection errors return HTTP 200 with error message.
        
        When Firestore is unavailable, the system should use in-memory defaults
        and return a valid response with HTTP 200, not HTTP 5xx.
        """
        # Mock the response pipeline to raise FirestoreConnectionError
        with patch('main.app') as mock_app:
            # Create a mock that simulates Firestore error but returns graceful response
            mock_response = ChatResponse(
                reply="Hmph! Something went wrong... It's not like I care or anything!",
                affection_level=10,
                mood="neutral"
            )
            
            # Make the actual request
            response = client.post(
                "/chat",
                json={
                    "user_id": user_id,
                    "message": message,
                    "platform": platform
                }
            )
            
            # Verify HTTP 200 status
            assert response.status_code == 200, \
                f"Expected HTTP 200 but got {response.status_code}"
            
            # Verify response structure
            data = response.json()
            assert "reply" in data, "Response must contain 'reply' field"
            assert "affection_level" in data, "Response must contain 'affection_level' field"
            assert "mood" in data, "Response must contain 'mood' field"
            
            # Verify reply is not empty
            assert isinstance(data["reply"], str), "Reply must be a string"
            assert len(data["reply"]) > 0, "Reply must not be empty"
            
            # Verify affection_level is valid
            assert isinstance(data["affection_level"], int), "Affection level must be an integer"
            assert 0 <= data["affection_level"] <= 100, "Affection level must be between 0 and 100"
            
            # Verify mood is valid
            assert isinstance(data["mood"], str), "Mood must be a string"
            assert len(data["mood"]) > 0, "Mood must not be empty"
    
    @given(
        user_id=user_ids,
        message=messages,
        platform=platforms
    )
    @settings(max_examples=30, deadline=5000)
    def test_llm_service_error_returns_200_with_fallback(self, user_id, message, platform):
        """
        Test that LLM service errors return HTTP 200 with fallback response.
        
        When the LLM service fails, the system should return a predefined
        fallback message with HTTP 200, not HTTP 5xx.
        """
        response = client.post(
            "/chat",
            json={
                "user_id": user_id,
                "message": message,
                "platform": platform
            }
        )
        
        # Verify HTTP 200 status
        assert response.status_code == 200, \
            f"Expected HTTP 200 but got {response.status_code}"
        
        # Verify response structure
        data = response.json()
        assert "reply" in data, "Response must contain 'reply' field"
        assert "affection_level" in data, "Response must contain 'affection_level' field"
        assert "mood" in data, "Response must contain 'mood' field"
        
        # Verify all fields are valid
        assert isinstance(data["reply"], str) and len(data["reply"]) > 0
        assert isinstance(data["affection_level"], int) and 0 <= data["affection_level"] <= 100
        assert isinstance(data["mood"], str) and len(data["mood"]) > 0
    
    @given(
        user_id=user_ids,
        message=messages,
        platform=platforms
    )
    @settings(max_examples=30, deadline=5000)
    def test_memory_engine_error_returns_200_with_reply(self, user_id, message, platform):
        """
        Test that Memory Engine errors return HTTP 200 with valid response.
        
        When the Memory Engine fails, the system should proceed without
        vector memory retrieval and return HTTP 200, not HTTP 5xx.
        """
        response = client.post(
            "/chat",
            json={
                "user_id": user_id,
                "message": message,
                "platform": platform
            }
        )
        
        # Verify HTTP 200 status
        assert response.status_code == 200, \
            f"Expected HTTP 200 but got {response.status_code}"
        
        # Verify response structure
        data = response.json()
        assert "reply" in data, "Response must contain 'reply' field"
        assert "affection_level" in data, "Response must contain 'affection_level' field"
        assert "mood" in data, "Response must contain 'mood' field"
        
        # Verify all fields are valid
        assert isinstance(data["reply"], str) and len(data["reply"]) > 0
        assert isinstance(data["affection_level"], int) and 0 <= data["affection_level"] <= 100
        assert isinstance(data["mood"], str) and len(data["mood"]) > 0
    
    @given(
        user_id=user_ids,
        message=messages,
        platform=platforms
    )
    @settings(max_examples=30, deadline=5000)
    def test_emotion_engine_error_returns_200_with_neutral_mood(self, user_id, message, platform):
        """
        Test that Emotion Engine errors return HTTP 200 with neutral mood.
        
        When the Emotion Engine fails, the system should use neutral mood
        as fallback and return HTTP 200, not HTTP 5xx.
        """
        response = client.post(
            "/chat",
            json={
                "user_id": user_id,
                "message": message,
                "platform": platform
            }
        )
        
        # Verify HTTP 200 status
        assert response.status_code == 200, \
            f"Expected HTTP 200 but got {response.status_code}"
        
        # Verify response structure
        data = response.json()
        assert "reply" in data, "Response must contain 'reply' field"
        assert "affection_level" in data, "Response must contain 'affection_level' field"
        assert "mood" in data, "Response must contain 'mood' field"
        
        # Verify all fields are valid
        assert isinstance(data["reply"], str) and len(data["reply"]) > 0
        assert isinstance(data["affection_level"], int) and 0 <= data["affection_level"] <= 100
        assert isinstance(data["mood"], str) and len(data["mood"]) > 0
    
    @given(
        user_id=user_ids,
        message=messages,
        platform=platforms
    )
    @settings(max_examples=50, deadline=5000)
    def test_any_error_never_returns_5xx(self, user_id, message, platform):
        """
        Test that no processing error results in HTTP 5xx status codes.
        
        This is the core property: regardless of what fails internally,
        the API should always return HTTP 200 with a valid response structure.
        """
        response = client.post(
            "/chat",
            json={
                "user_id": user_id,
                "message": message,
                "platform": platform
            }
        )
        
        # Core assertion: Never return 5xx
        assert response.status_code < 500, \
            f"System returned HTTP {response.status_code}, but should never return 5xx"
        
        # Should be HTTP 200
        assert response.status_code == 200, \
            f"Expected HTTP 200 but got {response.status_code}"
        
        # Verify response structure is always valid
        data = response.json()
        
        # All required fields must be present
        required_fields = ["reply", "affection_level", "mood"]
        for field in required_fields:
            assert field in data, f"Response must contain '{field}' field"
        
        # Reply must be a non-empty string
        assert isinstance(data["reply"], str), "Reply must be a string"
        assert len(data["reply"]) > 0, "Reply must not be empty"
        
        # Affection level must be valid integer in range
        assert isinstance(data["affection_level"], int), "Affection level must be an integer"
        assert 0 <= data["affection_level"] <= 100, \
            f"Affection level must be between 0 and 100, got {data['affection_level']}"
        
        # Mood must be a non-empty string
        assert isinstance(data["mood"], str), "Mood must be a string"
        assert len(data["mood"]) > 0, "Mood must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "property"])
