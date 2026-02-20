"""
Property-based tests for Firestore user document operations.

This module uses Hypothesis to test universal properties that should hold
across all valid inputs for user document operations.

**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite
from models import UserData, MemoryEntry, EmotionalMemoryEntry

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from firestore_operations import get_or_create_user, update_user_data, get_user_data


# Custom strategies for generating test data
@composite
def user_id_strategy(draw):
    """Generate valid user IDs."""
    return draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )))


@composite
def mood_strategy(draw):
    """Generate valid mood values."""
    moods = ["neutral", "happy", "sad", "angry", "jealous", "flustered"]
    return draw(st.sampled_from(moods))


@composite
def relationship_stage_strategy(draw):
    """Generate valid relationship stage values."""
    stages = ["stranger", "friend", "close", "attached"]
    return draw(st.sampled_from(stages))


@composite
def attachment_state_strategy(draw):
    """Generate valid attachment state values."""
    states = ["avoidant", "anxious", "secure", "possessive"]
    return draw(st.sampled_from(states))


@composite
def user_data_strategy(draw):
    """Generate valid UserData objects for testing."""
    user_id = draw(user_id_strategy())
    affection_level = draw(st.integers(min_value=0, max_value=100))
    trust_level = draw(st.integers(min_value=0, max_value=100))
    mood = draw(mood_strategy())
    relationship_stage = draw(relationship_stage_strategy())
    attachment_state = draw(attachment_state_strategy())
    daily_interaction_streak = draw(st.integers(min_value=0, max_value=365))
    
    return {
        "user_id": user_id,
        "name": draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        "affection_level": affection_level,
        "trust_level": trust_level,
        "mood": mood,
        "relationship_stage": relationship_stage,
        "attachment_state": attachment_state,
        "long_term_memory": [],
        "emotional_memory": [],
        "last_interaction": datetime.now(),
        "last_chat_date": date.today(),
        "daily_interaction_streak": daily_interaction_streak,
        "created_at": datetime.now(),
        "platform_stats": {"web": 0, "discord": 0}
    }


class TestProperty3_UserDocumentSchemaIntegrity:
    """
    Property 3: User Document Schema Integrity
    
    **Validates: Requirements 2.2, 2.5, 2.6, 2.7**
    
    For any user document in Firestore, it should contain all required fields
    with correct data types: affection_level and trust_level as numbers between
    0-100, mood as string, and relationship_stage as one of "stranger", "friend",
    "close", or "attached".
    """
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=10, deadline=None)
    def test_retrieved_user_has_all_required_fields(self, user_data):
        """Test that any retrieved user document contains all required fields."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = user_data
        
        # Retrieve user
        result = get_or_create_user(mock_db, user_data["user_id"])
        
        # Verify all required fields exist
        assert hasattr(result, 'user_id')
        assert hasattr(result, 'name')
        assert hasattr(result, 'affection_level')
        assert hasattr(result, 'trust_level')
        assert hasattr(result, 'mood')
        assert hasattr(result, 'relationship_stage')
        assert hasattr(result, 'attachment_state')
        assert hasattr(result, 'long_term_memory')
        assert hasattr(result, 'emotional_memory')
        assert hasattr(result, 'last_interaction')
        assert hasattr(result, 'last_chat_date')
        assert hasattr(result, 'daily_interaction_streak')
        assert hasattr(result, 'created_at')
        assert hasattr(result, 'platform_stats')
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=10, deadline=None)
    def test_affection_level_within_valid_range(self, user_data):
        """Test that affection_level is always between 0-100."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = user_data
        
        # Retrieve user
        result = get_or_create_user(mock_db, user_data["user_id"])
        
        # Verify affection_level is in valid range
        assert isinstance(result.affection_level, int)
        assert 0 <= result.affection_level <= 100
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=10, deadline=None)
    def test_trust_level_within_valid_range(self, user_data):
        """Test that trust_level is always between 0-100."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = user_data
        
        # Retrieve user
        result = get_or_create_user(mock_db, user_data["user_id"])
        
        # Verify trust_level is in valid range
        assert isinstance(result.trust_level, int)
        assert 0 <= result.trust_level <= 100
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=10, deadline=None)
    def test_mood_is_string(self, user_data):
        """Test that mood is always a string."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = user_data
        
        # Retrieve user
        result = get_or_create_user(mock_db, user_data["user_id"])
        
        # Verify mood is a string
        assert isinstance(result.mood, str)
    
    @given(user_data=user_data_strategy())
    @settings(max_examples=10, deadline=None)
    def test_relationship_stage_is_valid(self, user_data):
        """Test that relationship_stage is one of the valid values."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = user_data
        
        # Retrieve user
        result = get_or_create_user(mock_db, user_data["user_id"])
        
        # Verify relationship_stage is valid
        valid_stages = ["stranger", "friend", "close", "attached"]
        assert result.relationship_stage in valid_stages


class TestProperty4_NewUserInitialization:
    """
    Property 4: New User Initialization
    
    **Validates: Requirements 2.3**
    
    For any first-time user interaction, the system should create a Firestore
    document with default values: affection_level=10, trust_level=5,
    mood="neutral", relationship_stage="stranger", empty memory arrays.
    """
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_default_affection_level(self, user_id):
        """Test that new users are created with affection_level=10."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False  # User doesn't exist
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify default affection_level
        assert result.affection_level == 10
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_default_trust_level(self, user_id):
        """Test that new users are created with trust_level=5."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify default trust_level
        assert result.trust_level == 5
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_neutral_mood(self, user_id):
        """Test that new users are created with mood="neutral"."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify default mood
        assert result.mood == "neutral"
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_stranger_relationship_stage(self, user_id):
        """Test that new users are created with relationship_stage="stranger"."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify default relationship_stage
        assert result.relationship_stage == "stranger"
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_avoidant_attachment_state(self, user_id):
        """Test that new users are created with attachment_state="avoidant"."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify default attachment_state
        assert result.attachment_state == "avoidant"
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_empty_memory_arrays(self, user_id):
        """Test that new users are created with empty memory arrays."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify empty memory arrays
        assert result.long_term_memory == []
        assert result.emotional_memory == []
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_initial_streak(self, user_id):
        """Test that new users are created with daily_interaction_streak=1."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify initial streak
        assert result.daily_interaction_streak == 1
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_document_is_persisted(self, user_id):
        """Test that new user data is persisted to Firestore."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify Firestore set was called to persist the document
        mock_doc_ref.set.assert_called_once()


class TestProperty5_TimestampUpdateOnInteraction:
    """
    Property 5: Timestamp Update on Interaction
    
    **Validates: Requirements 2.4**
    
    For any conversation message, the last_interaction timestamp in Firestore
    should be updated to reflect the current time.
    """
    
    @given(
        user_id=user_id_strategy(),
        initial_timestamp=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now() - timedelta(hours=1)
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_last_interaction_is_updated_on_update(self, user_id, initial_timestamp):
        """Test that updating user data can update last_interaction timestamp."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Update with new timestamp
        new_timestamp = datetime.now()
        updates = {"last_interaction": new_timestamp}
        
        # Call update function
        update_user_data(mock_db, user_id, updates)
        
        # Verify update was called with the new timestamp
        mock_doc_ref.update.assert_called_once()
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "last_interaction" in call_args
        assert call_args["last_interaction"] == new_timestamp
    
    @given(
        user_id=user_id_strategy(),
        affection_delta=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    def test_timestamp_update_with_other_fields(self, user_id, affection_delta):
        """Test that last_interaction can be updated alongside other fields."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Update multiple fields including timestamp
        new_timestamp = datetime.now()
        updates = {
            "last_interaction": new_timestamp,
            "affection_level": 50 + affection_delta,
            "mood": "happy"
        }
        
        # Call update function
        update_user_data(mock_db, user_id, updates)
        
        # Verify all fields were updated
        mock_doc_ref.update.assert_called_once()
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "last_interaction" in call_args
        assert "affection_level" in call_args
        assert "mood" in call_args
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_new_user_has_recent_last_interaction(self, user_id):
        """Test that new users have last_interaction set to current time."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Record time before creation
        before_creation = datetime.now()
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Record time after creation
        after_creation = datetime.now()
        
        # Verify last_interaction is between before and after
        assert before_creation <= result.last_interaction <= after_creation
    
    @given(user_id=user_id_strategy())
    @settings(max_examples=10, deadline=None)
    def test_last_chat_date_is_set_for_new_users(self, user_id):
        """Test that new users have last_chat_date set to today."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain for non-existent user
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False
        
        # Create new user
        result = get_or_create_user(mock_db, user_id)
        
        # Verify last_chat_date is today
        assert result.last_chat_date == date.today()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
