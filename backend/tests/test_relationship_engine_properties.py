"""
Property-based tests for Relationship Engine.

Tests relationship progression properties including:
- Compliment affection increase
- Vulnerability trust increase
- Rude message affection decrease
- Affection threshold stage transitions
- Sentiment-based mood updates
- Relationship state persistence
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, MagicMock
from datetime import datetime, date

from models import UserData, SentimentScore, RelationshipUpdate
from modules.relationship_engine import RelationshipEngine


# Helper functions to create instances (not fixtures for Hypothesis compatibility)
def create_mock_firestore():
    """Create mock Firestore client."""
    return Mock()


def create_relationship_engine():
    """Create RelationshipEngine instance with mock Firestore."""
    return RelationshipEngine(create_mock_firestore())


def create_base_user_data():
    """Create base UserData for testing."""
    return UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=50,
        mood="neutral",
        relationship_stage="friend"
    )


# Property 13: Compliment Affection Increase
# **Validates: Requirements 5.1**
@given(
    compliment_word=st.sampled_from([
        "beautiful", "pretty", "cute", "amazing", "wonderful",
        "love you", "like you", "appreciate", "thank you"
    ]),
    prefix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20),
    suffix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20)
)
@settings(max_examples=10, deadline=None)
def test_property_compliment_increases_affection(
    compliment_word,
    prefix,
    suffix
):
    """
    Property: Messages containing compliment keywords MUST increase affection.
    
    **Validates: Requirements 5.1**
    """
    relationship_engine = create_relationship_engine()
    base_user_data = create_base_user_data()
    
    # Construct message with compliment
    message = f"{prefix} {compliment_word} {suffix}".strip()
    
    initial_affection = base_user_data.affection_level
    
    # Update relationship
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message=message,
        current_state=base_user_data
    )
    
    # Assert affection increased
    assert update.affection_level > initial_affection, \
        f"Compliment '{compliment_word}' should increase affection"
    
    # Assert increase is positive (at least +1)
    affection_delta = update.affection_level - initial_affection
    assert affection_delta >= 1, \
        f"Affection delta should be at least +1, got {affection_delta}"


# Property 14: Vulnerability Trust Increase
# **Validates: Requirements 5.2**
@given(
    vulnerability_word=st.sampled_from([
        "scared", "worried", "anxious", "nervous", "afraid",
        "sad", "depressed", "lonely", "hurt", "struggling"
    ]),
    prefix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20),
    suffix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20)
)
@settings(max_examples=10, deadline=None)
def test_property_vulnerability_increases_trust(
    vulnerability_word,
    prefix,
    suffix
):
    """
    Property: Messages sharing emotional vulnerability MUST increase trust.
    
    **Validates: Requirements 5.2**
    """
    relationship_engine = create_relationship_engine()
    base_user_data = create_base_user_data()
    
    # Construct message with vulnerability
    message = f"{prefix} {vulnerability_word} {suffix}".strip()
    
    initial_trust = base_user_data.trust_level
    
    # Update relationship
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message=message,
        current_state=base_user_data
    )
    
    # Assert trust increased
    assert update.trust_level > initial_trust, \
        f"Vulnerability '{vulnerability_word}' should increase trust"
    
    # Assert increase is positive (at least +1)
    trust_delta = update.trust_level - initial_trust
    assert trust_delta >= 1, \
        f"Trust delta should be at least +1, got {trust_delta}"


# Property 15: Rude Message Affection Decrease
# **Validates: Requirements 5.4**
@given(
    rude_word=st.sampled_from([
        "stupid", "dumb", "annoying", "shut up", "hate you",
        "go away", "leave me alone", "boring", "useless"
    ]),
    prefix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20),
    suffix=st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')), max_size=20)
)
@settings(max_examples=10, deadline=None)
def test_property_rude_message_decreases_affection(
    rude_word,
    prefix,
    suffix
):
    """
    Property: Rude messages MUST decrease affection.
    
    **Validates: Requirements 5.4**
    """
    relationship_engine = create_relationship_engine()
    base_user_data = create_base_user_data()
    
    # Construct rude message
    message = f"{prefix} {rude_word} {suffix}".strip()
    
    initial_affection = base_user_data.affection_level
    
    # Update relationship
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message=message,
        current_state=base_user_data
    )
    
    # Assert affection decreased
    assert update.affection_level < initial_affection, \
        f"Rude message '{rude_word}' should decrease affection"
    
    # Assert decrease is negative (at least -1)
    affection_delta = update.affection_level - initial_affection
    assert affection_delta <= -1, \
        f"Affection delta should be at least -1, got {affection_delta}"


# Property 16: Affection Threshold Stage Transition
# **Validates: Requirements 5.5**
@given(
    affection_level=st.integers(min_value=0, max_value=100)
)
@settings(max_examples=10, deadline=None)
def test_property_affection_threshold_stage_transition(
    affection_level
):
    """
    Property: Relationship stage MUST match affection level thresholds.
    
    Stage thresholds:
    - stranger: 0-20
    - friend: 21-50
    - close: 51-80
    - attached: 81-100
    
    **Validates: Requirements 5.5**
    """
    relationship_engine = create_relationship_engine()
    
    stage = relationship_engine.determine_stage(affection_level)
    
    # Verify correct stage mapping
    if affection_level <= 20:
        assert stage == "stranger", \
            f"Affection {affection_level} should be 'stranger', got '{stage}'"
    elif affection_level <= 50:
        assert stage == "friend", \
            f"Affection {affection_level} should be 'friend', got '{stage}'"
    elif affection_level <= 80:
        assert stage == "close", \
            f"Affection {affection_level} should be 'close', got '{stage}'"
    else:
        assert stage == "attached", \
            f"Affection {affection_level} should be 'attached', got '{stage}'"


# Property 17: Sentiment-Based Mood Update
# **Validates: Requirements 5.6**
@given(
    sentiment_type=st.sampled_from([
        "compliment", "vulnerability", "rude", "positive", "negative", "neutral"
    ]),
    current_mood=st.sampled_from([
        "happy", "sad", "angry", "jealous", "flustered", "neutral"
    ])
)
@settings(max_examples=10, deadline=None)
def test_property_sentiment_based_mood_update(
    sentiment_type,
    current_mood
):
    """
    Property: Mood MUST update based on message sentiment.
    
    Expected mood mappings:
    - compliment -> flustered
    - vulnerability -> sad (empathetic)
    - rude -> angry
    - positive -> happy
    - negative -> sad
    - neutral -> maintain or neutral
    
    **Validates: Requirements 5.6**
    """
    relationship_engine = create_relationship_engine()
    
    sentiment = SentimentScore(sentiment_type=sentiment_type, intensity=0.7)
    
    new_mood = relationship_engine.determine_mood(sentiment, current_mood)
    
    # Verify mood mapping
    if sentiment_type == "compliment":
        assert new_mood == "flustered", \
            f"Compliment should trigger 'flustered', got '{new_mood}'"
    elif sentiment_type == "vulnerability":
        assert new_mood == "sad", \
            f"Vulnerability should trigger 'sad', got '{new_mood}'"
    elif sentiment_type == "rude":
        assert new_mood == "angry", \
            f"Rude message should trigger 'angry', got '{new_mood}'"
    elif sentiment_type == "positive":
        assert new_mood == "happy", \
            f"Positive message should trigger 'happy', got '{new_mood}'"
    elif sentiment_type == "negative":
        assert new_mood == "sad", \
            f"Negative message should trigger 'sad', got '{new_mood}'"
    # Neutral maintains current mood or defaults to neutral
    
    # Mood should always be a valid mood string
    valid_moods = ["happy", "sad", "angry", "jealous", "flustered", "neutral"]
    assert new_mood in valid_moods, \
        f"Mood '{new_mood}' is not a valid mood state"


# Property 18: Relationship State Persistence
# **Validates: Requirements 5.7**
@given(
    affection=st.integers(min_value=0, max_value=100),
    trust=st.integers(min_value=0, max_value=100),
    mood=st.sampled_from(["happy", "sad", "angry", "jealous", "flustered", "neutral"]),
    stage=st.sampled_from(["stranger", "friend", "close", "attached"])
)
@settings(max_examples=10, deadline=None)
def test_property_relationship_state_persistence(
    affection,
    trust,
    mood,
    stage
):
    """
    Property: Relationship updates MUST be persisted to Firestore.
    
    **Validates: Requirements 5.7**
    """
    # Setup mock Firestore
    mock_firestore = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    engine = RelationshipEngine(mock_firestore)
    
    # Create update
    update = RelationshipUpdate(
        affection_level=affection,
        trust_level=trust,
        mood=mood,
        relationship_stage=stage
    )
    
    # Persist update
    engine.persist_update("test_user", update)
    
    # Verify Firestore was called
    mock_firestore.collection.assert_called_once_with("waifu_memory")
    mock_collection.document.assert_called_once_with("test_user")
    
    # Verify update was called with correct data
    mock_document.update.assert_called_once()
    call_args = mock_document.update.call_args[0][0]
    
    assert call_args["affection_level"] == affection
    assert call_args["trust_level"] == trust
    assert call_args["mood"] == mood
    assert call_args["relationship_stage"] == stage


# Additional test: Affection bounds enforcement
@given(
    initial_affection=st.integers(min_value=0, max_value=100),
    delta=st.integers(min_value=-50, max_value=50)
)
@settings(max_examples=10, deadline=None)
def test_property_affection_bounds_enforcement(
    initial_affection,
    delta
):
    """
    Property: Affection level MUST stay within 0-100 bounds.
    """
    relationship_engine = create_relationship_engine()
    
    # Create user data with specific affection
    user_data = UserData(
        user_id="test_user",
        affection_level=initial_affection,
        trust_level=50,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Simulate affection change by creating appropriate sentiment
    if delta > 0:
        # Use compliment to increase
        message = "you are beautiful"
    elif delta < 0:
        # Use rude message to decrease
        message = "you are annoying"
    else:
        # Neutral message
        message = "hello"
    
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message=message,
        current_state=user_data
    )
    
    # Assert bounds are enforced
    assert 0 <= update.affection_level <= 100, \
        f"Affection {update.affection_level} is out of bounds [0, 100]"


# Additional test: Trust bounds enforcement
@given(
    initial_trust=st.integers(min_value=0, max_value=100)
)
@settings(max_examples=10, deadline=None)
def test_property_trust_bounds_enforcement(
    initial_trust
):
    """
    Property: Trust level MUST stay within 0-100 bounds.
    """
    relationship_engine = create_relationship_engine()
    
    # Create user data with specific trust
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=initial_trust,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Use vulnerability message to increase trust
    message = "I'm feeling really scared and worried"
    
    update = relationship_engine.update_relationship(
        user_id="test_user",
        message=message,
        current_state=user_data
    )
    
    # Assert bounds are enforced
    assert 0 <= update.trust_level <= 100, \
        f"Trust {update.trust_level} is out of bounds [0, 100]"


# Test sentiment analysis directly
@given(
    message=st.text(min_size=1, max_size=100)
)
@settings(max_examples=10, deadline=None)
def test_property_sentiment_analysis_returns_valid_type(
    message
):
    """
    Property: Sentiment analysis MUST return a valid sentiment type.
    """
    relationship_engine = create_relationship_engine()
    
    sentiment = relationship_engine.analyze_sentiment(message)
    
    valid_types = ["positive", "negative", "neutral", "compliment", "vulnerability", "rude"]
    assert sentiment.sentiment_type in valid_types, \
        f"Invalid sentiment type: {sentiment.sentiment_type}"
    
    # Intensity should be in valid range
    assert 0.0 <= sentiment.intensity <= 1.0, \
        f"Intensity {sentiment.intensity} is out of bounds [0.0, 1.0]"
