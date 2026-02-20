"""
Property-based tests for Interaction Streak System.

This module uses Hypothesis to test universal properties that should hold
for interaction streak tracking and penalty application.

**Validates: Requirements 20.4, 20.5, 20.6, 20.7, 20.13**
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import date, timedelta
from unittest.mock import Mock, patch

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from interaction_streak_system import InteractionStreakSystem


class TestProperty32_InteractionStreakUpdateLogic:
    """
    Property 32: Interaction Streak Update Logic
    
    **Validates: Requirements 20.4, 20.5, 20.6**
    
    For any user interaction:
    - If current date equals last_chat_date: streak is unchanged
    - If current date is exactly one day after last_chat_date: streak increments by 1
    - If current date is more than one day after last_chat_date: streak resets to 1
    """
    
    @given(
        current_streak=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_same_day_streak_unchanged(self, current_streak):
        """
        Property: When current date equals last_chat_date, streak is unchanged.
        
        **Validates: Requirement 20.4**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        today = date.today()
        
        new_streak, was_broken = streak_system.calculate_streak(
            last_chat_date=today,
            current_date=today,
            current_streak=current_streak
        )
        
        assert new_streak == current_streak, (
            f"Expected streak to remain {current_streak} when chatting same day, "
            f"but got {new_streak}"
        )
        assert was_broken is False, (
            "Streak should not be marked as broken when chatting same day"
        )
    
    @given(
        current_streak=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_next_day_streak_increments(self, current_streak):
        """
        Property: When current date is exactly one day after last_chat_date,
        streak increments by 1.
        
        **Validates: Requirement 20.5**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        new_streak, was_broken = streak_system.calculate_streak(
            last_chat_date=yesterday,
            current_date=today,
            current_streak=current_streak
        )
        
        assert new_streak == current_streak + 1, (
            f"Expected streak to increment from {current_streak} to {current_streak + 1}, "
            f"but got {new_streak}"
        )
        assert was_broken is False, (
            "Streak should not be marked as broken when chatting next day"
        )
    
    @given(
        days_gap=st.integers(min_value=2, max_value=30),
        current_streak=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_gap_more_than_one_day_resets_streak(self, days_gap, current_streak):
        """
        Property: When current date is more than one day after last_chat_date,
        streak resets to 1.
        
        **Validates: Requirement 20.6**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        today = date.today()
        last_chat = today - timedelta(days=days_gap)
        
        new_streak, was_broken = streak_system.calculate_streak(
            last_chat_date=last_chat,
            current_date=today,
            current_streak=current_streak
        )
        
        assert new_streak == 1, (
            f"Expected streak to reset to 1 after {days_gap} days gap, "
            f"but got {new_streak}"
        )
        assert was_broken is True, (
            f"Streak should be marked as broken after {days_gap} days gap"
        )
    
    @given(
        days_gap=st.integers(min_value=0, max_value=10),
        current_streak=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_streak_logic_comprehensive(self, days_gap, current_streak):
        """
        Property: Comprehensive test of all streak update scenarios.
        
        **Validates: Requirements 20.4, 20.5, 20.6**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        today = date.today()
        last_chat = today - timedelta(days=days_gap)
        
        new_streak, was_broken = streak_system.calculate_streak(
            last_chat_date=last_chat,
            current_date=today,
            current_streak=current_streak
        )
        
        if days_gap == 0:
            # Same day - streak unchanged
            assert new_streak == current_streak
            assert was_broken is False
        elif days_gap == 1:
            # Next day - streak increments
            assert new_streak == current_streak + 1
            assert was_broken is False
        else:
            # Gap > 1 day - streak resets
            assert new_streak == 1
            assert was_broken is True


class TestProperty33_StreakBreakAffectionPenalty:
    """
    Property 33: Streak Break Affection Penalty
    
    **Validates: Requirements 20.7, 20.13**
    
    For any broken streak, the affection_level should decrease by 3 points,
    ensuring it never drops below 0.
    """
    
    @given(
        initial_affection=st.integers(min_value=4, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_penalty_decreases_affection_by_3(self, initial_affection):
        """
        Property: When streak is broken, affection decreases by exactly 3 points.
        
        **Validates: Requirement 20.7**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        user_data = {
            "affection_level": initial_affection,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        expected_affection = initial_affection - 3
        assert result["affection_level"] == expected_affection, (
            f"Expected affection to decrease from {initial_affection} to {expected_affection}, "
            f"but got {result['affection_level']}"
        )
    
    @given(
        initial_affection=st.integers(min_value=0, max_value=3)
    )
    @settings(max_examples=10, deadline=None)
    def test_penalty_never_goes_below_zero(self, initial_affection):
        """
        Property: Affection level never drops below 0 after penalty.
        
        **Validates: Requirement 20.13**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        user_data = {
            "affection_level": initial_affection,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["affection_level"] >= 0, (
            f"Affection level should never be negative, but got {result['affection_level']}"
        )
        assert result["affection_level"] == 0, (
            f"Expected affection to be 0 when starting from {initial_affection}, "
            f"but got {result['affection_level']}"
        )
    
    @given(
        initial_affection=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_penalty_sets_mood_to_sad(self, initial_affection):
        """
        Property: When streak is broken, mood is always set to 'sad'.
        
        **Validates: Requirement 20.8**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        user_data = {
            "affection_level": initial_affection,
            "mood": "happy",  # Start with any mood
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        assert result["mood"] == "sad", (
            f"Expected mood to be 'sad' after streak break, but got '{result['mood']}'"
        )
    
    @given(
        initial_affection=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=10, deadline=None)
    def test_penalty_comprehensive(self, initial_affection):
        """
        Property: Comprehensive test of penalty application.
        
        **Validates: Requirements 20.7, 20.13**
        """
        # Create streak system inside test method
        mock_firestore = Mock()
        streak_system = InteractionStreakSystem(mock_firestore)
        
        user_data = {
            "affection_level": initial_affection,
            "mood": "neutral",
            "last_chat_date": date(2024, 1, 1)
        }
        
        with patch('modules.firestore_operations.update_user_data'):
            result = streak_system.apply_streak_penalty("test_user", user_data)
        
        # Calculate expected affection (decrease by 3, but never below 0)
        expected_affection = max(0, initial_affection - 3)
        
        assert result["affection_level"] == expected_affection, (
            f"Expected affection {expected_affection}, got {result['affection_level']}"
        )
        assert result["affection_level"] >= 0, (
            "Affection should never be negative"
        )
        assert result["mood"] == "sad", (
            "Mood should be 'sad' after streak break"
        )
        assert result["last_chat_date"] == date.today(), (
            "Last chat date should be updated to today"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
