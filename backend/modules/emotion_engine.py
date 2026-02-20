"""
Emotion Engine Module

This module detects emotional keywords and jealousy triggers in user messages.
It updates mood state and affection levels based on detected emotions.

Requirements: 5.1.1, 5.1.2, 5.1.8
"""

import logging
from typing import List, Optional
from models import EmotionResult

logger = logging.getLogger("ai_waifu.emotion_engine")


class EmotionEngine:
    """
    Detects emotional keywords and jealousy triggers in user messages.
    
    The EmotionEngine analyzes user input for emotional content and updates
    the user's mood and affection level accordingly. It prioritizes jealousy
    detection and stores emotional events in memory.
    """
    
    def __init__(self, firestore_client):
        """
        Initialize the Emotion Engine.
        
        Args:
            firestore_client: Firebase Firestore client for persistence
        """
        self.firestore = firestore_client
        
        # Jealousy keywords that trigger possessive/jealous mood
        # Requirements: 5.1.2
        self.jealousy_keywords = [
            "she", "her", "another girl", "my girlfriend", 
            "my crush", "i like her", "she's cute",
            "talking to someone else", "other girl", "new girl"
        ]
        
        # Emotion keywords for detecting different emotional states
        # Requirements: 5.1.8
        self.emotion_keywords = {
            "happy": ["happy", "excited", "great", "awesome", "love"],
            "sad": ["sad", "depressed", "down", "upset", "hurt"],
            "angry": ["angry", "mad", "furious", "annoyed"],
            "vulnerable": ["scared", "worried", "anxious", "nervous"]
        }
    
    def check_jealousy(self, message: str) -> bool:
        """
        Check if message contains jealousy triggers.
        
        Args:
            message: User's message text
            
        Returns:
            True if jealousy keywords are detected, False otherwise
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.jealousy_keywords)
    
    def detect_emotions(self, message: str, user_id: str) -> EmotionResult:
        """
        Analyze message for emotional content and triggers.
        
        This method checks for jealousy first (highest priority), then checks
        for other emotional keywords. It returns the detected mood, affection
        delta, and trigger keywords.
        
        Args:
            message: User's message text
            user_id: User identifier
            
        Returns:
            EmotionResult with detected_mood, affection_delta, triggers
        """
        message_lower = message.lower()
        detected_mood: Optional[str] = None
        affection_delta = 0
        triggers: List[str] = []
        
        # Check jealousy first (highest priority)
        # Requirements: 5.1.2, 5.1.3, 5.1.4
        if self.check_jealousy(message):
            detected_mood = "jealous"
            affection_delta = -2
            triggers = [kw for kw in self.jealousy_keywords if kw in message_lower]
            logger.info(f"Jealousy detected for user {user_id}: triggers={triggers}, affection_delta={affection_delta}")
        else:
            # Check other emotion keywords
            # Requirements: 5.1.8, 5.1.9
            for mood, keywords in self.emotion_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_mood = mood
                    triggers = [kw for kw in keywords if kw in message_lower]
                    logger.info(f"Emotion detected for user {user_id}: mood={mood}, triggers={triggers}")
                    break
        
        if not detected_mood:
            logger.debug(f"No emotional keywords detected for user {user_id}")
        
        return EmotionResult(
            detected_mood=detected_mood,
            affection_delta=affection_delta,
            triggers=triggers
        )
    
    def update_mood(self, user_id: str, mood: str, affection_delta: int):
        """
        Persist mood and affection changes to Firestore.
        
        This method updates the user's mood and affection level in Firestore
        and stores the emotional event in the emotional_memory array.
        
        Args:
            user_id: User identifier
            mood: New mood state
            affection_delta: Change in affection level
        """
        from datetime import datetime
        from modules import firestore_operations
        from models import EmotionalMemoryEntry
        
        # Get current user data
        user_data = firestore_operations.get_user_data(self.firestore, user_id)
        
        if user_data is None:
            # User doesn't exist yet, skip update
            return
        
        # Calculate new affection level
        new_affection = user_data.affection_level + affection_delta
        # Ensure affection stays within 0-100 range
        new_affection = max(0, min(100, new_affection))
        
        # Create emotional memory entry
        emotional_event = EmotionalMemoryEntry(
            timestamp=datetime.now(),
            event_type=mood,
            trigger=f"Mood changed to {mood}",
            mood_change=mood,
            affection_delta=affection_delta
        )
        
        # Get current emotional memory and append new event
        updated_emotional_memory = user_data.emotional_memory + [emotional_event]
        
        # Update Firestore with new mood, affection level, and emotional memory
        updates = {
            "mood": mood,
            "affection_level": new_affection,
            "emotional_memory": updated_emotional_memory
        }
        
        firestore_operations.update_user_data(self.firestore, user_id, updates)
