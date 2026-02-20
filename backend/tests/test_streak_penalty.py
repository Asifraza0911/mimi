"""
Unit tests for InteractionStreakSystem.apply_streak_penalty method.

This test verifies that the streak break penalty logic correctly:
- Decreases affection_level by 3 points
- Ensures affection_level never drops below 0
- Sets mood to "sad"
- Updates last_chat_date to current date
- Updates Firestore with the new values

Requirements: 20.7, 20.8, 20.9, 20.13
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch
from modules.interaction_streak_system import InteractionStreakSystem


class TestApplyStreakPenalty:
    """Test suite for apply_streak_penalty method."""
    
    @pytest.fixture
    def mock_firestore(self):
        """Create a mock Firestore client."""
        return Mock()
    
    @pytest.fixture
    def streak_system(self, mock_firestore):
        """Create an InteractionStreakSystem instance with mocked Firestore."""
        return InteractionStreakSystem(mock_firestore)
    
    def test_apply_penalty_decreases_affection_by_3(self, streak_system):
        """Test that affection_level is decreased by 3 points."""
        user_data = {
            "affection_level": 50,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["affection_level"] == 47
    
    def test_apply_penalty_never_goes_below_zero(self, streak_system):
        """Test that affection_level never drops below 0."""
        user_data = {
            "affection_level": 2,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["affection_level"] == 0
    
    def test_apply_penalty_sets_mood_to_sad(self, streak_system):
        """Test that mood is set to 'sad' when streak is broken."""
        user_data = {
            "affection_level": 50,
            "mood": "happy",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["mood"] == "sad"
    
    def test_apply_penalty_updates_last_chat_date(self, streak_system):
        """Test that last_chat_date is updated to current date."""
        user_data = {
            "affection_level": 50,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["last_chat_date"] == date.today()
    
    def test_apply_penalty_calls_firestore_update(self, streak_system):
        """Test that Firestore is updated with the new values."""
        user_data = {
            "affection_level": 50,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data') as mock_update:
            streak_system.apply_streak_penalty("test_user", user_data)
            
            # Verify update_user_data was called with correct arguments
            mock_update.assert_called_once()
            call_args = mock_update.call_args
            
            assert call_args[0][1] == "test_user"  # user_id
            updates = call_args[0][2]
            assert updates["affection_level"] == 47
            assert updates["mood"] == "sad"
            assert updates["last_chat_date"] == date.today()
    
    def test_apply_penalty_with_zero_affection(self, streak_system):
        """Test edge case where affection is already 0."""
        user_data = {
            "affection_level": 0,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["affection_level"] == 0
        assert result["mood"] == "sad"
