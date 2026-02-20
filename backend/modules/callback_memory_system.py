"""
Callback Memory System Module

This module implements self-initiated memory recall functionality where Mimi
naturally brings up past conversations based on affection level. Higher affection
means higher probability of callbacks.

Requirements: 21.1, 21.2, 21.3, 21.8
"""

import random
from typing import Optional


class CallbackMemorySystem:
    """
    Manages probabilistic memory callbacks based on affection level.
    
    The system calculates recall probability as affection_level / 100 and
    uses probabilistic logic to determine if a callback should trigger.
    Callbacks are suppressed when affection < 30.
    """
    
    def __init__(self):
        """Initialize the Callback Memory System."""
        self.min_affection_for_callbacks = 30
    
    def calculate_recall_probability(self, affection_level: int) -> float:
        """
        Calculate the probability of memory recall based on affection level.
        
        Args:
            affection_level: Current affection level (0-100)
            
        Returns:
            Probability value between 0.0 and 1.0 (affection_level / 100)
            
        Requirements: 21.2
        """
        return affection_level / 100.0
    
    def should_trigger_callback(self, affection_level: int) -> bool:
        """
        Determine if a memory callback should be triggered using probabilistic logic.
        
        The method suppresses callbacks when affection < 30 and uses random
        probability based on affection level for higher values.
        
        Args:
            affection_level: Current affection level (0-100)
            
        Returns:
            True if callback should trigger, False otherwise
            
        Requirements: 21.1, 21.3, 21.8
        """
        # Suppress callbacks when affection is below threshold
        if affection_level < self.min_affection_for_callbacks:
            return False
        
        # Calculate recall probability
        probability = self.calculate_recall_probability(affection_level)
        
        # Use probabilistic logic to determine if callback should trigger
        return random.random() < probability
    
    def select_callback_memory(self, long_term_memory: list) -> Optional[dict]:
        """
        Select a high-weight memory for callback reference.
        
        Filters memories with Memory_Weight > 0.7 and randomly selects one
        for natural conversation continuity.
        
        Args:
            long_term_memory: List of memory objects with text and weight fields
            
        Returns:
            Selected memory dict or None if no suitable memories exist
            
        Requirements: 21.4, 21.5, 21.6
        """
        # Filter memories with weight > 0.7
        high_weight_memories = [
            memory for memory in long_term_memory
            if memory.get("weight", 0.0) > 0.7
        ]
        
        # Return None if no high-weight memories exist
        if not high_weight_memories:
            return None
        
        # Randomly select one high-weight memory
        return random.choice(high_weight_memories)
    
    def format_callback(self, memory: dict) -> str:
        """
        Format a memory as a callback reference with natural phrasing.
        
        Uses phrases like "Last time you said..." or "I remember when you told me..."
        to create natural conversation continuity.
        
        Args:
            memory: Memory dict with text field
            
        Returns:
            Formatted callback string
            
        Requirements: 21.6
        """
        callback_phrases = [
            "Last time you said...",
            "I remember when you told me...",
            "You mentioned before that...",
            "Didn't you say...?",
            "I haven't forgotten that you..."
        ]
        
        # Randomly select a callback phrase
        phrase = random.choice(callback_phrases)
        
        # Format with the memory text
        memory_text = memory.get("text", "")
        return f"{phrase} {memory_text}"


