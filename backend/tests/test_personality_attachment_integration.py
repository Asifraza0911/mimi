"""
Integration test for Personality System with Attachment Style Engine.

Tests that attachment behaviors are properly injected into prompts
and that possessive+jealousy combinations are intensified.
"""

import pytest
from unittest.mock import MagicMock

from modules.personality_system import PersonalitySystem
from modules.attachment_style_engine import AttachmentStyleEngine


def test_personality_system_uses_attachment_instructions():
    """Test that PersonalitySystem properly injects attachment instructions into prompts."""
    ps = PersonalitySystem()
    
    # Test with each attachment state
    attachment_states = ["avoidant", "anxious", "secure", "possessive"]
    
    for state in attachment_states:
        user_data = {
            "affection_level": 50,
            "mood": "neutral",
            "relationship_stage": "friend",
            "attachment_state": state,
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="How are you?",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        # Verify attachment state is in prompt
        assert f"Attachment Style: {state}" in prompt
        assert "ATTACHMENT BEHAVIOR" in prompt
        
        # Verify attachment instructions are present
        instruction = ps.get_attachment_instructions(state)
        # Check that key words from instruction appear in prompt
        assert any(word in prompt.lower() for word in instruction.lower().split())


def test_personality_system_intensifies_possessive_jealousy():
    """Test that possessive+jealousy combination triggers intensification."""
    ps = PersonalitySystem()
    
    # Test possessive + jealous
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
        recent_context=[]
    )
    
    # Verify intensification is present
    assert "POSSESSIVE JEALOUSY MODE" in prompt
    assert "Intensify possessive responses" in prompt
    assert "territorial" in prompt.lower()
    assert "exclusive attention" in prompt.lower()


def test_personality_system_no_intensification_without_both_conditions():
    """Test that intensification only occurs with both possessive AND jealous."""
    ps = PersonalitySystem()
    
    # Test possessive but not jealous
    user_data_1 = {
        "affection_level": 90,
        "mood": "happy",
        "relationship_stage": "attached",
        "attachment_state": "possessive",
        "long_term_memory": []
    }
    
    prompt_1 = ps.construct_prompt(
        user_message="I love you",
        user_data=user_data_1,
        similar_memories=[],
        recent_context=[]
    )
    
    assert "POSSESSIVE JEALOUSY MODE" not in prompt_1
    
    # Test jealous but not possessive
    user_data_2 = {
        "affection_level": 50,
        "mood": "jealous",
        "relationship_stage": "friend",
        "attachment_state": "anxious",
        "long_term_memory": []
    }
    
    prompt_2 = ps.construct_prompt(
        user_message="I was talking to someone",
        user_data=user_data_2,
        similar_memories=[],
        recent_context=[]
    )
    
    assert "POSSESSIVE JEALOUSY MODE" not in prompt_2


def test_attachment_engine_integration_with_personality_system():
    """Test that AttachmentStyleEngine and PersonalitySystem work together."""
    mock_firestore = MagicMock()
    attachment_engine = AttachmentStyleEngine(mock_firestore)
    ps = PersonalitySystem()
    
    # Test different affection levels
    test_cases = [
        (15, "avoidant"),
        (45, "anxious"),
        (70, "secure"),
        (90, "possessive")
    ]
    
    for affection, expected_state in test_cases:
        # Determine attachment state using engine
        attachment_state = attachment_engine.determine_attachment_state(affection)
        assert attachment_state == expected_state
        
        # Get instructions from both systems
        engine_instructions = attachment_engine.get_attachment_instructions(attachment_state)
        ps_instructions = ps.get_attachment_instructions(attachment_state)
        
        # Instructions should be the same
        assert engine_instructions == ps_instructions
        
        # Verify instructions are injected into prompt
        user_data = {
            "affection_level": affection,
            "mood": "neutral",
            "relationship_stage": "friend",
            "attachment_state": attachment_state,
            "long_term_memory": []
        }
        
        prompt = ps.construct_prompt(
            user_message="Hi",
            user_data=user_data,
            similar_memories=[],
            recent_context=[]
        )
        
        assert f"Attachment Style: {attachment_state}" in prompt
        assert "ATTACHMENT BEHAVIOR" in prompt


def test_attachment_state_parameter_override():
    """Test that attachment_state parameter overrides user_data value."""
    ps = PersonalitySystem()
    
    user_data = {
        "affection_level": 50,
        "mood": "neutral",
        "relationship_stage": "friend",
        "attachment_state": "anxious",  # This should be overridden
        "long_term_memory": []
    }
    
    # Override with possessive
    prompt = ps.construct_prompt(
        user_message="Hi",
        user_data=user_data,
        similar_memories=[],
        recent_context=[],
        attachment_state="possessive"  # Override
    )
    
    # Should use the override value
    assert "Attachment Style: possessive" in prompt
    assert "Attachment Style: anxious" not in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
