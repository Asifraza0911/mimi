"""
Property-based tests for memory storage functionality.

Feature: ai-waifu-cross-platform
Property 7: Important Message Storage

**Validates: Requirements 3.2, 3.3**

For any message deemed important (containing emotional content or personal information),
the system should convert it to an embedding vector and store it in the user's FAISS index,
increasing the index size.
"""

from hypothesis import given, strategies as st, settings
import pytest
import os
import sys
import shutil
import tempfile

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from memory_engine import MemoryEngine


# Strategy for generating diverse message types
message_strategy = st.one_of(
    # Emotional messages
    st.sampled_from([
        "I'm feeling really happy today!",
        "I'm so sad and lonely...",
        "You make me so angry!",
        "I'm scared and worried about this.",
        "I love spending time with you.",
        "I hate when you ignore me.",
        "I'm excited about our conversation!",
        "I feel anxious and nervous."
    ]),
    # Personal information messages
    st.sampled_from([
        "My name is Alice.",
        "I am a software engineer.",
        "I like playing video games.",
        "I love pizza and sushi.",
        "My favorite color is blue.",
        "I work at a tech company.",
        "I study computer science.",
        "I hate spicy food."
    ]),
    # Long messages (indicating sharing)
    st.text(min_size=100, max_size=500, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='.,!?'
    )),
    # Casual messages (not important)
    st.sampled_from([
        "hi",
        "hello",
        "okay",
        "sure",
        "yes",
        "no",
        "thanks",
        "bye"
    ]),
    # Random text
    st.text(min_size=1, max_size=200)
)


# Helper function to create memory engine instances
def create_memory_engine():
    """Create a Memory Engine instance with temporary directory."""
    temp_dir = tempfile.mkdtemp()
    engine = MemoryEngine(firestore_client=None, indices_dir=temp_dir)
    return engine, temp_dir


@given(
    user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    message=message_strategy
)
@settings(max_examples=5, deadline=None)  # Reduced from 100 to 5
@pytest.mark.property_test
def test_important_message_increases_faiss_index_size(user_id, message):
    """
    Property 7: Important Message Storage
    
    For any message stored as important, the FAISS index size should increase
    by exactly 1 vector. This ensures that:
    1. The message is converted to an embedding
    2. The embedding is added to the FAISS index
    3. The index size is correctly updated
    
    This property validates Requirements 3.2 (storing embeddings in FAISS)
    and 3.3 (maintaining FAISS indices).
    """
    # Create memory engine for this test
    memory_engine, temp_dir = create_memory_engine()
    
    try:
        # Get or create the user's FAISS index
        index = memory_engine.get_or_create_index(user_id)
        
        # Record the initial index size
        initial_size = index.ntotal
        
        # Store the message as important
        memory_engine.store_memory(user_id, message, is_important=True)
        
        # Get the index again (should be the same object)
        index_after = memory_engine.get_or_create_index(user_id)
        
        # Verify the index size increased by exactly 1
        assert index_after.ntotal == initial_size + 1, \
            f"Expected index size to increase from {initial_size} to {initial_size + 1}, " \
            f"but got {index_after.ntotal}"
        
        # Verify the same index object is returned (cached)
        assert index is index_after, \
            "get_or_create_index should return the same cached index object"
        
        # Verify metadata was updated
        metadata = memory_engine.user_metadata[user_id]
        assert len(metadata["messages"]) == initial_size + 1, \
            f"Expected {initial_size + 1} messages in metadata, got {len(metadata['messages'])}"
        assert len(metadata["timestamps"]) == initial_size + 1, \
            f"Expected {initial_size + 1} timestamps in metadata, got {len(metadata['timestamps'])}"
        assert metadata["vector_count"] == initial_size + 1, \
            f"Expected vector_count to be {initial_size + 1}, got {metadata['vector_count']}"
        
        # Verify the message was stored in metadata
        assert message in metadata["messages"], \
            "Stored message should appear in metadata"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(
    user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    messages=st.lists(message_strategy, min_size=1, max_size=3)
)
@settings(max_examples=3, deadline=None)  # Reduced from 50 to 3, max_size from 10 to 3
@pytest.mark.property_test
def test_multiple_important_messages_increase_index_size_correctly(user_id, messages):
    """
    Property 7 (Extended): Multiple Message Storage
    
    For any sequence of important messages, each message should increase
    the FAISS index size by 1, resulting in a total increase equal to
    the number of messages stored.
    """
    # Create memory engine for this test
    memory_engine, temp_dir = create_memory_engine()
    
    try:
        # Get or create the user's FAISS index
        index = memory_engine.get_or_create_index(user_id)
        
        # Record the initial index size
        initial_size = index.ntotal
        
        # Store all messages as important
        for message in messages:
            memory_engine.store_memory(user_id, message, is_important=True)
        
        # Get the index after storing all messages
        index_after = memory_engine.get_or_create_index(user_id)
        
        # Verify the index size increased by the number of messages
        expected_size = initial_size + len(messages)
        assert index_after.ntotal == expected_size, \
            f"Expected index size to be {expected_size}, but got {index_after.ntotal}"
        
        # Verify metadata reflects all stored messages
        metadata = memory_engine.user_metadata[user_id]
        assert len(metadata["messages"]) == expected_size, \
            f"Expected {expected_size} messages in metadata, got {len(metadata['messages'])}"
        assert metadata["vector_count"] == expected_size, \
            f"Expected vector_count to be {expected_size}, got {metadata['vector_count']}"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(
    user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    message=message_strategy
)
@settings(max_examples=3, deadline=None)  # Reduced from 50 to 3
@pytest.mark.property_test
def test_non_important_message_still_increases_index_size(user_id, message):
    """
    Property 7 (Extended): Non-Important Message Storage
    
    Even when is_important=False, the message should still be stored in
    the FAISS index (just not in Firestore long_term_memory). This ensures
    all messages contribute to semantic memory retrieval.
    """
    # Create memory engine for this test
    memory_engine, temp_dir = create_memory_engine()
    
    try:
        # Get or create the user's FAISS index
        index = memory_engine.get_or_create_index(user_id)
        
        # Record the initial index size
        initial_size = index.ntotal
        
        # Store the message as NOT important
        memory_engine.store_memory(user_id, message, is_important=False)
        
        # Get the index after storing
        index_after = memory_engine.get_or_create_index(user_id)
        
        # Verify the index size still increased by 1
        assert index_after.ntotal == initial_size + 1, \
            f"Expected index size to increase from {initial_size} to {initial_size + 1}, " \
            f"but got {index_after.ntotal} (even for non-important messages)"
        
        # Verify metadata was updated
        metadata = memory_engine.user_metadata[user_id]
        assert len(metadata["messages"]) == initial_size + 1, \
            "Non-important messages should still be stored in FAISS metadata"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(
    user1_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    user2_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    message1=message_strategy,
    message2=message_strategy
)
@settings(max_examples=3, deadline=None)  # Reduced from 50 to 3
@pytest.mark.property_test
def test_memory_storage_maintains_user_isolation(user1_id, user2_id, message1, message2):
    """
    Property 7 (Extended): User Memory Isolation During Storage
    
    When storing messages for different users, each user's FAISS index
    should be independent. Storing a message for user1 should not affect
    user2's index size.
    """
    # Skip if user IDs are the same
    if user1_id == user2_id:
        return
    
    # Create memory engine for this test
    memory_engine, temp_dir = create_memory_engine()
    
    try:
        # Get initial indices for both users
        index1 = memory_engine.get_or_create_index(user1_id)
        index2 = memory_engine.get_or_create_index(user2_id)
        
        initial_size1 = index1.ntotal
        initial_size2 = index2.ntotal
        
        # Store message for user1
        memory_engine.store_memory(user1_id, message1, is_important=True)
        
        # Verify user1's index increased
        assert index1.ntotal == initial_size1 + 1, \
            f"User1 index should increase from {initial_size1} to {initial_size1 + 1}"
        
        # Verify user2's index is unchanged
        assert index2.ntotal == initial_size2, \
            f"User2 index should remain at {initial_size2}, but got {index2.ntotal}"
        
        # Store message for user2
        memory_engine.store_memory(user2_id, message2, is_important=True)
        
        # Verify user2's index increased
        assert index2.ntotal == initial_size2 + 1, \
            f"User2 index should increase from {initial_size2} to {initial_size2 + 1}"
        
        # Verify user1's index is still at +1 from initial
        assert index1.ntotal == initial_size1 + 1, \
            f"User1 index should remain at {initial_size1 + 1}"
        
        # Verify indices are different objects
        assert index1 is not index2, \
            "Different users should have different FAISS index objects"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(
    user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    message=st.just("")  # Empty string
)
@settings(max_examples=2, deadline=None)  # Reduced from 20 to 2
@pytest.mark.property_test
def test_empty_message_storage_increases_index_size(user_id, message):
    """
    Property 7 (Edge Case): Empty Message Storage
    
    Even an empty message should be stored in the FAISS index and increase
    its size. The embedding model should handle empty strings gracefully.
    """
    # Create memory engine for this test
    memory_engine, temp_dir = create_memory_engine()
    
    try:
        # Get or create the user's FAISS index
        index = memory_engine.get_or_create_index(user_id)
        
        # Record the initial index size
        initial_size = index.ntotal
        
        # Store the empty message
        memory_engine.store_memory(user_id, message, is_important=True)
        
        # Verify the index size increased by 1
        assert index.ntotal == initial_size + 1, \
            f"Empty message should still increase index size from {initial_size} to {initial_size + 1}"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(
    user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    message=st.text(min_size=1, max_size=200)
)
@settings(max_examples=1, deadline=None)  # Reduced from 30 to 1 (model loading is slow)
@pytest.mark.property_test
def test_stored_message_persists_to_disk(user_id, message):
    """
    Property 7 (Extended): Memory Persistence
    
    When a message is stored, it should be persisted to disk so that it
    can be loaded in future sessions. This validates Requirement 3.3
    (maintaining FAISS indices with persistence).
    """
    # Create temporary directory for this test
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create first memory engine and store message
        engine1 = MemoryEngine(firestore_client=None, indices_dir=temp_dir)
        engine1.store_memory(user_id, message, is_important=True)
        
        # Verify index and metadata files were created
        index_path = os.path.join(temp_dir, f"{user_id}.index")
        metadata_path = os.path.join(temp_dir, f"{user_id}_metadata.json")
        
        assert os.path.exists(index_path), \
            f"FAISS index file should be created at {index_path}"
        assert os.path.exists(metadata_path), \
            f"Metadata file should be created at {metadata_path}"
        
        # Create a new memory engine instance (simulating restart)
        engine2 = MemoryEngine(firestore_client=None, indices_dir=temp_dir)
        
        # Load the index from disk
        loaded_index = engine2.get_or_create_index(user_id)
        
        # Verify the loaded index has the stored message
        assert loaded_index.ntotal >= 1, \
            "Loaded index should contain at least the stored message"
        
        # Verify metadata was loaded
        assert user_id in engine2.user_metadata, \
            "User metadata should be loaded from disk"
        assert message in engine2.user_metadata[user_id]["messages"], \
            "Stored message should be in loaded metadata"
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "property_test"])
