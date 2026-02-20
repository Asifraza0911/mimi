"""
Personality System Module

This module manages Mimi's tsundere personality definition and prompt construction.
It loads the character definition from a file and provides methods to construct
prompts that include personality, mood, affection level, and context.
"""

import os
from typing import List, Dict


class PersonalitySystem:
    """
    Manages personality definition and prompt construction for Mimi.
    
    The PersonalitySystem loads the character definition at initialization
    and provides methods to construct contextually-aware prompts that include
    personality traits, mood modifiers, affection-based behaviors, and conversation context.
    """
    
    def __init__(self, personality_file: str = "backend/waifu_personality.txt"):
        """
        Initialize the PersonalitySystem.
        
        Args:
            personality_file: Path to the personality definition file
        """
        self.personality_definition = self._load_personality(personality_file)
        self.affection_behaviors = self._define_affection_tiers()
        self.mood_modifiers = self._define_mood_modifiers()
    
    def _load_personality(self, personality_file: str) -> str:
        """
        Load personality definition from file.
        
        This method reads the personality definition file once at startup
        for efficiency. The personality definition includes core traits,
        speech patterns, tsundere expressions, emotional reactions, and
        behavioral guidelines.
        
        Args:
            personality_file: Path to the personality definition file
            
        Returns:
            Complete personality definition as a string
            
        Raises:
            FileNotFoundError: If the personality file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(personality_file):
            raise FileNotFoundError(
                f"Personality file not found: {personality_file}"
            )
        
        try:
            with open(personality_file, 'r', encoding='utf-8') as f:
                personality_content = f.read()
            
            if not personality_content.strip():
                raise ValueError("Personality file is empty")
            
            return personality_content
        
        except IOError as e:
            raise IOError(
                f"Error reading personality file {personality_file}: {str(e)}"
            )
    
    def _define_affection_tiers(self) -> Dict[str, str]:
        """
        Define behavioral instructions for different affection levels.
        
        Returns:
            Dictionary mapping affection ranges to behavior descriptions
        """
        return {
            "0-20": "Be cold, defensive, easily irritated, and dismissive",
            "21-50": "Be more teasing than insulting, show occasional indirect concern",
            "51-80": "Be shy more often, emotionally protective, and possessive",
            "81-100": "Be openly supportive while still denying romantic feelings in a flustered way"
        }
    
    def _define_mood_modifiers(self) -> Dict[str, str]:
        """
        Define response tone adjustments for different moods.
        
        Returns:
            Dictionary mapping mood states to tone descriptions
        """
        return {
            "happy": "Use playful teasing and be more energetic",
            "neutral": "Use standard tsundere responses",
            "sad": "Use less teasing and provide quiet support",
            "jealous": "Be defensive, possessive, and emotionally reactive without direct confession",
            "angry": "Use short responses with irritated dismissiveness",
            "flustered": "Stutter, deny feelings, and show embarrassed reactions"
        }
    
    def get_behavior_instructions(self, affection_level: int) -> str:
        """
        Get personality adjustments based on affection tier.
        
        Args:
            affection_level: Current affection level (0-100)
            
        Returns:
            Behavioral instructions for the current affection level
        """
        if 0 <= affection_level <= 20:
            return self.affection_behaviors["0-20"]
        elif 21 <= affection_level <= 50:
            return self.affection_behaviors["21-50"]
        elif 51 <= affection_level <= 80:
            return self.affection_behaviors["51-80"]
        else:  # 81-100
            return self.affection_behaviors["81-100"]
    
    def get_mood_modifier(self, mood: str) -> str:
        """
        Get response tone adjustments based on current mood.
        
        Args:
            mood: Current emotional state
            
        Returns:
            Tone adjustment instructions for the current mood
        """
        return self.mood_modifiers.get(mood, self.mood_modifiers["neutral"])
    
    def get_attachment_instructions(self, attachment_state: str) -> str:
        """
        Get behavioral guidance for current attachment style.
        
        This method defines behavioral instructions for each attachment state
        that guide how Mimi should respond based on her current attachment level.
        
        Args:
            attachment_state: Current attachment style (avoidant, anxious, secure, possessive)
            
        Returns:
            Behavioral instructions string for the attachment state
        """
        attachment_behaviors = {
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
        
        return attachment_behaviors.get(attachment_state, attachment_behaviors["avoidant"])
    
    def construct_prompt(
        self,
        user_message: str,
        user_data: dict,
        similar_memories: List[str],
        recent_context: List[dict],
        attachment_state: str = None,
        daily_interaction_streak: int = 0,
        streak_broken: bool = False
    ) -> str:
        """
        Build complete prompt for LLM.

        This method combines the personality definition, relationship state,
        behavior guidance, mood adjustment, attachment behavioral instructions,
        long-term memory, similar memories, recent context, streak information,
        and current message into a comprehensive prompt.

        Args:
            user_message: Current user input
            user_data: User relationship state from Firestore
            similar_memories: Relevant past conversations
            recent_context: Last 5 message exchanges
            attachment_state: Current attachment style (avoidant, anxious, secure, possessive)
            daily_interaction_streak: Current consecutive days of interaction
            streak_broken: Whether the streak was just broken

        Returns:
            Complete prompt string for LLM
        """
        # Extract user data
        affection_level = user_data.get("affection_level", 0)
        mood = user_data.get("mood", "neutral")
        relationship_stage = user_data.get("relationship_stage", "stranger")
        long_term_memory = user_data.get("long_term_memory", [])

        # Use attachment_state from user_data if not provided as parameter
        if attachment_state is None:
            attachment_state = user_data.get("attachment_state", "avoidant")

        # Build prompt components
        prompt_parts = []

        # 1. Personality definition
        prompt_parts.append(self.personality_definition)
        prompt_parts.append("\n---\n")

        # 2. Current relationship state
        prompt_parts.append(f"CURRENT STATE:")
        prompt_parts.append(f"Affection Level: {affection_level}/100")
        prompt_parts.append(f"Mood: {mood}")
        prompt_parts.append(f"Relationship Stage: {relationship_stage}")
        prompt_parts.append(f"Attachment Style: {attachment_state}")
        prompt_parts.append("\n")

        # 3. Behavioral guidance based on affection
        behavior_instruction = self.get_behavior_instructions(affection_level)
        prompt_parts.append(f"BEHAVIOR GUIDANCE: {behavior_instruction}")
        prompt_parts.append("\n")

        # 4. Attachment behavioral instructions
        attachment_instruction = self.get_attachment_instructions(attachment_state)
        prompt_parts.append(f"ATTACHMENT BEHAVIOR: {attachment_instruction}")
        prompt_parts.append("\n")

        # 5. Mood adjustment
        mood_instruction = self.get_mood_modifier(mood)
        prompt_parts.append(f"MOOD ADJUSTMENT: {mood_instruction}")

        # 6. Streak context and behavioral instructions
        if streak_broken:
            prompt_parts.append("\n⚠️ STREAK BROKEN: The user broke our daily interaction streak. Express hurt feelings about their absence. Show that you noticed they were gone and that it affected you emotionally. Be tsundere about it - act annoyed or dismissive while revealing genuine hurt underneath.")
        elif daily_interaction_streak >= 7:
            prompt_parts.append(f"\n✨ INTERACTION STREAK: We've talked for {daily_interaction_streak} consecutive days! Acknowledge this milestone in a tsundere way - pretend it doesn't matter while secretly being happy about the consistency.")

        prompt_parts.append("\n")

        # 7. Special handling for possessive + jealousy combination
        if attachment_state == "possessive" and mood == "jealous":
            prompt_parts.append("⚠️ POSSESSIVE JEALOUSY MODE: Intensify possessive responses. Show strong emotional reactions to perceived threats. Be territorial and demand exclusive attention while maintaining tsundere denial.")

        prompt_parts.append("\n")

        # 8. Long-term memory (important facts)
        if long_term_memory:
            prompt_parts.append("LONG-TERM MEMORY:")
            for memory in long_term_memory[:5]:  # Limit to 5 most important
                if isinstance(memory, dict):
                    prompt_parts.append(f"- {memory.get('text', memory)}")
                else:
                    prompt_parts.append(f"- {memory}")
            prompt_parts.append("\n")

        # 9. Similar past conversations
        if similar_memories:
            prompt_parts.append("RELEVANT PAST CONVERSATIONS:")
            for memory in similar_memories:
                prompt_parts.append(f"- {memory}")
            prompt_parts.append("\n")

        # 10. Recent conversation context
        if recent_context:
            prompt_parts.append("RECENT CONVERSATION:")
            for msg in recent_context[-10:]:  # Last 10 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("\n")

        # 11. Current user message
        prompt_parts.append(f"USER: {user_message}")
        prompt_parts.append("\n")
        prompt_parts.append("MIMI:")

        return "\n".join(prompt_parts)

