"""
Unit tests for Callback Memory System

Tests the basic functionality of the CallbackMemorySystem class.
"""

import pytest
from modules.callback_memory_system import CallbackMemorySystem


class TestCallbackMemorySystem:
    """Test suite for CallbackMemorySystem"""
    
    def test_calculate_recall_probability(self):
        """Test that recall probability is calculated as affection_level / 100"""
        system = CallbackMemorySystem()
        
        # Test various affection levels
        assert system.calculate_recall_probability(0) == 0.0
        assert system.calculate_recall_probability(30) == 0.3
        assert system.calculate_recall_probability(50) == 0.5
        assert system.calculate_recall_probability(70) == 0.7
        assert system.calculate_recall_probability(100) == 1.0
    
    def test_should_trigger_callback_suppression_below_30(self):
        """Test that callbacks are suppressed when affection < 30"""
        system = CallbackMemorySystem()
        
        # Test multiple times to ensure it's always False, not just probabilistic
        for _ in range(10):
            assert system.should_trigger_callback(0) is False
            assert system.should_trigger_callback(10) is False
            assert system.should_trigger_callback(29) is False
    
    def test_should_trigger_callback_at_100_affection(self):
        """Test that callbacks always trigger at 100% affection"""
        system = CallbackMemorySystem()
        
        # At 100 affection, probability is 1.0, so it should always trigger
        for _ in range(10):
            assert system.should_trigger_callback(100) is True
    
    def test_should_trigger_callback_probabilistic_behavior(self):
        """Test that callbacks have probabilistic behavior at mid-range affection"""
        system = CallbackMemorySystem()
        
        # At 50% affection, we should see some True and some False over many trials
        results = [system.should_trigger_callback(50) for _ in range(100)]
        
        # We should have both True and False results (not all the same)
        assert True in results
        assert False in results
        
        # The ratio should be roughly 50% (with some variance)
        true_count = sum(results)
        assert 30 < true_count < 70  # Allow for statistical variance
    
    def test_select_callback_memory_filters_high_weight(self):
        """Test that select_callback_memory filters memories with weight > 0.7"""
        system = CallbackMemorySystem()
        
        # Create test memories with various weights
        long_term_memory = [
            {"text": "Low weight memory", "weight": 0.3},
            {"text": "Medium weight memory", "weight": 0.6},
            {"text": "High weight memory 1", "weight": 0.8},
            {"text": "High weight memory 2", "weight": 0.9},
            {"text": "Max weight memory", "weight": 1.0}
        ]
        
        # Select multiple times to ensure only high-weight memories are selected
        for _ in range(20):
            selected = system.select_callback_memory(long_term_memory)
            assert selected is not None
            assert selected["weight"] > 0.7
            assert selected["text"] in [
                "High weight memory 1",
                "High weight memory 2",
                "Max weight memory"
            ]
    
    def test_select_callback_memory_returns_none_when_no_high_weight(self):
        """Test that select_callback_memory returns None when no high-weight memories exist"""
        system = CallbackMemorySystem()
        
        # Create memories with only low weights
        long_term_memory = [
            {"text": "Low weight memory 1", "weight": 0.3},
            {"text": "Low weight memory 2", "weight": 0.5},
            {"text": "Threshold memory", "weight": 0.7}  # Exactly 0.7, not > 0.7
        ]
        
        selected = system.select_callback_memory(long_term_memory)
        assert selected is None
    
    def test_select_callback_memory_returns_none_for_empty_list(self):
        """Test that select_callback_memory returns None for empty memory list"""
        system = CallbackMemorySystem()
        
        selected = system.select_callback_memory([])
        assert selected is None
    
    def test_select_callback_memory_random_selection(self):
        """Test that select_callback_memory randomly selects from high-weight memories"""
        system = CallbackMemorySystem()
        
        # Create multiple high-weight memories
        long_term_memory = [
            {"text": "Memory A", "weight": 0.8},
            {"text": "Memory B", "weight": 0.9},
            {"text": "Memory C", "weight": 1.0}
        ]
        
        # Select many times and collect results
        selections = [system.select_callback_memory(long_term_memory)["text"] for _ in range(50)]
        
        # All three memories should appear at least once (probabilistically)
        unique_selections = set(selections)
        assert len(unique_selections) > 1  # Should have variety
    
    def test_format_callback_includes_memory_text(self):
        """Test that format_callback includes the memory text in the output"""
        system = CallbackMemorySystem()
        
        memory = {"text": "you love programming", "weight": 0.9}
        
        formatted = system.format_callback(memory)
        
        # The formatted callback should include the memory text
        assert "you love programming" in formatted
    
    def test_format_callback_uses_natural_phrasing(self):
        """Test that format_callback uses one of the predefined natural phrases"""
        system = CallbackMemorySystem()
        
        memory = {"text": "you enjoy coffee", "weight": 0.8}
        
        expected_phrases = [
            "Last time you said...",
            "I remember when you told me...",
            "You mentioned before that...",
            "Didn't you say...?",
            "I haven't forgotten that you..."
        ]
        
        # Test multiple times to see various phrases
        formatted_callbacks = [system.format_callback(memory) for _ in range(20)]
        
        # At least one should start with one of the expected phrases
        for callback in formatted_callbacks:
            assert any(callback.startswith(phrase) for phrase in expected_phrases)
    
    def test_format_callback_handles_missing_text_field(self):
        """Test that format_callback handles memory dict without text field"""
        system = CallbackMemorySystem()
        
        memory = {"weight": 0.9}  # Missing text field
        
        formatted = system.format_callback(memory)
        
        # Should not crash and should return a string
        assert isinstance(formatted, str)
        # Should contain one of the phrases followed by empty string
        assert formatted.endswith(" ")
