"""
Tests for session context management in Response Pipeline.

Tests verify:
- update_session_context() maintains last 10 messages (5 exchanges)
- clear_inactive_sessions() removes sessions after 30-minute timeout
- Session context isolation between users
- Timestamp updates on activity

Requirements: 14.1, 14.2, 14.3
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from models import Message
from modules.response_pipeline import ResponsePipeline


@pytest.fixture
def mock_modules():
    """Create mock instances of all required modules."""
    return {
        'firestore_client': Mock(),
        'affection_decay_engine': Mock(),
        'interaction_streak_system': Mock(),
        'emotion_engine': Mock(),
        'memory_engine': Mock(),
        'personality_system': Mock(),
        'relationship_engine': Mock(),
        'attachment_style_engine': Mock(),
        'temperature_scaling_system': Mock(),
        'callback_memory_system': Mock(),
        'llm_service': Mock()
    }


@pytest.fixture
def pipeline(mock_modules):
    """Create ResponsePipeline instance with mocked modules."""
    return ResponsePipeline(**mock_modules)


class TestUpdateSessionContext:
    """Tests for update_session_context() method."""
    
    def test_creates_new_session_context(self, pipeline):
        """Test that new session context is created for new user."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        pipeline.update_session_context(user_id, message)
        
        assert user_id in pipeline.session_contexts
        assert len(pipeline.session_contexts[user_id]["messages"]) == 1
        assert pipeline.session_contexts[user_id]["messages"][0] == message
    
    def test_appends_messages_to_existing_context(self, pipeline):
        """Test that messages are appended to existing session."""
        user_id = "user123"
        msg1 = Message(role="user", content="Hello!")
        msg2 = Message(role="assistant", content="Hi there!")
        msg3 = Message(role="user", content="How are you?")
        
        pipeline.update_session_context(user_id, msg1)
        pipeline.update_session_context(user_id, msg2)
        pipeline.update_session_context(user_id, msg3)
        
        assert len(pipeline.session_contexts[user_id]["messages"]) == 3
        assert pipeline.session_contexts[user_id]["messages"][0] == msg1
        assert pipeline.session_contexts[user_id]["messages"][1] == msg2
        assert pipeline.session_contexts[user_id]["messages"][2] == msg3
    
    def test_keeps_last_10_messages_only(self, pipeline):
        """Test that only last 10 messages (5 exchanges) are kept."""
        user_id = "user123"
        
        # Add 15 messages
        for i in range(15):
            role = "user" if i % 2 == 0 else "assistant"
            message = Message(role=role, content=f"Message {i}")
            pipeline.update_session_context(user_id, message)
        
        # Should only keep last 10
        messages = pipeline.session_contexts[user_id]["messages"]
        assert len(messages) == 10
        
        # Verify it's the last 10 messages (5-14)
        assert messages[0].content == "Message 5"
        assert messages[-1].content == "Message 14"
    
    def test_updates_last_activity_timestamp(self, pipeline):
        """Test that last_activity timestamp is updated on each message."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        before = datetime.now()
        pipeline.update_session_context(user_id, message)
        after = datetime.now()
        
        last_activity = pipeline.session_contexts[user_id]["last_activity"]
        assert before <= last_activity <= after
    
    def test_session_isolation_between_users(self, pipeline):
        """Test that different users have isolated session contexts."""
        user1 = "user123"
        user2 = "user456"
        
        msg1 = Message(role="user", content="User 1 message")
        msg2 = Message(role="user", content="User 2 message")
        
        pipeline.update_session_context(user1, msg1)
        pipeline.update_session_context(user2, msg2)
        
        assert len(pipeline.session_contexts[user1]["messages"]) == 1
        assert len(pipeline.session_contexts[user2]["messages"]) == 1
        assert pipeline.session_contexts[user1]["messages"][0].content == "User 1 message"
        assert pipeline.session_contexts[user2]["messages"][0].content == "User 2 message"


class TestGetSessionContext:
    """Tests for get_session_context() method."""
    
    def test_returns_empty_list_for_new_user(self, pipeline):
        """Test that empty list is returned for user with no context."""
        user_id = "new_user"
        context = pipeline.get_session_context(user_id)
        
        assert context == []
    
    def test_returns_messages_for_existing_user(self, pipeline):
        """Test that messages are returned for user with context."""
        user_id = "user123"
        msg1 = Message(role="user", content="Hello!")
        msg2 = Message(role="assistant", content="Hi!")
        
        pipeline.update_session_context(user_id, msg1)
        pipeline.update_session_context(user_id, msg2)
        
        context = pipeline.get_session_context(user_id)
        
        assert len(context) == 2
        assert context[0] == msg1
        assert context[1] == msg2


class TestClearInactiveSessions:
    """Tests for clear_inactive_sessions() method."""
    
    def test_removes_sessions_after_timeout(self, pipeline):
        """Test that sessions inactive for 30+ minutes are removed."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        # Create session
        pipeline.update_session_context(user_id, message)
        
        # Manually set last_activity to 31 minutes ago
        pipeline.session_contexts[user_id]["last_activity"] = datetime.now() - timedelta(minutes=31)
        
        # Clear inactive sessions
        pipeline.clear_inactive_sessions(timeout_minutes=30)
        
        # Session should be removed
        assert user_id not in pipeline.session_contexts
    
    def test_keeps_active_sessions(self, pipeline):
        """Test that sessions active within timeout are kept."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        # Create session
        pipeline.update_session_context(user_id, message)
        
        # Manually set last_activity to 29 minutes ago (within timeout)
        pipeline.session_contexts[user_id]["last_activity"] = datetime.now() - timedelta(minutes=29)
        
        # Clear inactive sessions
        pipeline.clear_inactive_sessions(timeout_minutes=30)
        
        # Session should still exist
        assert user_id in pipeline.session_contexts
    
    def test_clears_multiple_inactive_sessions(self, pipeline):
        """Test that multiple inactive sessions are cleared."""
        user1 = "user123"
        user2 = "user456"
        user3 = "user789"
        
        # Create sessions
        for user_id in [user1, user2, user3]:
            message = Message(role="user", content="Hello!")
            pipeline.update_session_context(user_id, message)
        
        # Set user1 and user2 as inactive, user3 as active
        pipeline.session_contexts[user1]["last_activity"] = datetime.now() - timedelta(minutes=31)
        pipeline.session_contexts[user2]["last_activity"] = datetime.now() - timedelta(minutes=35)
        pipeline.session_contexts[user3]["last_activity"] = datetime.now() - timedelta(minutes=5)
        
        # Clear inactive sessions
        pipeline.clear_inactive_sessions(timeout_minutes=30)
        
        # Only user3 should remain
        assert user1 not in pipeline.session_contexts
        assert user2 not in pipeline.session_contexts
        assert user3 in pipeline.session_contexts
    
    def test_clears_callback_count_with_session(self, pipeline):
        """Test that callback count is cleared when session is removed."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        # Create session and set callback count
        pipeline.update_session_context(user_id, message)
        pipeline.session_callback_count[user_id] = 1
        
        # Set as inactive
        pipeline.session_contexts[user_id]["last_activity"] = datetime.now() - timedelta(minutes=31)
        
        # Clear inactive sessions
        pipeline.clear_inactive_sessions(timeout_minutes=30)
        
        # Both session and callback count should be removed
        assert user_id not in pipeline.session_contexts
        assert user_id not in pipeline.session_callback_count
    
    def test_custom_timeout_duration(self, pipeline):
        """Test that custom timeout duration is respected."""
        user_id = "user123"
        message = Message(role="user", content="Hello!")
        
        # Create session
        pipeline.update_session_context(user_id, message)
        
        # Set last_activity to 11 minutes ago
        pipeline.session_contexts[user_id]["last_activity"] = datetime.now() - timedelta(minutes=11)
        
        # Clear with 10-minute timeout
        pipeline.clear_inactive_sessions(timeout_minutes=10)
        
        # Session should be removed
        assert user_id not in pipeline.session_contexts
    
    def test_no_error_when_no_sessions_exist(self, pipeline):
        """Test that clearing inactive sessions works when no sessions exist."""
        # Should not raise any errors
        pipeline.clear_inactive_sessions(timeout_minutes=30)
        
        assert len(pipeline.session_contexts) == 0


class TestSessionContextIntegration:
    """Integration tests for session context management."""
    
    def test_five_exchanges_equals_ten_messages(self, pipeline):
        """Test that 5 exchanges (user + assistant pairs) equals 10 messages."""
        user_id = "user123"
        
        # Simulate 5 exchanges
        for i in range(5):
            user_msg = Message(role="user", content=f"User message {i}")
            assistant_msg = Message(role="assistant", content=f"Assistant message {i}")
            pipeline.update_session_context(user_id, user_msg)
            pipeline.update_session_context(user_id, assistant_msg)
        
        context = pipeline.get_session_context(user_id)
        assert len(context) == 10
    
    def test_sixth_exchange_removes_first_exchange(self, pipeline):
        """Test that adding 6th exchange removes the 1st exchange."""
        user_id = "user123"
        
        # Add 6 exchanges (12 messages)
        for i in range(6):
            user_msg = Message(role="user", content=f"User message {i}")
            assistant_msg = Message(role="assistant", content=f"Assistant message {i}")
            pipeline.update_session_context(user_id, user_msg)
            pipeline.update_session_context(user_id, assistant_msg)
        
        context = pipeline.get_session_context(user_id)
        
        # Should only have last 10 messages (exchanges 1-5)
        assert len(context) == 10
        assert context[0].content == "User message 1"  # First exchange removed
        assert context[-1].content == "Assistant message 5"
    
    def test_context_persists_across_multiple_updates(self, pipeline):
        """Test that context persists correctly across multiple updates."""
        user_id = "user123"
        
        # Add messages over time
        msg1 = Message(role="user", content="First")
        pipeline.update_session_context(user_id, msg1)
        
        msg2 = Message(role="assistant", content="Second")
        pipeline.update_session_context(user_id, msg2)
        
        # Get context
        context1 = pipeline.get_session_context(user_id)
        assert len(context1) == 2
        
        # Add more messages
        msg3 = Message(role="user", content="Third")
        pipeline.update_session_context(user_id, msg3)
        
        # Get context again
        context2 = pipeline.get_session_context(user_id)
        assert len(context2) == 3
        assert context2[0] == msg1
        assert context2[1] == msg2
        assert context2[2] == msg3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
