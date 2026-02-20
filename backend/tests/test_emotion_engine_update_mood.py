"""
Test for EmotionEngine.update_mood method.

This test verifies that the update_mood method correctly updates
Firestore with new mood, affection level, and emotional memory.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from modules.emotion_engine import EmotionEngine
from models import UserData, EmotionalMemoryEntry


@patch('modules.firestore_operations.get_user_data')
@patch('modules.firestore_operations.update_user_data')
def test_update_mood_updates_firestore(mock_update_user_data, mock_get_user_data):
    """Test that update_mood correctly updates mood, affection, and emotional memory."""
    # Create mock Firestore client
    mock_firestore = Mock()
    
    # Create EmotionEngine instance
    engine = EmotionEngine(mock_firestore)
    
    # Create mock user data
    mock_user_data = UserData(
        user_id="test_user",
        affection_level=50,
        mood="neutral",
        emotional_memory=[]
    )
    
    mock_get_user_data.return_value = mock_user_data
    
    # Call update_mood
    engine.update_mood("test_user", "jealous", -2)
    
    # Verify get_user_data was called
    mock_get_user_data.assert_called_once_with(mock_firestore, "test_user")
    
    # Verify update_user_data was called
    assert mock_update_user_data.called
    call_args = mock_update_user_data.call_args
    
    # Check the arguments
    assert call_args[0][0] == mock_firestore
    assert call_args[0][1] == "test_user"
    
    updates = call_args[0][2]
    assert updates["mood"] == "jealous"
    assert updates["affection_level"] == 48  # 50 + (-2)
    assert len(updates["emotional_memory"]) == 1
    
    # Verify emotional memory entry
    emotional_entry = updates["emotional_memory"][0]
    assert isinstance(emotional_entry, EmotionalMemoryEntry)
    assert emotional_entry.event_type == "jealous"
    assert emotional_entry.mood_change == "jealous"
    assert emotional_entry.affection_delta == -2


@patch('modules.firestore_operations.get_user_data')
@patch('modules.firestore_operations.update_user_data')
def test_update_mood_respects_affection_bounds(mock_update_user_data, mock_get_user_data):
    """Test that update_mood keeps affection level within 0-100 range."""
    mock_firestore = Mock()
    engine = EmotionEngine(mock_firestore)
    
    # Test upper bound
    mock_user_high = UserData(
        user_id="test_user_high",
        affection_level=98,
        mood="neutral",
        emotional_memory=[]
    )
    
    mock_get_user_data.return_value = mock_user_high
    
    engine.update_mood("test_user_high", "happy", 5)
    
    call_args = mock_update_user_data.call_args
    updates = call_args[0][2]
    assert updates["affection_level"] == 100  # Capped at 100
    
    # Test lower bound
    mock_user_low = UserData(
        user_id="test_user_low",
        affection_level=1,
        mood="neutral",
        emotional_memory=[]
    )
    
    mock_get_user_data.return_value = mock_user_low
    mock_update_user_data.reset_mock()
    
    engine.update_mood("test_user_low", "angry", -5)
    
    call_args = mock_update_user_data.call_args
    updates = call_args[0][2]
    assert updates["affection_level"] == 0  # Capped at 0


@patch('modules.firestore_operations.get_user_data')
@patch('modules.firestore_operations.update_user_data')
def test_update_mood_handles_nonexistent_user(mock_update_user_data, mock_get_user_data):
    """Test that update_mood gracefully handles nonexistent users."""
    mock_firestore = Mock()
    engine = EmotionEngine(mock_firestore)
    
    mock_get_user_data.return_value = None
    
    # Should not raise an exception
    engine.update_mood("nonexistent_user", "happy", 5)
    
    # Verify update_user_data was NOT called
    mock_update_user_data.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

