"""
Affection Decay Engine for AI Waifu Cross-Platform System.

This module implements time-based affection decay logic. When users don't
interact for extended periods, affection decreases and mood changes to reflect
the emotional impact of absence.

Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.7
"""

from datetime import datetime
from typing import Optional
from models import UserData, DecayResult


class AffectionDecayEngine:
    """
    Manages time-based affection decay and mood changes due to user absence.
    
    Decay Rules:
    - Affection decays by (hours_passed // 24) points when hours_passed > 24
    - Mood changes to "sad" when hours_passed > 72
    - Affection never drops below 0
    """
    
    def __init__(self, firestore_client):
        """
        Initialize the Affection Decay Engine.
        
        Args:
            firestore_client: Firebase Firestore client for persistence
        """
        self.firestore = firestore_client
        self.decay_threshold_hours = 24
        self.sad_threshold_hours = 72
    
    def calculate_decay(self, last_interaction: datetime, current_time: datetime) -> int:
        """
        Calculate affection decay amount based on time elapsed.
        
        Args:
            last_interaction: Timestamp of last user interaction
            current_time: Current timestamp
            
        Returns:
            Decay amount (number of affection points to subtract)
        """
        hours_passed = self._calculate_hours_passed(last_interaction, current_time)
        
        if hours_passed <= self.decay_threshold_hours:
            return 0
        
        # Decay by 1 point per 24 hours after the threshold
        decay_amount = hours_passed // 24
        return decay_amount
    
    def apply_decay(self, user_id: str, user_data: UserData) -> DecayResult:
        """
        Calculate and apply affection decay based on time since last interaction.
        
        This method:
        1. Calculates hours since last interaction
        2. Determines decay amount (hours_passed // 24)
        3. Decreases affection_level (ensuring it doesn't go below 0)
        4. Sets mood to "sad" if hours_passed > 72
        5. Persists changes to Firestore
        
        Args:
            user_id: User identifier
            user_data: Current user relationship state
            
        Returns:
            DecayResult with hours_passed, affection_delta, new_mood
        """
        current_time = datetime.now()
        hours_passed = self._calculate_hours_passed(user_data.last_interaction, current_time)
        
        # Calculate decay amount
        decay_amount = self.calculate_decay(user_data.last_interaction, current_time)
        
        # Apply decay to affection level (ensure it doesn't go below 0)
        new_affection = max(0, user_data.affection_level - decay_amount)
        affection_delta = new_affection - user_data.affection_level
        
        # Determine if mood should change to sad
        new_mood = None
        if hours_passed > self.sad_threshold_hours:
            new_mood = "sad"
        
        # Persist changes if decay occurred or mood changed
        if decay_amount > 0 or new_mood:
            self._persist_decay(user_id, new_affection, new_mood)
        
        return DecayResult(
            hours_passed=hours_passed,
            affection_delta=affection_delta,
            new_mood=new_mood
        )
    
    def _calculate_hours_passed(self, last_interaction: datetime, current_time: datetime) -> int:
        """
        Calculate hours elapsed since last interaction.
        
        Args:
            last_interaction: Timestamp of last interaction
            current_time: Current timestamp
            
        Returns:
            Number of hours passed (rounded down to integer)
        """
        time_delta = current_time - last_interaction
        hours_passed = int(time_delta.total_seconds() / 3600)
        return hours_passed
    
    def _persist_decay(self, user_id: str, new_affection: int, new_mood: Optional[str]):
        """
        Update Firestore with decayed affection and mood values.
        
        Args:
            user_id: User identifier
            new_affection: Updated affection level
            new_mood: Updated mood (if changed)
        """
        updates = {
            "affection_level": new_affection
        }
        
        if new_mood:
            updates["mood"] = new_mood
        
        # Update Firestore document
        doc_ref = self.firestore.collection("waifu_memory").document(user_id)
        doc_ref.update(updates)
