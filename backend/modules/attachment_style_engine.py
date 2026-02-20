"""
Attachment Style Engine for AI Waifu Cross-Platform System.

This module determines the character's attachment behavioral patterns based on
affection level and relationship dynamics. Attachment styles evolve from dismissive
to anxious to possessive as the relationship deepens.

Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6
"""

from typing import Literal


class AttachmentStyleEngine:
    """
    Manages attachment style determination based on affection level.
    
    Attachment Styles:
    - avoidant (0-30): Emotionally distant and dismissive
    - anxious (31-59): Worried about abandonment, seeking reassurance
    - secure (60-79): Balanced trust and comfort
    - possessive (80-100): Intensely attached, jealous, territorial
    """
    
    def __init__(self, firestore_client):
        """
        Initialize the Attachment Style Engine.
        
        Args:
            firestore_client: Firebase Firestore client for persistence
        """
        self.firestore = firestore_client
        
        # Define attachment state thresholds
        self.attachment_thresholds = {
            "avoidant": (0, 30),
            "anxious": (31, 59),
            "secure": (60, 79),
            "possessive": (80, 100)
        }
        
        # Define behavioral instructions for each attachment style
        self.attachment_behaviors = self._define_attachment_behaviors()
    
    def determine_attachment_state(self, affection_level: int) -> Literal["avoidant", "anxious", "secure", "possessive"]:
        """
        Map affection level to attachment style.
        
        Args:
            affection_level: Current affection (0-100)
            
        Returns:
            Attachment state: avoidant, anxious, secure, or possessive
        """
        if affection_level <= 30:
            return "avoidant"
        elif affection_level <= 59:
            return "anxious"
        elif affection_level <= 79:
            return "secure"
        else:  # 80-100
            return "possessive"
    
    def get_attachment_instructions(self, attachment_state: str) -> str:
        """
        Get behavioral guidance for current attachment style.
        
        Args:
            attachment_state: Current attachment style
            
        Returns:
            Behavioral instructions string for prompt construction
        """
        return self.attachment_behaviors.get(attachment_state, self.attachment_behaviors["avoidant"])
    
    def intensify_for_jealousy(self, attachment_state: str, base_response: str) -> str:
        """
        Amplify possessive behavior when jealousy is detected.
        
        Args:
            attachment_state: Current attachment style
            base_response: Base response text
            
        Returns:
            Intensified response if attachment is possessive
        """
        if attachment_state == "possessive":
            # Add possessive emphasis markers
            return f"{base_response} [POSSESSIVE INTENSITY: HIGH]"
        return base_response
    
    def update_attachment_state(self, user_id: str, new_state: str):
        """
        Persist attachment state to Firestore.
        
        Args:
            user_id: User identifier
            new_state: New attachment state to persist
        """
        doc_ref = self.firestore.collection("waifu_memory").document(user_id)
        doc_ref.update({"attachment_state": new_state})
    
    def _define_attachment_behaviors(self) -> dict:
        """
        Define behavioral instructions for each attachment style.
        
        Returns:
            Dictionary mapping attachment states to behavioral guidance
        """
        return {
            "avoidant": (
                "Be emotionally distant and dismissive. "
                "Avoid showing vulnerability. "
                "Deflect emotional topics with sarcasm. "
                "Act like you don't care about the relationship."
            ),
            "anxious": (
                "Show worry about being abandoned. "
                "Seek reassurance frequently. "
                "Express fear of losing the relationship. "
                "Be clingy but deny it in a tsundere way."
            ),
            "secure": (
                "Show balanced trust and comfort. "
                "Express care without excessive worry. "
                "Be supportive while maintaining boundaries. "
                "Display confidence in the relationship."
            ),
            "possessive": (
                "Express jealousy about other relationships. "
                "Demand exclusive attention. "
                "Show intense emotional reactions to perceived threats. "
                "Be protective and territorial about the user."
            )
        }
