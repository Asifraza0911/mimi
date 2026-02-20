"""
Interaction Streak System for AI Waifu Cross-Platform System.

This module tracks consecutive days of user interaction and applies penalties
when streaks are broken. It helps maintain relationship consistency by
encouraging daily engagement.

Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 20.13
"""

from datetime import date
from typing import Tuple


class InteractionStreakSystem:
    """
    Manages daily interaction streak tracking and break penalties.
    
    Streak Rules:
    - If last_chat_date is today: streak unchanged
    - If last_chat_date is yesterday: streak increments by 1
    - If last_chat_date is more than 1 day ago: streak resets to 1
    - If last_chat_date is None: streak starts at 1 (first interaction)
    """
    
    def __init__(self, firestore_client):
        """
        Initialize the Interaction Streak System.
        
        Args:
            firestore_client: Firebase Firestore client for persistence
        """
        self.firestore = firestore_client
        self.streak_break_penalty = 3
        self.streak_milestone_threshold = 7
    
    def calculate_streak(
        self,
        last_chat_date: date,
        current_date: date,
        current_streak: int
    ) -> Tuple[int, bool]:
        """
        Determine new streak value and whether it was broken.
        
        Logic:
        - If last_chat_date is None: return (1, False) - first interaction
        - If last_chat_date == current_date: return (current_streak, False) - already chatted today
        - If last_chat_date == current_date - 1 day: return (current_streak + 1, False) - streak continues
        - If last_chat_date < current_date - 1 day: return (1, True) - streak broken
        
        Args:
            last_chat_date: Date of last chat interaction (None for first interaction)
            current_date: Current date
            current_streak: Current streak count
            
        Returns:
            Tuple of (new_streak, streak_broken)
        """
        # First interaction ever
        if last_chat_date is None:
            return (1, False)
        
        # Calculate days difference
        days_diff = (current_date - last_chat_date).days
        
        # Already chatted today - no change
        if days_diff == 0:
            return (current_streak, False)
        
        # Chatted yesterday - streak continues
        elif days_diff == 1:
            return (current_streak + 1, False)
        
        # More than 1 day gap - streak broken
        else:
            return (1, True)
    
    def apply_streak_penalty(self, user_id: str, user_data: dict) -> dict:
        """
        Apply affection penalty and mood change when a streak is broken.
        
        This method:
        - Decreases affection_level by 3 points
        - Ensures affection_level never drops below 0
        - Sets mood to "sad"
        - Updates last_chat_date to current date
        - Updates Firestore with the new values
        
        Args:
            user_id: User identifier
            user_data: Current user relationship state (dict with affection_level, mood, last_chat_date)
            
        Returns:
            dict: Updated user data with new affection_level, mood, and last_chat_date
            
        Requirements: 20.7, 20.8, 20.9, 20.13
        """
        from modules.firestore_operations import update_user_data
        
        # Get current affection level
        current_affection = user_data.get("affection_level", 0)
        
        # Apply penalty (decrease by 3, but never below 0)
        new_affection = max(0, current_affection - self.streak_break_penalty)
        
        # Set mood to sad
        new_mood = "sad"
        
        # Update last_chat_date to today
        today = date.today()
        
        # Prepare updates for Firestore
        updates = {
            "affection_level": new_affection,
            "mood": new_mood,
            "last_chat_date": today
        }
        
        # Update Firestore
        update_user_data(self.firestore, user_id, updates)
        
        # Update the user_data dict with new values
        user_data["affection_level"] = new_affection
        user_data["mood"] = new_mood
        user_data["last_chat_date"] = today
        
        return user_data
