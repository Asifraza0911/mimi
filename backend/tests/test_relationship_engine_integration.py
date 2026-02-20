"""
Integration tests for Relationship Engine.

Tests the complete workflow of the Relationship Engine.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from models import UserData
from modules.relationship_engine import RelationshipEngine


def test_complete_relationship_progression_workflow():
    """Test complete workflow from stranger to attached."""
    # Setup
    mock_firestore = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    engine = RelationshipEngine(mock_firestore)
    
    # Start as stranger
    user_data = UserData(
        user_id="test_user",
        affection_level=10,
        trust_level=5,
        mood="neutral",
        relationship_stage="stranger"
    )
    
    # Send compliments to increase affection
    messages = [
        "you are beautiful",
        "I really appreciate you",
        "you're amazing",
        "thank you so much",
        "you are wonderful"
    ]
    
    for message in messages:
        update = engine.update_relationship(
            user_id="test_user",
            message=message,
            current_state=user_data
        )
        
        # Update user data for next iteration
        user_data.affection_level = update.affection_level
        user_data.trust_level = update.trust_level
        user_data.mood = update.mood
        user_data.relationship_stage = update.relationship_stage
    
    # After 5 compliments (+3 each = +15), should be at 25 affection (friend stage)
    assert user_data.affection_level >= 21, "Should have progressed to friend stage"
    assert user_data.relationship_stage == "friend", "Stage should be friend"
    assert user_data.mood == "flustered", "Should be flustered from compliments"


def test_vulnerability_increases_trust():
    """Test that sharing vulnerability increases trust."""
    mock_firestore = Mock()
    engine = RelationshipEngine(mock_firestore)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=30,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Share vulnerability
    update = engine.update_relationship(
        user_id="test_user",
        message="I'm feeling really scared and worried about everything",
        current_state=user_data
    )
    
    assert update.trust_level > 30, "Trust should increase"
    assert update.affection_level > 50, "Affection should also increase"
    assert update.mood == "sad", "Mood should be empathetic sad"


def test_rude_message_damages_relationship():
    """Test that rude messages decrease affection."""
    mock_firestore = Mock()
    engine = RelationshipEngine(mock_firestore)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=50,
        mood="happy",
        relationship_stage="friend"
    )
    
    # Send rude message
    update = engine.update_relationship(
        user_id="test_user",
        message="you are so annoying shut up",
        current_state=user_data
    )
    
    assert update.affection_level < 50, "Affection should decrease"
    assert update.mood == "angry", "Mood should be angry"


def test_stage_transitions():
    """Test all stage transitions."""
    mock_firestore = Mock()
    engine = RelationshipEngine(mock_firestore)
    
    # Test stranger stage (0-20)
    assert engine.determine_stage(0) == "stranger"
    assert engine.determine_stage(10) == "stranger"
    assert engine.determine_stage(20) == "stranger"
    
    # Test friend stage (21-50)
    assert engine.determine_stage(21) == "friend"
    assert engine.determine_stage(35) == "friend"
    assert engine.determine_stage(50) == "friend"
    
    # Test close stage (51-80)
    assert engine.determine_stage(51) == "close"
    assert engine.determine_stage(65) == "close"
    assert engine.determine_stage(80) == "close"
    
    # Test attached stage (81-100)
    assert engine.determine_stage(81) == "attached"
    assert engine.determine_stage(90) == "attached"
    assert engine.determine_stage(100) == "attached"


def test_sentiment_analysis_accuracy():
    """Test sentiment analysis for various message types."""
    mock_firestore = Mock()
    engine = RelationshipEngine(mock_firestore)
    
    # Test compliments
    sentiment = engine.analyze_sentiment("you are so beautiful")
    assert sentiment.sentiment_type == "compliment"
    
    # Test vulnerability
    sentiment = engine.analyze_sentiment("I'm feeling really scared")
    assert sentiment.sentiment_type == "vulnerability"
    
    # Test rude
    sentiment = engine.analyze_sentiment("you are stupid")
    assert sentiment.sentiment_type == "rude"
    
    # Test positive
    sentiment = engine.analyze_sentiment("this is great")
    assert sentiment.sentiment_type == "positive"
    
    # Test negative
    sentiment = engine.analyze_sentiment("this is terrible")
    assert sentiment.sentiment_type == "negative"
    
    # Test neutral
    sentiment = engine.analyze_sentiment("hello there")
    assert sentiment.sentiment_type == "neutral"


def test_affection_bounds():
    """Test that affection stays within 0-100 bounds."""
    mock_firestore = Mock()
    engine = RelationshipEngine(mock_firestore)
    
    # Test upper bound
    user_data = UserData(
        user_id="test_user",
        affection_level=98,
        trust_level=50,
        mood="neutral",
        relationship_stage="attached"
    )
    
    update = engine.update_relationship(
        user_id="test_user",
        message="you are beautiful and amazing",
        current_state=user_data
    )
    
    assert update.affection_level <= 100, "Affection should not exceed 100"
    
    # Test lower bound
    user_data.affection_level = 2
    
    update = engine.update_relationship(
        user_id="test_user",
        message="you are annoying and stupid",
        current_state=user_data
    )
    
    assert update.affection_level >= 0, "Affection should not go below 0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
