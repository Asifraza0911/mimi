"""
Tests for Personality System Module
"""

import pytest
import os
from backend.modules.personality_system import PersonalitySystem


class TestPersonalitySystem:
    """Test suite for PersonalitySystem class"""
    
    def test_personality_system_initialization(self):
        """Test that PersonalitySystem initializes correctly"""
        ps = PersonalitySystem()
        
        assert ps.personality_definition is not None
        assert len(ps.personality_definition) > 0
        assert "Mimi" in ps.personality_definition
        assert "tsundere" in ps.personality_definition.lower()
    
    def test_load_personality_success(self):
        """Test successful personality file loading"""
        ps = PersonalitySystem()
        
        # Verify personality content is loaded
        assert "CORE TRAITS" in ps.personality_definition
        assert "SPEECH PATTERNS" in ps.personality_definition
        assert "TSUNDERE EXPRESSIONS" in ps.personality_definition
        assert "EMOTIONAL REACTIONS" in ps.personality_definition
    
    def test_load_personality_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file"""
        with pytest.raises(FileNotFoundError):
            PersonalitySystem(personality_file="nonexistent_file.txt")
    
    def test_affection_tiers_defined(self):
        """Test that affection tier behaviors are defined"""
        ps = PersonalitySystem()
        
        assert "0-20" in ps.affection_behaviors
        assert "21-50" in ps.affection_behaviors
        assert "51-80" in ps.affection_behaviors
        assert "81-100" in ps.affection_behaviors
    
    def test_mood_modifiers_defined(self):
        """Test that mood modifiers are defined"""
        ps = PersonalitySystem()
        
        assert "happy" in ps.mood_modifiers
        assert "neutral" in ps.mood_modifiers
        assert "sad" in ps.mood_modifiers
        assert "jealous" in ps.mood_modifiers
        assert "angry" in ps.mood_modifiers
        assert "flustered" in ps.mood_modifiers
    
    def test_get_behavior_instructions_low_affection(self):
        """Test behavior instructions for low affection (0-20)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_behavior_instructions(10)
        assert "cold" in instruction.lower() or "defensive" in instruction.lower()
    
    def test_get_behavior_instructions_medium_affection(self):
        """Test behavior instructions for medium affection (21-50)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_behavior_instructions(35)
        assert "teasing" in instruction.lower()
    
    def test_get_behavior_instructions_high_affection(self):
        """Test behavior instructions for high affection (51-80)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_behavior_instructions(65)
        assert "shy" in instruction.lower() or "protective" in instruction.lower()
    
    def test_get_behavior_instructions_max_affection(self):
        """Test behavior instructions for max affection (81-100)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_behavior_instructions(90)
        assert "supportive" in instruction.lower()
    
    def test_get_mood_modifier_happy(self):
        """Test mood modifier for happy mood"""
        ps = PersonalitySystem()
        
        modifier = ps.get_mood_modifier("happy")
        assert "playful" in modifier.lower() or "energetic" in modifier.lower()
    
    def test_get_mood_modifier_jealous(self):
        """Test mood modifier for jealous mood"""
        ps = PersonalitySystem()
        
        modifier = ps.get_mood_modifier("jealous")
        assert "defensive" in modifier.lower() or "possessive" in modifier.lower()
    
    def test_get_mood_modifier_unknown_defaults_to_neutral(self):
        """Test that unknown mood defaults to neutral"""
        ps = PersonalitySystem()
        
        modifier = ps.get_mood_modifier("unknown_mood")
        neutral_modifier = ps.get_mood_modifier("neutral")
        assert modifier == neutral_modifier
    
    def test_construct_prompt_basic(self):
        """Test basic prompt construction"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 50,
            "mood": "neutral",
            "relationship_stage": "friend",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Hello!",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify prompt contains key components
        assert "Mimi" in prompt
        assert "Affection Level: 50/100" in prompt
        assert "Mood: neutral" in prompt
        assert "Relationship Stage: friend" in prompt
        assert "Hello!" in prompt
    
    def test_construct_prompt_with_memories(self):
        """Test prompt construction with long-term memories"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 70,
            "mood": "happy",
            "relationship_stage": "close",
            "long_term_memory": [
                {"text": "User likes pizza", "weight": 0.8},
                {"text": "User has a cat named Whiskers", "weight": 0.9}
            ]
        }
        
        prompt = ps.construct_prompt(
            user_message="What do you remember about me?",
            user_data=user_data,
            similar_memories=["We talked about your cat before"],
            recent_context=[
                {"role": "USER", "content": "Hi Mimi"},
                {"role": "MIMI", "content": "H-hey! What do you want?"}
            ]
        )
        
        # Verify memories are included
        assert "LONG-TERM MEMORY" in prompt
        assert "pizza" in prompt
        assert "Whiskers" in prompt
        assert "RELEVANT PAST CONVERSATIONS" in prompt
        assert "cat" in prompt
        assert "RECENT CONVERSATION" in prompt
    
    def test_construct_prompt_with_recent_context(self):
        """Test prompt construction with recent conversation context"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 30,
            "mood": "neutral",
            "relationship_stage": "friend",
            "long_term_memory": []
        }
        
        recent_context = [
            {"role": "USER", "content": "How are you?"},
            {"role": "MIMI", "content": "I'm fine, not that you care!"},
            {"role": "USER", "content": "I do care about you"}
        ]
        
        prompt = ps.construct_prompt(
            user_message="Really, I mean it",
            user_data=user_data,
            similar_memories=[],
            recent_context=recent_context
        )
        
        # Verify recent context is included
        assert "RECENT CONVERSATION" in prompt
        assert "How are you?" in prompt
        assert "I do care about you" in prompt
    
    def test_personality_loaded_once_at_startup(self):
        """Test that personality is loaded once at initialization (Requirement 4.10)"""
        ps = PersonalitySystem()
        
        # Store original personality definition
        original_definition = ps.personality_definition
        
        # Call methods that might trigger reload (they shouldn't)
        ps.get_behavior_instructions(50)
        ps.get_mood_modifier("happy")
        ps.construct_prompt("test", {"affection_level": 50, "mood": "neutral"}, [], [])
        
        # Verify personality definition hasn't changed (same object)
        assert ps.personality_definition is original_definition
    
    def test_get_attachment_instructions_avoidant(self):
        """Test attachment instructions for avoidant style (Requirement 18.9)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_attachment_instructions("avoidant")
        assert "distant" in instruction.lower() or "dismissive" in instruction.lower()
        assert "vulnerability" in instruction.lower()
    
    def test_get_attachment_instructions_anxious(self):
        """Test attachment instructions for anxious style (Requirement 18.10)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_attachment_instructions("anxious")
        assert "abandon" in instruction.lower() or "reassurance" in instruction.lower()
        assert "clingy" in instruction.lower()
    
    def test_get_attachment_instructions_secure(self):
        """Test attachment instructions for secure style (Requirement 18.11)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_attachment_instructions("secure")
        assert "trust" in instruction.lower() or "comfort" in instruction.lower()
        assert "balanced" in instruction.lower()
    
    def test_get_attachment_instructions_possessive(self):
        """Test attachment instructions for possessive style (Requirement 18.12)"""
        ps = PersonalitySystem()
        
        instruction = ps.get_attachment_instructions("possessive")
        assert "jealous" in instruction.lower() or "possessive" in instruction.lower()
        assert "territorial" in instruction.lower()
    
    def test_construct_prompt_with_attachment_state(self):
        """Test prompt construction includes attachment state (Requirement 18.8)"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 85,
            "mood": "neutral",
            "relationship_stage": "attached",
            "attachment_state": "possessive",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Who were you talking to?",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify attachment state is included
        assert "Attachment Style: possessive" in prompt
        assert "ATTACHMENT BEHAVIOR" in prompt
        assert "jealous" in prompt.lower() or "possessive" in prompt.lower()
    
    def test_construct_prompt_possessive_jealousy_intensification(self):
        """Test intensified possessive responses when jealousy detected (Requirement 18.13)"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 90,
            "mood": "jealous",
            "relationship_stage": "attached",
            "attachment_state": "possessive",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="I was talking to another girl",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            attachment_state="possessive"
        )
        
        # Verify possessive jealousy mode is activated
        assert "POSSESSIVE JEALOUSY MODE" in prompt
        assert "Intensify possessive responses" in prompt
        assert "territorial" in prompt.lower()
    
    def test_construct_prompt_attachment_state_from_user_data(self):
        """Test that attachment_state is extracted from user_data if not provided"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 65,
            "mood": "happy",
            "relationship_stage": "close",
            "attachment_state": "secure",
            "long_term_memory": []
        }
        
        # Don't pass attachment_state parameter
        prompt = ps.construct_prompt(
            user_message="How are you?",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify attachment state from user_data is used
        assert "Attachment Style: secure" in prompt
        assert "ATTACHMENT BEHAVIOR" in prompt
    
    def test_construct_prompt_attachment_state_defaults_to_avoidant(self):
        """Test that attachment_state defaults to avoidant if not in user_data"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 15,
            "mood": "neutral",
            "relationship_stage": "stranger",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Hi",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify default attachment state is avoidant
        assert "Attachment Style: avoidant" in prompt
        assert "ATTACHMENT BEHAVIOR" in prompt
    
    def test_construct_prompt_no_intensification_without_jealousy(self):
        """Test that possessive mode doesn't intensify without jealousy"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 90,
            "mood": "happy",  # Not jealous
            "relationship_stage": "attached",
            "attachment_state": "possessive",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="I love spending time with you",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify possessive jealousy mode is NOT activated
        assert "POSSESSIVE JEALOUSY MODE" not in prompt

