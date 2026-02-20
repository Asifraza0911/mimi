"""
Unit tests for Firestore user document operations.

Tests the get_or_create_user, update_user_data, and get_user_data functions.
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, MagicMock, patch
from models import UserData, MemoryEntry, EmotionalMemoryEntry


# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from firestore_operations import get_or_create_user, update_user_data, get_user_data


class TestGetOrCreateUser:
    """Test suite for get_or_create_user function."""
    
    def test_create_new_user_with_defaults(self):
        """Test creating a new user with default values."""
        # Mock Firestore client and document
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False  # User doesn't exist
        
        # Call function
        user_data = get_or_create_user(mock_db, "test_user_123")
        
        # Verify user was created with correct defaults
        assert user_data.user_id == "test_user_123"
        assert user_data.affection_level == 10
        assert user_data.trust_level == 5
        assert user_data.mood == "neutral"
        assert user_data.relationship_stage == "stranger"
        assert user_data.attachment_state == "avoidant"
        assert user_data.daily_interaction_streak == 1
        assert user_data.long_term_memory == []
        assert user_data.emotional_memory == []
        assert user_data.platform_stats == {"web": 0, "discord": 0}
        
        # Verify Firestore set was called
        mock_doc_ref.set.assert_called_once()
    
    def test_retrieve_existing_user(self):
        """Test retrieving an existing user from Firestore."""
        # Mock Firestore client and document
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup existing user data
        existing_data = {
            "user_id": "existing_user",
            "name": "TestUser",
            "affection_level": 50,
            "trust_level": 40,
            "mood": "happy",
            "relationship_stage": "friend",
            "attachment_state": "anxious",
            "long_term_memory": [],
            "emotional_memory": [],
            "last_interaction": datetime.now(),
            "last_chat_date": date.today(),
            "daily_interaction_streak": 5,
            "created_at": datetime.now(),
            "platform_stats": {"web": 10, "discord": 5}
        }
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = existing_data
        
        # Call function
        user_data = get_or_create_user(mock_db, "existing_user")
        
        # Verify user data was retrieved correctly
        assert user_data.user_id == "existing_user"
        assert user_data.name == "TestUser"
        assert user_data.affection_level == 50
        assert user_data.trust_level == 40
        assert user_data.mood == "happy"
        assert user_data.relationship_stage == "friend"
        assert user_data.attachment_state == "anxious"
        assert user_data.daily_interaction_streak == 5
        
        # Verify Firestore set was NOT called (user already exists)
        mock_doc_ref.set.assert_not_called()


class TestUpdateUserData:
    """Test suite for update_user_data function."""
    
    def test_update_single_field(self):
        """Test updating a single field."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Call function
        updates = {"affection_level": 75}
        update_user_data(mock_db, "test_user", updates)
        
        # Verify update was called with correct data
        mock_doc_ref.update.assert_called_once_with({"affection_level": 75})
    
    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Call function
        updates = {
            "affection_level": 60,
            "mood": "flustered",
            "relationship_stage": "close"
        }
        update_user_data(mock_db, "test_user", updates)
        
        # Verify update was called with all fields
        mock_doc_ref.update.assert_called_once()
        call_args = mock_doc_ref.update.call_args[0][0]
        assert call_args["affection_level"] == 60
        assert call_args["mood"] == "flustered"
        assert call_args["relationship_stage"] == "close"


class TestGetUserData:
    """Test suite for get_user_data function."""
    
    def test_get_existing_user(self):
        """Test retrieving an existing user."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup existing user data
        existing_data = {
            "user_id": "test_user",
            "name": None,
            "affection_level": 30,
            "trust_level": 20,
            "mood": "neutral",
            "relationship_stage": "friend",
            "attachment_state": "avoidant",
            "long_term_memory": [],
            "emotional_memory": [],
            "last_interaction": datetime.now(),
            "last_chat_date": date.today(),
            "daily_interaction_streak": 3,
            "created_at": datetime.now(),
            "platform_stats": {"web": 5, "discord": 0}
        }
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = True
        mock_doc.to_dict.return_value = existing_data
        
        # Call function
        user_data = get_user_data(mock_db, "test_user")
        
        # Verify user data was retrieved
        assert user_data is not None
        assert user_data.user_id == "test_user"
        assert user_data.affection_level == 30
        assert user_data.relationship_stage == "friend"
    
    def test_get_nonexistent_user(self):
        """Test retrieving a user that doesn't exist returns None."""
        # Mock Firestore client
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc = Mock()
        
        # Setup mock chain
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc
        mock_doc.exists = False  # User doesn't exist
        
        # Call function
        user_data = get_user_data(mock_db, "nonexistent_user")
        
        # Verify None is returned
        assert user_data is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
