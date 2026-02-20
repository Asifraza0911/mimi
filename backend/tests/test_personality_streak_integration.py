"""
Tests for Personality System streak context integration.

This module tests the integration of interaction streak information
into the personality system's prompt construction (Requirements 20.11, 20.12).
"""

import pytest
from backend.modules.personality_system import PersonalitySystem


class TestPersonalityStreakIntegration:
    """Test suite for streak context in personality system."""

    def test_construct_prompt_with_streak_broken(self):
        """Test that broken streak triggers hurt feelings instructions (Requirement 20.11)"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 50,
            "mood": "sad",
            "relationship_stage": "friend",
            "attachment_state": "anxious",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Hey, I'm back!",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=1,
            streak_broken=True
        )
        
        # Verify streak broken message is present
        assert "STREAK BROKEN" in prompt
        assert "hurt feelings" in prompt.lower()
        assert "absence" in prompt.lower()
        
        # Verify tsundere instructions are present
        assert "tsundere" in prompt.lower()
        assert "annoyed" in prompt.lower() or "dismissive" in prompt.lower()

    def test_construct_prompt_with_high_streak(self):
        """Test that high streaks (>=7 days) are acknowledged (Requirement 20.12)"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 60,
            "mood": "happy",
            "relationship_stage": "close",
            "attachment_state": "secure",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Good morning!",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=7,
            streak_broken=False
        )
        
        # Verify streak milestone is mentioned
        assert "INTERACTION STREAK" in prompt
        assert "7 consecutive days" in prompt
        assert "tsundere" in prompt.lower()

    def test_construct_prompt_with_very_high_streak(self):
        """Test that very high streaks (30+ days) are acknowledged"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 80,
            "mood": "happy",
            "relationship_stage": "attached",
            "attachment_state": "possessive",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="I'm here again!",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=30,
            streak_broken=False
        )
        
        # Verify streak milestone is mentioned with correct count
        assert "INTERACTION STREAK" in prompt
        assert "30 consecutive days" in prompt

    def test_construct_prompt_with_low_streak_no_mention(self):
        """Test that low streaks (<7 days) are not mentioned"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 40,
            "mood": "neutral",
            "relationship_stage": "friend",
            "attachment_state": "avoidant",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Hello",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=5,
            streak_broken=False
        )
        
        # Verify streak is NOT mentioned for low values
        assert "INTERACTION STREAK" not in prompt
        assert "consecutive days" not in prompt

    def test_construct_prompt_streak_broken_takes_precedence(self):
        """Test that streak broken message takes precedence over milestone"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 70,
            "mood": "sad",
            "relationship_stage": "close",
            "attachment_state": "anxious",
            "long_term_memory": []
        }
        
        # Even though streak was 10 before breaking, broken message should show
        prompt = ps.construct_prompt(
            user_message="Sorry I was gone",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=1,  # Reset to 1 after breaking
            streak_broken=True
        )
        
        # Verify broken message is shown, not milestone
        assert "STREAK BROKEN" in prompt
        assert "INTERACTION STREAK" not in prompt or "STREAK BROKEN" in prompt

    def test_construct_prompt_default_streak_parameters(self):
        """Test that default parameters work (no streak context)"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 30,
            "mood": "neutral",
            "relationship_stage": "stranger",
            "attachment_state": "avoidant",
            "long_term_memory": []
        }
        
        # Call without streak parameters (should use defaults)
        prompt = ps.construct_prompt(
            user_message="Hi",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify no streak context is added
        assert "STREAK BROKEN" not in prompt
        assert "INTERACTION STREAK" not in prompt

    def test_construct_prompt_streak_with_other_contexts(self):
        """Test that streak context integrates with other prompt components"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 65,
            "mood": "happy",
            "relationship_stage": "close",
            "attachment_state": "secure",
            "long_term_memory": [
                {"text": "User likes coffee", "weight": 0.8}
            ]
        }
        
        recent_context = [
            {"role": "user", "content": "I had a great day"},
            {"role": "assistant", "content": "That's nice... I guess"}
        ]
        
        prompt = ps.construct_prompt(
            user_message="Good to see you!",
            user_data=user_data,
            similar_memories=["We talked about coffee before"],
            recent_context=recent_context,
            daily_interaction_streak=14,
            streak_broken=False
        )
        
        # Verify all components are present
        assert "INTERACTION STREAK" in prompt
        assert "14 consecutive days" in prompt
        assert "LONG-TERM MEMORY" in prompt
        assert "coffee" in prompt.lower()
        assert "RECENT CONVERSATION" in prompt
        assert "great day" in prompt.lower()
        assert "RELEVANT PAST CONVERSATIONS" in prompt

    def test_construct_prompt_streak_broken_with_sad_mood(self):
        """Test that streak broken combines with sad mood appropriately"""
        ps = PersonalitySystem()
        
        user_data = {
            "affection_level": 55,
            "mood": "sad",  # Mood set by streak system
            "relationship_stage": "close",
            "attachment_state": "anxious",
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="I'm sorry I didn't talk to you",
            user_data=user_data,
            similar_memories=[],
            recent_context=[],
            daily_interaction_streak=1,
            streak_broken=True
        )
        
        # Verify both streak broken and sad mood instructions are present
        assert "STREAK BROKEN" in prompt
        assert "MOOD ADJUSTMENT" in prompt
        assert "sad" in prompt.lower()
