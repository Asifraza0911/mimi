"""
Property-based tests for Affection Decay Engine.

This module uses Hypothesis to test universal properties that should hold
for time-based affection decay calculations.

**Validates: Requirements 16.2, 16.3, 16.4, 16.7**
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from models import UserData, DecayResult
from affection_decay_engine import AffectionDecayEngine


# Custom strategies for generating test data
@composite
def hours_passed_strategy(draw):
    """Generate hours passed values for testing decay scenarios."""
    return draw(st.integers(min_value=0, max_value=720))  # 0 to 30 days


@composite
def affection_level_strategy(draw):
    """Generate valid affection levels."""
    return draw(st.integers(min_value=0, max_value=100))


@composite
def timestamp_pair_strategy(draw):
    """Generate a pair of timestamps with controlled time difference."""
    hours_passed = draw(st.integers(min_value=0, max_value=720))
    current_time = datetime.now()
    last_interaction = current_time - timedelta(hours=hours_passed)
    return last_interaction, current_time, hours_passed


class TestProperty26_AffectionDecayCalculation:
    """
    Property 26: Affection Decay Calculation
    
    **Validates: Requirements 16.2, 16.3**
    
    For any time elapsed since last interaction:
    - If hours_passed <= 24: decay = 0
    - If hours_passed > 24: decay = hours_passed // 24
    - Affection never drops below 0
    """
    
    @given(timestamp_data=timestamp_pair_strategy())
    @settings(max_examples=10, deadline=None)
    def test_no_decay_within_24_hours(self, timestamp_data):
        """Test that no decay occurs when hours_passed <= 24."""
        last_interaction, current_time, hours_passed = timestamp_data
        
        # Skip if hours_passed > 24
        if hours_passed > 24:
            return
        
        # Mock Firestore client
        mock_db = Mock()
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Calculate decay
        decay_amount = engine.calculate_decay(last_interaction, current_time)
        
        # Verify no decay within 24 hours
        assert decay_amount == 0
    
    @given(timestamp_data=timestamp_pair_strategy())
    @settings(max_examples=10, deadline=None)
    def test_decay_formula_after_24_hours(self, timestamp_data):
        """Test that decay = hours_passed // 24 when hours_passed > 24."""
        last_interaction, current_time, hours_passed = timestamp_data
        
        # Skip if hours_passed <= 24
        if hours_passed <= 24:
            return
        
        # Mock Firestore client
        mock_db = Mock()
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Calculate decay
        decay_amount = engine.calculate_decay(last_interaction, current_time)
        
        # Verify decay formula
        expected_decay = hours_passed // 24
        assert decay_amount == expected_decay
    
    @given(
        affection_level=affection_level_strategy(),
        hours_passed=st.integers(min_value=25, max_value=720)
    )
    @settings(max_examples=10, deadline=None)
    def test_affection_never_drops_below_zero(self, affection_level, hours_passed):
        """Test that affection level never drops below 0 after decay."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data with specific affection level
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=affection_level,
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Calculate expected new affection
        decay_amount = hours_passed // 24
        expected_affection = max(0, affection_level - decay_amount)
        
        # Verify affection never goes below 0
        assert result.affection_delta <= 0  # Delta should be negative or zero
        assert affection_level + result.affection_delta >= 0
        assert affection_level + result.affection_delta == expected_affection
    
    @given(
        affection_level=affection_level_strategy(),
        hours_passed=st.integers(min_value=0, max_value=24)
    )
    @settings(max_examples=10, deadline=None)
    def test_no_affection_change_within_threshold(self, affection_level, hours_passed):
        """Test that affection doesn't change when within 24-hour threshold."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=affection_level,
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify no affection change
        assert result.affection_delta == 0
        assert result.hours_passed == hours_passed
    
    @given(hours_passed=st.integers(min_value=25, max_value=720))
    @settings(max_examples=10, deadline=None)
    def test_decay_amount_is_integer_division(self, hours_passed):
        """Test that decay uses integer division (hours_passed // 24)."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create timestamps
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        # Calculate decay
        decay_amount = engine.calculate_decay(last_interaction, current_time)
        
        # Verify integer division
        expected_decay = hours_passed // 24
        assert decay_amount == expected_decay
        assert isinstance(decay_amount, int)


class TestProperty27_SadMoodOnExtendedAbsence:
    """
    Property 27: Sad Mood on Extended Absence
    
    **Validates: Requirements 16.4, 16.7**
    
    For any user interaction:
    - If hours_passed > 72: mood should be set to "sad"
    - If hours_passed <= 72: mood should not be changed by decay
    """
    
    @given(hours_passed=st.integers(min_value=73, max_value=720))
    @settings(max_examples=10, deadline=None)
    def test_mood_becomes_sad_after_72_hours(self, hours_passed):
        """Test that mood is set to 'sad' when hours_passed > 72."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data with neutral mood
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=50,
            mood="neutral",
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify mood is set to sad
        assert result.new_mood == "sad"
        assert result.hours_passed > 72
    
    @given(hours_passed=st.integers(min_value=0, max_value=72))
    @settings(max_examples=10, deadline=None)
    def test_mood_not_changed_within_72_hours(self, hours_passed):
        """Test that mood is not changed when hours_passed <= 72."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data with happy mood
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=50,
            mood="happy",
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify mood is not changed
        assert result.new_mood is None
        assert result.hours_passed <= 72
    
    @given(
        initial_mood=st.sampled_from(["happy", "neutral", "angry", "jealous", "flustered"]),
        hours_passed=st.integers(min_value=73, max_value=720)
    )
    @settings(max_examples=10, deadline=None)
    def test_any_mood_becomes_sad_after_extended_absence(self, initial_mood, hours_passed):
        """Test that any mood becomes 'sad' after extended absence."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data with any initial mood
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=50,
            mood=initial_mood,
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify mood becomes sad regardless of initial mood
        assert result.new_mood == "sad"
    
    @given(
        affection_level=affection_level_strategy(),
        hours_passed=st.integers(min_value=73, max_value=720)
    )
    @settings(max_examples=10, deadline=None)
    def test_firestore_updated_with_sad_mood(self, affection_level, hours_passed):
        """Test that Firestore is updated with sad mood after extended absence."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=affection_level,
            mood="neutral",
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify Firestore update was called with mood
        mock_doc_ref.update.assert_called_once()
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "mood" in call_args
        assert call_args["mood"] == "sad"
    
    @given(hours_passed=st.integers(min_value=0, max_value=24))
    @settings(max_examples=10, deadline=None)
    def test_no_firestore_update_when_no_decay(self, hours_passed):
        """Test that Firestore is not updated when no decay occurs."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Create decay engine
        engine = AffectionDecayEngine(mock_db)
        
        # Create user data
        current_time = datetime.now()
        last_interaction = current_time - timedelta(hours=hours_passed)
        
        user_data = UserData(
            user_id="test_user",
            affection_level=50,
            mood="neutral",
            last_interaction=last_interaction
        )
        
        # Apply decay
        result = engine.apply_decay("test_user", user_data)
        
        # Verify Firestore update was not called
        mock_doc_ref.update.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
