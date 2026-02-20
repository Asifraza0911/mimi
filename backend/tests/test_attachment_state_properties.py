"""
Property-based tests for Attachment Style Engine.

This module uses Hypothesis to test universal properties that should hold
for attachment state mapping based on affection levels.

**Validates: Requirements 18.3, 18.4, 18.5, 18.6**
"""

import pytest
from unittest.mock import Mock
from hypothesis import given, strategies as st, settings

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from attachment_style_engine import AttachmentStyleEngine


class TestProperty30_AttachmentStateMapping:
    """
    Property 30: Attachment State Mapping
    
    **Validates: Requirements 18.3, 18.4, 18.5, 18.6**
    
    For any affection level (0-100):
    - If affection_level is 0-30: attachment_state should be "avoidant"
    - If affection_level is 31-59: attachment_state should be "anxious"
    - If affection_level is 60-79: attachment_state should be "secure"
    - If affection_level is 80-100: attachment_state should be "possessive"
    """
    
    @given(affection_level=st.integers(min_value=0, max_value=30))
    @settings(max_examples=10, deadline=None)
    def test_avoidant_state_for_low_affection(self, affection_level):
        """Test that affection levels 0-30 map to 'avoidant' attachment state."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify avoidant state for low affection
        assert attachment_state == "avoidant", (
            f"Expected 'avoidant' for affection_level={affection_level}, "
            f"got '{attachment_state}'"
        )
    
    @given(affection_level=st.integers(min_value=31, max_value=59))
    @settings(max_examples=10, deadline=None)
    def test_anxious_state_for_medium_low_affection(self, affection_level):
        """Test that affection levels 31-59 map to 'anxious' attachment state."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify anxious state for medium-low affection
        assert attachment_state == "anxious", (
            f"Expected 'anxious' for affection_level={affection_level}, "
            f"got '{attachment_state}'"
        )
    
    @given(affection_level=st.integers(min_value=60, max_value=79))
    @settings(max_examples=10, deadline=None)
    def test_secure_state_for_medium_high_affection(self, affection_level):
        """Test that affection levels 60-79 map to 'secure' attachment state."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify secure state for medium-high affection
        assert attachment_state == "secure", (
            f"Expected 'secure' for affection_level={affection_level}, "
            f"got '{attachment_state}'"
        )
    
    @given(affection_level=st.integers(min_value=80, max_value=100))
    @settings(max_examples=10, deadline=None)
    def test_possessive_state_for_high_affection(self, affection_level):
        """Test that affection levels 80-100 map to 'possessive' attachment state."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify possessive state for high affection
        assert attachment_state == "possessive", (
            f"Expected 'possessive' for affection_level={affection_level}, "
            f"got '{attachment_state}'"
        )
    
    @given(affection_level=st.integers(min_value=0, max_value=100))
    @settings(max_examples=10, deadline=None)
    def test_all_affection_levels_map_to_valid_state(self, affection_level):
        """Test that all affection levels map to one of the four valid attachment states."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify state is one of the valid options
        valid_states = ["avoidant", "anxious", "secure", "possessive"]
        assert attachment_state in valid_states, (
            f"Invalid attachment state '{attachment_state}' for affection_level={affection_level}"
        )
    
    @given(affection_level=st.integers(min_value=0, max_value=100))
    @settings(max_examples=10, deadline=None)
    def test_attachment_state_boundaries(self, affection_level):
        """Test that attachment state boundaries are correctly enforced."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Verify correct state based on boundaries
        if affection_level <= 30:
            expected_state = "avoidant"
        elif affection_level <= 59:
            expected_state = "anxious"
        elif affection_level <= 79:
            expected_state = "secure"
        else:  # 80-100
            expected_state = "possessive"
        
        assert attachment_state == expected_state, (
            f"Expected '{expected_state}' for affection_level={affection_level}, "
            f"got '{attachment_state}'"
        )
    
    @given(affection_level=st.integers(min_value=0, max_value=100))
    @settings(max_examples=10, deadline=None)
    def test_attachment_instructions_exist_for_all_states(self, affection_level):
        """Test that behavioral instructions exist for all attachment states."""
        # Mock Firestore client
        mock_db = Mock()
        
        # Create attachment style engine
        engine = AttachmentStyleEngine(mock_db)
        
        # Determine attachment state
        attachment_state = engine.determine_attachment_state(affection_level)
        
        # Get attachment instructions
        instructions = engine.get_attachment_instructions(attachment_state)
        
        # Verify instructions exist and are non-empty
        assert instructions is not None
        assert isinstance(instructions, str)
        assert len(instructions) > 0, (
            f"No instructions found for attachment state '{attachment_state}'"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
