"""
Unit tests for Temperature Scaling System

Tests the mood-to-temperature mapping functionality.
"""

import pytest
from modules.temperature_scaling_system import TemperatureScalingSystem


class TestTemperatureScalingSystem:
    """Test suite for TemperatureScalingSystem class."""
    
    def test_initialization(self):
        """Test that the system initializes with correct mood mappings."""
        system = TemperatureScalingSystem()
        
        assert system.mood_temperature_map["angry"] == 0.3
        assert system.mood_temperature_map["sad"] == 0.4
        assert system.mood_temperature_map["neutral"] == 0.5
        assert system.mood_temperature_map["happy"] == 0.7
        assert system.mood_temperature_map["jealous"] == 0.8
        assert system.mood_temperature_map["flustered"] == 0.9
        assert system.default_temperature == 0.5
    
    def test_get_temperature_angry(self):
        """Test temperature for angry mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("angry") == 0.3
    
    def test_get_temperature_sad(self):
        """Test temperature for sad mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("sad") == 0.4
    
    def test_get_temperature_neutral(self):
        """Test temperature for neutral mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("neutral") == 0.5
    
    def test_get_temperature_happy(self):
        """Test temperature for happy mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("happy") == 0.7
    
    def test_get_temperature_jealous(self):
        """Test temperature for jealous mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("jealous") == 0.8
    
    def test_get_temperature_flustered(self):
        """Test temperature for flustered mood."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("flustered") == 0.9
    
    def test_get_temperature_unknown_mood(self):
        """Test that unknown moods return default temperature."""
        system = TemperatureScalingSystem()
        assert system.get_temperature("unknown_mood") == 0.5
        assert system.get_temperature("") == 0.5
        assert system.get_temperature("excited") == 0.5
    
    def test_temperature_range(self):
        """Test that all temperatures are within valid range [0.0, 1.0]."""
        system = TemperatureScalingSystem()
        
        for mood, temp in system.mood_temperature_map.items():
            assert 0.0 <= temp <= 1.0, f"Temperature for {mood} is out of range: {temp}"
    
    def test_temperature_ordering(self):
        """Test that temperatures follow expected emotional intensity ordering."""
        system = TemperatureScalingSystem()
        
        # Controlled moods should have lower temperatures
        assert system.get_temperature("angry") < system.get_temperature("neutral")
        assert system.get_temperature("sad") < system.get_temperature("neutral")
        
        # Emotional moods should have higher temperatures
        assert system.get_temperature("happy") > system.get_temperature("neutral")
        assert system.get_temperature("jealous") > system.get_temperature("happy")
        assert system.get_temperature("flustered") > system.get_temperature("jealous")
