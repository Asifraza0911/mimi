"""
Integration test for Attachment Style Engine integration with Relationship Engine.

Tests that attachment state is properly determined and persisted when
relationship updates occur.
"""

import pytest
from unittest.mock import Mock, MagicMock

from models import UserData
from modules.relationship_engine import RelationshipEngine
from modules.attachment_style_engine import AttachmentStyleEngine


def test_attachment_state_integration():
    """Test that attachment state is determined and included in relationship updates."""
    # Setup
    mock_firestore = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create engines
    attachment_engine = AttachmentStyleEngine(mock_firestore)
    relationship_engine = RelationshipEngine(mock_firestore, attachment_engine)
    
    # Test avoidant state (0-30)
    user_data = UserData(
        user_id="test_user",
        affection_level=15,
        trust_level=5,
        mood="neutral",
        relationship_stage="stranger",
        attachment_state="avoidant"
    )
    
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="hello",
        current_state=user_data
    )
    
    assert update.attachment_state == "avoidant", "Should be avoidant at low affection"
    
    # Test anxious state (31-59)
    user_data.affection_level = 45
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="you are nice",
        current_state=user_data
    )
    
    assert update.attachment_state == "anxious", "Should be anxious at mid-low affection"
    
    # Test secure state (60-79)
    user_data.affection_level = 70
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="you are great",
        current_state=user_data
    )
    
    assert update.attachment_state == "secure", "Should be secure at mid-high affection"
    
    # Test possessive state (80-100)
    user_data.affection_level = 85
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="you are amazing",
        current_state=user_data
    )
    
    assert update.attachment_state == "possessive", "Should be possessive at high affection"


def test_attachment_state_persistence():
    """Test that attachment state is persisted to Firestore."""
    # Setup
    mock_firestore = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create engines
    attachment_engine = AttachmentStyleEngine(mock_firestore)
    relationship_engine = RelationshipEngine(mock_firestore, attachment_engine)
    
    # Create user data
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend",
        attachment_state="avoidant"
    )
    
    # Update relationship
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="you are wonderful",
        current_state=user_data
    )
    
    # Persist the update
    relationship_engine.persist_update("test_user", update)
    
    # Verify that attachment_state was included in the update
    assert update.attachment_state is not None, "Attachment state should be set"
    
    # Verify that update_user_data was called with attachment_state
    mock_document.update.assert_called_once()
    call_args = mock_document.update.call_args[0][0]
    assert "attachment_state" in call_args, "Attachment state should be persisted"


def test_attachment_state_without_engine():
    """Test that relationship engine works without attachment engine (backward compatibility)."""
    # Setup
    mock_firestore = MagicMock()
    
    # Create relationship engine without attachment engine
    relationship_engine = RelationshipEngine(mock_firestore)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend",
        attachment_state="avoidant"
    )
    
    # Update relationship
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message="hello",
        current_state=user_data
    )
    
    # Should work but attachment_state should be None
    assert update.attachment_state is None, "Attachment state should be None without engine"


def test_attachment_state_progression():
    """Test attachment state changes as affection increases."""
    # Setup
    mock_firestore = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create engines
    attachment_engine = AttachmentStyleEngine(mock_firestore)
    relationship_engine = RelationshipEngine(mock_firestore, attachment_engine)
    
    # Start at affection level that will reach anxious threshold
    user_data = UserData(
        user_id="test_user",
        affection_level=20,
        trust_level=5,
        mood="neutral",
        relationship_stage="stranger",
        attachment_state="avoidant"
    )
    
    # Send multiple compliments to increase affection
    # Need to go from 20 to 31+ (anxious threshold)
    # 4 compliments: 20 + 4*3 = 32
    compliments = [
        "you are beautiful",
        "you are amazing",
        "you are wonderful",
        "I appreciate you"
    ]
    
    attachment_states = []
    affection_levels = []
    
    for compliment in compliments:
        update = relationship_engine.update_relationship(
            user_id="test_user",
            message=compliment,
            current_state=user_data
        )
        
        attachment_states.append(update.attachment_state)
        affection_levels.append(update.affection_level)
        
        # Update user data for next iteration
        user_data.affection_level = update.affection_level
        user_data.trust_level = update.trust_level
        user_data.mood = update.mood
        user_data.relationship_stage = update.relationship_stage
        user_data.attachment_state = update.attachment_state
    
    # Verify progression from avoidant to anxious
    assert attachment_states[0] == "avoidant", f"Should start as avoidant (affection: {affection_levels[0]})"
    assert "anxious" in attachment_states, f"Should progress to anxious. States: {attachment_states}, Affection: {affection_levels}"
    assert user_data.affection_level > 30, f"Final affection should be above 30, got {user_data.affection_level}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
