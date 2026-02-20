"""
Temperature Scaling System Module

This module adjusts LLM response randomness based on Mimi's current mood.
Lower temperatures (angry, sad) produce more predictable responses,
while higher temperatures (jealous, flustered) produce more varied and emotional responses.

Requirements: 19.1, 19.2
"""


class TemperatureScalingSystem:
    """
    Maps mood states to LLM temperature values for response generation.
    
    Temperature controls the randomness/creativity of LLM responses:
    - Lower values (0.3-0.4): More controlled, predictable, sharp
    - Medium values (0.5-0.7): Standard to playful variation
    - Higher values (0.8-0.9): Emotionally reactive, chaotic, stuttering
    """
    
    def __init__(self):
        """Initialize the temperature scaling system with mood-temperature mappings."""
        # Mood to temperature mapping as specified in Requirements 19.2
        self.mood_temperature_map = {
            "angry": 0.3,      # Controlled, sharp speech
            "sad": 0.4,        # Subdued, quiet speech
            "neutral": 0.5,    # Standard variation
            "happy": 0.7,      # Playful variation
            "jealous": 0.8,    # Emotionally reactive speech
            "flustered": 0.9   # Chaotic, stuttering speech
        }
        self.default_temperature = 0.5
    
    def get_temperature(self, mood: str) -> float:
        """
        Get LLM temperature for current mood.
        
        Args:
            mood: Current emotional state (angry, sad, neutral, happy, jealous, flustered)
            
        Returns:
            Temperature value (0.0-1.0) for LLM response generation
            
        Requirements: 19.1, 19.2
        """
        return self.mood_temperature_map.get(mood, self.default_temperature)
