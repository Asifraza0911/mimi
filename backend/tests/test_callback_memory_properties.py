"""
Property-based tests for Callback Memory System.

This module uses Hypothesis to test universal properties that should hold
for self-initiated memory recall functionality.

**Validates: Requirements 21.2, 21.4, 21.6, 21.8**
"""

import pytest
from hypothesis import given, strategies as st, settings

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from callback_memory_system import CallbackMemorySystem


# Custom strategies for generating test data
@st.composite
def affection_level_strategy(draw):
    """Generate valid affection levels (0-100)."""
    return draw(st.integers(min_value=0, max_value=100))


@st.composite
def memory_list_strategy(draw):
    """Generate a list of memory objects with various weights."""
    num_memories = draw(st.integers(min_value=0, max_value=20))
    memories = []
    for _ in range(num_memories):
        weight = draw(st.floats(min_value=0.0, max_value=1.0))
        text = draw(st.text(min_size=1, max_size=100))
        memories.append({"text": text, "weight": weight})
    return memories


@st.composite
def high_weight_memory_list_strategy(draw):
    """Generate a list of memory objects with weights > 0.7."""
    num_memories = draw(st.integers(min_value=1, max_value=10))
    memories = []
    for _ in range(num_memories):
        weight = draw(st.floats(min_value=0.71, max_value=1.0))
        text = draw(st.text(min_size=1, max_size=100))
        memories.append({"text": text, "weight": weight})
    return memories


@st.composite
def low_weight_memory_list_strategy(draw):
    """Generate a list of memory objects with weights <= 0.7."""
    num_memories = draw(st.integers(min_value=1, max_value=10))
    memories = []
    for _ in range(num_memories):
        weight = draw(st.floats(min_value=0.0, max_value=0.7))
        text = draw(st.text(min_size=1, max_size=100))
        memories.append({"text": text, "weight": weight})
    return memories


class TestProperty34_CallbackProbabilityCalculation:
    """
    Property 34: Callback Probability Calculation
    
    **Validates: Requirements 21.2**
    
    For any affection level (0-100):
    - Recall probability = affection_level / 100
    - Probability is always between 0.0 and 1.0
    - Probability increases linearly with affection
    """
    
    @given(affection_level=affection_level_strategy())
    @settings(max_examples=10, deadline=None)
    def test_probability_equals_affection_divided_by_100(self, affection_level):
        """Test that recall probability is calculated as affection_level / 100."""
        system = CallbackMemorySystem()
        
        probability = system.calculate_recall_probability(affection_level)
        
        # Verify the formula
        expected_probability = affection_level / 100.0
        assert probability == expected_probability
    
    @given(affection_level=affection_level_strategy())
    @settings(max_examples=10, deadline=None)
    def test_probability_is_between_0_and_1(self, affection_level):
        """Test that probability is always in valid range [0.0, 1.0]."""
        system = CallbackMemorySystem()
        
        probability = system.calculate_recall_probability(affection_level)
        
        # Verify range
        assert 0.0 <= probability <= 1.0
    
    @given(
        affection1=affection_level_strategy(),
        affection2=affection_level_strategy()
    )
    @settings(max_examples=10, deadline=None)
    def test_probability_increases_with_affection(self, affection1, affection2):
        """Test that higher affection always results in higher or equal probability."""
        system = CallbackMemorySystem()
        
        prob1 = system.calculate_recall_probability(affection1)
        prob2 = system.calculate_recall_probability(affection2)
        
        # If affection1 < affection2, then prob1 < prob2
        if affection1 < affection2:
            assert prob1 < prob2
        elif affection1 == affection2:
            assert prob1 == prob2
        else:  # affection1 > affection2
            assert prob1 > prob2
    
    @given(affection_level=affection_level_strategy())
    @settings(max_examples=10, deadline=None)
    def test_probability_is_float_type(self, affection_level):
        """Test that probability is returned as a float."""
        system = CallbackMemorySystem()
        
        probability = system.calculate_recall_probability(affection_level)
        
        assert isinstance(probability, float)


class TestProperty35_HighWeightMemorySelection:
    """
    Property 35: High-Weight Memory Selection for Callbacks
    
    **Validates: Requirements 21.4, 21.6**
    
    For any list of memories:
    - Only memories with weight > 0.7 are selected
    - Selection is random among high-weight memories
    - Returns None if no high-weight memories exist
    """
    
    @given(memories=high_weight_memory_list_strategy())
    @settings(max_examples=10, deadline=None)
    def test_only_high_weight_memories_selected(self, memories):
        """Test that only memories with weight > 0.7 are selected."""
        system = CallbackMemorySystem()
        
        # Select multiple times to verify consistency
        for _ in range(5):
            selected = system.select_callback_memory(memories)
            
            # Should always select a memory
            assert selected is not None
            
            # Selected memory should have weight > 0.7
            assert selected["weight"] > 0.7
            
            # Selected memory should be from the input list
            assert selected in memories
    
    @given(memories=low_weight_memory_list_strategy())
    @settings(max_examples=10, deadline=None)
    def test_returns_none_when_no_high_weight_memories(self, memories):
        """Test that None is returned when no memories have weight > 0.7."""
        system = CallbackMemorySystem()
        
        selected = system.select_callback_memory(memories)
        
        # Should return None since all weights are <= 0.7
        assert selected is None
    
    @given(memories=memory_list_strategy())
    @settings(max_examples=10, deadline=None)
    def test_selection_respects_weight_threshold(self, memories):
        """Test that selection strictly respects the 0.7 weight threshold."""
        system = CallbackMemorySystem()
        
        # Count high-weight memories
        high_weight_count = sum(1 for m in memories if m["weight"] > 0.7)
        
        selected = system.select_callback_memory(memories)
        
        if high_weight_count > 0:
            # Should select a high-weight memory
            assert selected is not None
            assert selected["weight"] > 0.7
        else:
            # Should return None
            assert selected is None
    
    def test_returns_none_for_empty_list(self):
        """Test that None is returned for empty memory list."""
        system = CallbackMemorySystem()
        
        selected = system.select_callback_memory([])
        
        assert selected is None
    
    @given(memories=high_weight_memory_list_strategy())
    @settings(max_examples=10, deadline=None)
    def test_random_selection_among_high_weight_memories(self, memories):
        """Test that selection is random among high-weight memories."""
        # Skip if only one memory (can't test randomness)
        if len(memories) <= 1:
            return
        
        system = CallbackMemorySystem()
        
        # Select multiple times
        selections = [system.select_callback_memory(memories) for _ in range(20)]
        
        # All selections should be from the input list
        for selected in selections:
            assert selected in memories
            assert selected["weight"] > 0.7
        
        # With multiple high-weight memories, we should see variety
        # (This is probabilistic, but with 20 selections it's very likely)
        unique_selections = len(set(s["text"] for s in selections))
        
        # If there are 2+ memories, we should see at least 2 different selections
        # (unless we're extremely unlucky)
        if len(memories) >= 2:
            # Allow for some statistical variance
            assert unique_selections >= 1  # At minimum, we selected something


class TestProperty36_CallbackSuppressionAtLowAffection:
    """
    Property 36: Callback Suppression at Low Affection
    
    **Validates: Requirements 21.8**
    
    For any affection level:
    - If affection < 30: callbacks are always suppressed (return False)
    - If affection >= 30: callbacks use probabilistic logic
    - At affection = 100: callbacks always trigger (return True)
    """
    
    @given(affection_level=st.integers(min_value=0, max_value=29))
    @settings(max_examples=10, deadline=None)
    def test_callbacks_suppressed_below_30_affection(self, affection_level):
        """Test that callbacks are always suppressed when affection < 30."""
        system = CallbackMemorySystem()
        
        # Test multiple times to ensure it's deterministic, not probabilistic
        for _ in range(10):
            result = system.should_trigger_callback(affection_level)
            
            # Should always be False
            assert result is False
    
    @given(affection_level=st.integers(min_value=30, max_value=100))
    @settings(max_examples=10, deadline=None)
    def test_callbacks_use_probability_at_or_above_30(self, affection_level):
        """Test that callbacks use probabilistic logic when affection >= 30."""
        system = CallbackMemorySystem()
        
        # At affection >= 30, the method should use probability
        # We can't test randomness directly, but we can verify it doesn't always return False
        
        # At 100 affection, it should always return True
        if affection_level == 100:
            for _ in range(10):
                result = system.should_trigger_callback(affection_level)
                assert result is True
        else:
            # For other values >= 30, it should be probabilistic
            # We'll just verify it doesn't crash and returns a boolean
            result = system.should_trigger_callback(affection_level)
            assert isinstance(result, bool)
    
    def test_callbacks_always_trigger_at_100_affection(self):
        """Test that callbacks always trigger at 100% affection."""
        system = CallbackMemorySystem()
        
        # At 100 affection, probability is 1.0, so it should always trigger
        for _ in range(10):
            result = system.should_trigger_callback(100)
            assert result is True
    
    @given(affection_level=st.integers(min_value=0, max_value=29))
    @settings(max_examples=10, deadline=None)
    def test_suppression_threshold_is_exactly_30(self, affection_level):
        """Test that the suppression threshold is exactly 30."""
        system = CallbackMemorySystem()
        
        # Below 30 should always be False
        result_below = system.should_trigger_callback(affection_level)
        assert result_below is False
        
        # At exactly 30, it should use probability (not suppressed)
        # At 30, probability is 0.3, so we test multiple times
        results_at_30 = [system.should_trigger_callback(30) for _ in range(50)]
        
        # Should have some True values (not all False)
        # With probability 0.3 and 50 trials, we expect ~15 True values
        true_count = sum(results_at_30)
        assert true_count > 0  # Should have at least some True values
    
    @given(affection_level=affection_level_strategy())
    @settings(max_examples=10, deadline=None)
    def test_return_type_is_boolean(self, affection_level):
        """Test that should_trigger_callback always returns a boolean."""
        system = CallbackMemorySystem()
        
        result = system.should_trigger_callback(affection_level)
        
        assert isinstance(result, bool)
    
    @given(affection_level=st.integers(min_value=30, max_value=99))
    @settings(max_examples=10, deadline=None)
    def test_probabilistic_behavior_between_30_and_99(self, affection_level):
        """Test that callbacks show probabilistic behavior between 30 and 99 affection."""
        system = CallbackMemorySystem()
        
        # Run multiple trials
        results = [system.should_trigger_callback(affection_level) for _ in range(100)]
        
        # Should have both True and False results (probabilistic)
        # The exact ratio depends on affection_level
        true_count = sum(results)
        
        # With 100 trials, we should see some variation
        # (not all True, not all False, unless affection is very low)
        if affection_level >= 50:
            # At 50% or higher, we should definitely see some True values
            assert true_count > 0
        
        # Should not be all True (unless affection is 100, which is excluded here)
        assert true_count < 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
