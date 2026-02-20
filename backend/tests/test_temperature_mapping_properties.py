"""
Property-based tests for Temperature Scaling System.

This module uses Hypothesis to test universal properties that should hold
for mood-to-temperature mapping.

**Validates: Requirements 19.4, 19.5, 19.6, 19.7, 19.8, 19.9**
"""

import pytest
from hypothesis import given, strategies as st, settings

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from temperature_scaling_system import TemperatureScalingSystem


class TestProperty31_MoodBasedTemperatureMapping:
    """
    Property 31: Mood-Based Temperature Mapping
    
    **Validates: Requirements 19.4, 19.5, 19.6, 19.7, 19.8, 19.9**
    
    For each mood value, the correct temperature should be returned:
    - angry: 0.3 (controlled, sharp speech)
    - sad: 0.4 (subdued, quiet speech)
    - neutral: 0.5 (standard variation)
    - happy: 0.7 (playful variation)
    - jealous: 0.8 (emotionally reactive speech)
    - flustered: 0.9 (chaotic, stuttering speech)
    """
    
    @given(mood=st.sampled_from(["angry"]))
    @settings(max_examples=10, deadline=None)
    def test_angry_mood_temperature(self, mood):
        """Test that 'angry' mood maps to temperature 0.3."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.3, (
            f"Expected temperature 0.3 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["sad"]))
    @settings(max_examples=10, deadline=None)
    def test_sad_mood_temperature(self, mood):
        """Test that 'sad' mood maps to temperature 0.4."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.4, (
            f"Expected temperature 0.4 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["neutral"]))
    @settings(max_examples=10, deadline=None)
    def test_neutral_mood_temperature(self, mood):
        """Test that 'neutral' mood maps to temperature 0.5."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.5, (
            f"Expected temperature 0.5 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["happy"]))
    @settings(max_examples=10, deadline=None)
    def test_happy_mood_temperature(self, mood):
        """Test that 'happy' mood maps to temperature 0.7."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.7, (
            f"Expected temperature 0.7 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["jealous"]))
    @settings(max_examples=10, deadline=None)
    def test_jealous_mood_temperature(self, mood):
        """Test that 'jealous' mood maps to temperature 0.8."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.8, (
            f"Expected temperature 0.8 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["flustered"]))
    @settings(max_examples=10, deadline=None)
    def test_flustered_mood_temperature(self, mood):
        """Test that 'flustered' mood maps to temperature 0.9."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert temperature == 0.9, (
            f"Expected temperature 0.9 for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["angry", "sad", "neutral", "happy", "jealous", "flustered"]))
    @settings(max_examples=10, deadline=None)
    def test_all_moods_map_to_correct_temperature(self, mood):
        """Test that all mood values map to their correct temperature values."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        # Define expected mappings
        expected_temperatures = {
            "angry": 0.3,
            "sad": 0.4,
            "neutral": 0.5,
            "happy": 0.7,
            "jealous": 0.8,
            "flustered": 0.9
        }
        
        expected_temp = expected_temperatures[mood]
        assert temperature == expected_temp, (
            f"Expected temperature {expected_temp} for mood '{mood}', got {temperature}"
        )
    
    @given(mood=st.sampled_from(["angry", "sad", "neutral", "happy", "jealous", "flustered"]))
    @settings(max_examples=10, deadline=None)
    def test_temperature_within_valid_range(self, mood):
        """Test that all temperatures are within valid range [0.0, 1.0]."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert 0.0 <= temperature <= 1.0, (
            f"Temperature {temperature} for mood '{mood}' is out of valid range [0.0, 1.0]"
        )
    
    @given(mood=st.sampled_from(["angry", "sad", "neutral", "happy", "jealous", "flustered"]))
    @settings(max_examples=10, deadline=None)
    def test_temperature_is_float(self, mood):
        """Test that temperature values are returned as floats."""
        system = TemperatureScalingSystem()
        temperature = system.get_temperature(mood)
        
        assert isinstance(temperature, (float, int)), (
            f"Temperature for mood '{mood}' should be numeric, got {type(temperature)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
