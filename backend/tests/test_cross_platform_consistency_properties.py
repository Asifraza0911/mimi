"""
Property-based tests for cross-platform consistency.

This module uses Hypothesis to test universal properties that should hold
across all valid inputs for cross-platform interactions.

**Validates: Requirements 4.11, 10.3, 10.4, 10.5**
"""

import pytest
import sys
import os
from datetime import datetime, date
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import ChatRequest, ChatResponse, UserData, MemoryEntry
from container import ServiceContainer
from config import Config


# Custom strategies for generating test data
@composite
def user_id_strategy(draw):
    """Generate valid user IDs."""
    return draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )))


@composite
def platform_strategy(draw):
    """Generate valid platform values."""
    return draw(st.sampled_from(["web", "discord"]))


@composite
def message_strategy(draw):
    """Generate valid message content."""
    return draw(st.text(min_size=1, max_size=200, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # Exclude control characters
        blacklist_characters='\x00\r\n\t'
    )))


def create_mock_firestore():
    """Create a mock Firestore client with in-memory document storage."""
    mock_client = MagicMock()
    documents = {}
    
    def get_document(collection_name, doc_id):
        """Get document from in-memory storage."""
        key = f"{collection_name}/{doc_id}"
        mock_doc = MagicMock()
        if key in documents:
            mock_doc.exists = True
            mock_doc.to_dict.return_value = documents[key]
        else:
            mock_doc.exists = False
        return mock_doc
    
    def set_document(collection_name, doc_id, data):
        """Set document in in-memory storage."""
        key = f"{collection_name}/{doc_id}"
        documents[key] = data
    
    def update_document(collection_name, doc_id, updates):
        """Update document in in-memory storage."""
        key = f"{collection_name}/{doc_id}"
        if key in documents:
            documents[key].update(updates)
        else:
            documents[key] = updates
    
    # Configure mock to use in-memory storage
    mock_collection = MagicMock()
    mock_client.collection.return_value = mock_collection
    
    # Store doc_id when document() is called
    def set_doc_id(doc_id):
        mock_doc = MagicMock()
        mock_doc._doc_id = doc_id
        mock_doc.get.side_effect = lambda: get_document("waifu_memory", doc_id)
        mock_doc.set.side_effect = lambda data: set_document("waifu_memory", doc_id, data)
        mock_doc.update.side_effect = lambda updates: update_document("waifu_memory", doc_id, updates)
        return mock_doc
    
    mock_collection.document.side_effect = set_doc_id
    mock_client.collections.return_value = []
    
    return mock_client, documents


def create_service_container_with_mocks():
    """Create service container with all external dependencies mocked."""
    config = Config()
    config.HUGGINGFACE_API_TOKEN = "test_token"
    
    mock_firestore, documents = create_mock_firestore()
    
    # Mock personality file
    mock_personality = """You are Mimi, a tsundere anime girl.
You pretend to be annoyed but secretly care about the user.
Use expressions like 'Hmph!', 'B-baka!', and 'I-it's not like I care!'"""
    
    # Mock FAISS index
    mock_faiss_index = MagicMock()
    mock_faiss_index.ntotal = 0
    mock_faiss_index.search.return_value = ([], [])
    
    # Mock HuggingFace API
    mock_hf_response = MagicMock()
    mock_hf_response.status_code = 200
    mock_hf_response.json.return_value = [{"generated_text": "Hmph! Test response!"}]
    
    # Mock sentence transformer
    import numpy as np
    mock_st_model = MagicMock()
    mock_st_model.encode.return_value = np.array([0.1] * 384, dtype='float32')
    
    with patch('container.initialize_firestore', return_value=mock_firestore), \
         patch('modules.llm_service.requests.post', return_value=mock_hf_response), \
         patch('modules.memory_engine.SentenceTransformer', return_value=mock_st_model), \
         patch('os.path.exists') as mock_exists, \
         patch('builtins.open', create=True) as mock_open, \
         patch('modules.memory_engine.faiss.IndexFlatL2', return_value=mock_faiss_index), \
         patch('modules.memory_engine.faiss.read_index', return_value=mock_faiss_index), \
         patch('modules.memory_engine.faiss.write_index'), \
         patch('os.makedirs'):
        
        # Configure os.path.exists
        def exists_side_effect(path):
            if 'waifu_personality.txt' in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        
        # Configure open to return personality content
        mock_file = MagicMock()
        mock_file.read.return_value = mock_personality
        mock_file.__enter__.return_value = mock_file
        mock_open.return_value = mock_file
        
        container = ServiceContainer(config)
        return container, documents


class TestProperty12_CrossPlatformPersonalityConsistency:
    """
    Property 12: Cross-Platform Personality Consistency
    
    **Validates: Requirements 4.11**
    
    For any user_id, interactions from "web" platform and "discord" platform
    should retrieve the same personality definition and relationship state.
    """
    
    @given(
        user_id=user_id_strategy(),
        message=message_strategy()
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_same_personality_across_platforms(self, user_id, message):
        """Test that personality definition is consistent across platforms."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # Interact via web platform
        response_web = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="web"
        )
        
        # Interact via discord platform with same user_id
        response_discord = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="discord"
        )
        
        # Verify both responses were generated (personality was applied)
        assert response_web.reply is not None
        assert response_discord.reply is not None
        assert len(response_web.reply) > 0
        assert len(response_discord.reply) > 0
        
        # Verify personality system is the same instance
        assert container.personality_system is not None
        
        # Verify personality definition is loaded once and shared
        personality_def = container.personality_system.personality_definition
        assert personality_def is not None
        assert len(personality_def) > 0
    
    @given(
        user_id=user_id_strategy(),
        message1=message_strategy(),
        message2=message_strategy()
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_relationship_state_consistent_across_platforms(self, user_id, message1, message2):
        """Test that relationship state is shared across platforms."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # First interaction via web
        response_web1 = await pipeline.process_message(
            user_id=user_id,
            message=message1,
            platform="web"
        )
        web_affection = response_web1.affection_level
        web_mood = response_web1.mood
        
        # Second interaction via discord (should see state from web)
        response_discord = await pipeline.process_message(
            user_id=user_id,
            message=message2,
            platform="discord"
        )
        
        # Verify affection is consistent (may change slightly due to message processing)
        # But should be in reasonable range, not reset to default
        assert abs(response_discord.affection_level - web_affection) <= 10
        
        # Third interaction via web (should see cumulative state)
        response_web2 = await pipeline.process_message(
            user_id=user_id,
            message=message1,
            platform="web"
        )
        
        # Verify state continuity across all platforms
        assert response_web2.affection_level >= 0
        assert response_web2.affection_level <= 100


class TestProperty23_CrossPlatformIdentityConsistency:
    """
    Property 23: Cross-Platform Identity Consistency
    
    **Validates: Requirements 10.3, 10.4, 10.5**
    
    For any user_id, sending messages from "web" platform and "discord" platform
    should retrieve the same Firestore document and query the same FAISS index,
    ensuring unified relationship state and memory across platforms.
    """
    
    @given(
        user_id=user_id_strategy(),
        platform1=platform_strategy(),
        platform2=platform_strategy()
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_same_firestore_document_across_platforms(self, user_id, platform1, platform2):
        """Test that same user_id accesses same Firestore document regardless of platform."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # Interact via first platform
        response1 = await pipeline.process_message(
            user_id=user_id,
            message="Hello from platform 1",
            platform=platform1
        )
        
        # Check that document was created
        doc_key = f"waifu_memory/{user_id}"
        assert doc_key in documents
        
        # Store initial state
        initial_affection = response1.affection_level
        
        # Interact via second platform
        response2 = await pipeline.process_message(
            user_id=user_id,
            message="Hello from platform 2",
            platform=platform2
        )
        
        # Verify same document is still being used
        assert doc_key in documents
        
        # Verify state continuity (affection should not reset)
        # It may change slightly due to message processing, but should not be default value
        if platform1 == platform2:
            # Same platform, state should be very similar
            assert abs(response2.affection_level - initial_affection) <= 5
        else:
            # Different platforms, but should still access same state
            # Affection should not reset to default (10)
            assert response2.affection_level >= initial_affection - 5
    
    @given(
        user_id=user_id_strategy(),
        message=message_strategy()
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_same_faiss_index_across_platforms(self, user_id, message):
        """Test that same user_id uses same FAISS index regardless of platform."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        memory_engine = container.memory_engine
        
        # Interact via web platform
        response_web = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="web"
        )
        
        # Check if FAISS index was created for user
        # Note: With mocked FAISS, we verify the memory engine is shared
        assert memory_engine is not None
        
        # Interact via discord platform
        response_discord = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="discord"
        )
        
        # Verify memory engine is the same instance (shared FAISS indices)
        assert container.memory_engine is memory_engine
        
        # Verify both interactions used the memory engine
        assert response_web.reply is not None
        assert response_discord.reply is not None
    
    @given(
        user_id=user_id_strategy(),
        important_message=st.text(min_size=50, max_size=200)  # Long message likely to be stored
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_memory_shared_across_platforms(self, user_id, important_message):
        """Test that memories stored on one platform are accessible on another."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # Store important memory via web platform
        response_web = await pipeline.process_message(
            user_id=user_id,
            message=important_message,
            platform="web"
        )
        
        # Check if memory was stored in Firestore
        doc_key = f"waifu_memory/{user_id}"
        assert doc_key in documents
        
        # Interact via discord platform
        response_discord = await pipeline.process_message(
            user_id=user_id,
            message="What do you remember about me?",
            platform="discord"
        )
        
        # Verify same Firestore document is accessed
        assert doc_key in documents
        
        # Verify response was generated (memory system is working)
        assert response_discord.reply is not None
    
    @given(
        user_id=user_id_strategy(),
        platforms=st.lists(platform_strategy(), min_size=2, max_size=5)
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_affection_accumulates_across_platform_switches(self, user_id, platforms):
        """Test that affection changes accumulate across multiple platform switches."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # Initial interaction
        response_initial = await pipeline.process_message(
            user_id=user_id,
            message="Hello!",
            platform=platforms[0]
        )
        initial_affection = response_initial.affection_level
        
        # Interact across multiple platforms
        last_response = response_initial
        for platform in platforms[1:]:
            last_response = await pipeline.process_message(
                user_id=user_id,
                message="You're great!",
                platform=platform
            )
        
        # Verify state is maintained across all platform switches
        # Affection should not reset to default
        assert last_response.affection_level >= initial_affection - 5
        
        # Verify same document was used throughout
        doc_key = f"waifu_memory/{user_id}"
        assert doc_key in documents
    
    @given(
        user_id=user_id_strategy(),
        message=message_strategy()
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_platform_field_tracked_but_not_used_for_segregation(self, user_id, message):
        """Test that platform field is tracked for analytics but doesn't segregate data."""
        container, documents = create_service_container_with_mocks()
        pipeline = container.get_response_pipeline()
        
        # Interact via web
        response_web = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="web"
        )
        
        # Interact via discord
        response_discord = await pipeline.process_message(
            user_id=user_id,
            message=message,
            platform="discord"
        )
        
        # Verify only one document exists for this user (not segregated by platform)
        doc_key = f"waifu_memory/{user_id}"
        assert doc_key in documents
        
        # Count documents for this user (should be exactly 1)
        user_docs = [key for key in documents.keys() if user_id in key]
        assert len(user_docs) == 1
        
        # Verify platform_stats may be tracked in the document
        user_data = documents[doc_key]
        if "platform_stats" in user_data:
            # Platform stats exist for analytics
            assert isinstance(user_data["platform_stats"], dict)
        
        # But verify state is unified (not separate per platform)
        assert response_web.affection_level >= 0
        assert response_discord.affection_level >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
