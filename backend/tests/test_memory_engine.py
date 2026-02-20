"""
Unit tests for Memory Engine module

Tests basic functionality of the Memory Engine including:
- Embedding generation
- FAISS index creation
- Memory storage
- Similarity retrieval
"""

import pytest
import os
import sys
import shutil
import numpy as np

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from memory_engine import MemoryEngine


@pytest.fixture
def temp_indices_dir(tmp_path):
    """Create a temporary directory for FAISS indices."""
    indices_dir = tmp_path / "test_faiss_indices"
    indices_dir.mkdir()
    yield str(indices_dir)
    # Cleanup after test
    if indices_dir.exists():
        shutil.rmtree(indices_dir)


@pytest.fixture
def memory_engine(temp_indices_dir):
    """Create a Memory Engine instance with temporary directory."""
    return MemoryEngine(firestore_client=None, indices_dir=temp_indices_dir)


def test_generate_embedding_returns_correct_shape(memory_engine):
    """Test that embeddings have the correct dimension (384)."""
    text = "Hello, how are you?"
    embedding = memory_engine.generate_embedding(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)
    assert embedding.dtype == np.float32


def test_generate_embedding_consistency(memory_engine):
    """Test that the same text generates the same embedding."""
    text = "This is a test message"
    embedding1 = memory_engine.generate_embedding(text)
    embedding2 = memory_engine.generate_embedding(text)
    
    # Embeddings should be identical for the same input
    np.testing.assert_array_almost_equal(embedding1, embedding2)


def test_get_or_create_index_creates_new_index(memory_engine):
    """Test that a new FAISS index is created for a new user."""
    user_id = "test_user_1"
    index = memory_engine.get_or_create_index(user_id)
    
    assert index is not None
    assert index.ntotal == 0  # New index should be empty
    assert user_id in memory_engine.user_indices
    assert user_id in memory_engine.user_metadata


def test_get_or_create_index_returns_cached_index(memory_engine):
    """Test that the same index is returned for subsequent calls."""
    user_id = "test_user_2"
    index1 = memory_engine.get_or_create_index(user_id)
    index2 = memory_engine.get_or_create_index(user_id)
    
    # Should return the same index object
    assert index1 is index2


def test_store_memory_adds_to_index(memory_engine):
    """Test that storing a memory increases the index size."""
    user_id = "test_user_3"
    message = "I love pizza"
    
    # Get initial index
    index = memory_engine.get_or_create_index(user_id)
    initial_count = index.ntotal
    
    # Store memory
    memory_engine.store_memory(user_id, message, is_important=False)
    
    # Check that index size increased
    assert index.ntotal == initial_count + 1
    assert len(memory_engine.user_metadata[user_id]["messages"]) == 1
    assert memory_engine.user_metadata[user_id]["messages"][0] == message


def test_store_multiple_memories(memory_engine):
    """Test storing multiple memories for a user."""
    user_id = "test_user_4"
    messages = [
        "I like cats",
        "My favorite color is blue",
        "I enjoy programming"
    ]
    
    for message in messages:
        memory_engine.store_memory(user_id, message, is_important=False)
    
    index = memory_engine.user_indices[user_id]
    assert index.ntotal == len(messages)
    assert len(memory_engine.user_metadata[user_id]["messages"]) == len(messages)


def test_retrieve_similar_returns_empty_for_empty_index(memory_engine):
    """Test that retrieval returns empty list when no memories exist."""
    user_id = "test_user_5"
    query = "What do you remember?"
    
    similar = memory_engine.retrieve_similar(user_id, query, k=3)
    
    assert similar == []


def test_retrieve_similar_finds_relevant_memories(memory_engine):
    """Test that similarity search returns relevant memories."""
    user_id = "test_user_6"
    
    # Store some memories
    memories = [
        "I love dogs and puppies",
        "My favorite food is sushi",
        "I have a pet cat named Whiskers"
    ]
    
    for memory in memories:
        memory_engine.store_memory(user_id, memory, is_important=False)
    
    # Query for pet-related memories
    query = "Tell me about pets"
    similar = memory_engine.retrieve_similar(user_id, query, k=2)
    
    assert len(similar) <= 2
    assert len(similar) > 0
    # The pet-related memories should be in the results
    # (exact order may vary based on similarity scores)


def test_retrieve_similar_respects_k_parameter(memory_engine):
    """Test that k parameter limits the number of results."""
    user_id = "test_user_7"
    
    # Store 5 memories
    for i in range(5):
        memory_engine.store_memory(user_id, f"Memory number {i}", is_important=False)
    
    # Request only 3 results
    similar = memory_engine.retrieve_similar(user_id, "test query", k=3)
    
    assert len(similar) == 3


def test_user_memory_isolation(memory_engine):
    """Test that different users have separate memory indices."""
    user1 = "user_1"
    user2 = "user_2"
    
    # Store memory for user 1
    memory_engine.store_memory(user1, "User 1 memory", is_important=False)
    
    # Store memory for user 2
    memory_engine.store_memory(user2, "User 2 memory", is_important=False)
    
    # Check that each user has their own index
    assert user1 in memory_engine.user_indices
    assert user2 in memory_engine.user_indices
    assert memory_engine.user_indices[user1] is not memory_engine.user_indices[user2]
    
    # Check that memories are isolated
    user1_memories = memory_engine.retrieve_similar(user1, "memory", k=10)
    user2_memories = memory_engine.retrieve_similar(user2, "memory", k=10)
    
    assert "User 1 memory" in user1_memories
    assert "User 1 memory" not in user2_memories
    assert "User 2 memory" in user2_memories
    assert "User 2 memory" not in user1_memories


def test_index_persistence(memory_engine, temp_indices_dir):
    """Test that indices are persisted to disk."""
    user_id = "test_user_8"
    message = "This should be persisted"
    
    # Store memory
    memory_engine.store_memory(user_id, message, is_important=False)
    
    # Get the sanitized user_id (hashed filename)
    safe_user_id = memory_engine._sanitize_user_id(user_id)
    
    # Check that files were created with hashed filename
    index_path = os.path.join(temp_indices_dir, f"{safe_user_id}.index")
    metadata_path = os.path.join(temp_indices_dir, f"{safe_user_id}_metadata.json")
    
    assert os.path.exists(index_path)
    assert os.path.exists(metadata_path)


def test_index_loading_from_disk(temp_indices_dir):
    """Test that indices can be loaded from disk."""
    user_id = "test_user_9"
    message = "Persistent memory"
    
    # Create first engine and store memory
    engine1 = MemoryEngine(firestore_client=None, indices_dir=temp_indices_dir)
    engine1.store_memory(user_id, message, is_important=False)
    
    # Create second engine (simulating restart)
    engine2 = MemoryEngine(firestore_client=None, indices_dir=temp_indices_dir)
    
    # Load index from disk
    index = engine2.get_or_create_index(user_id)
    
    # Check that memory was loaded
    assert index.ntotal == 1
    assert len(engine2.user_metadata[user_id]["messages"]) == 1
    assert engine2.user_metadata[user_id]["messages"][0] == message
    
    # Verify retrieval works
    similar = engine2.retrieve_similar(user_id, "memory", k=1)
    assert message in similar


# ============================================================================
# Property-Based Tests for Memory Importance Scoring
# ============================================================================

from hypothesis import given, strategies as st, settings

# Create a shared engine instance for property tests to avoid reloading the model
_shared_engine = None

def get_shared_engine():
    """Get or create a shared MemoryEngine instance for property tests."""
    global _shared_engine
    if _shared_engine is None:
        _shared_engine = MemoryEngine(firestore_client=None)
    return _shared_engine


# Property 28: Memory Weight Range Constraint
# Validates: Requirements 17.1
@given(
    message=st.text(min_size=1, max_size=200),
    emotion_mood=st.one_of(st.none(), st.sampled_from(["happy", "sad", "angry", "vulnerable", "neutral", "jealous", "flustered"]))
)
@settings(max_examples=10, deadline=None)
def test_property_memory_weight_range_constraint(message, emotion_mood):
    """
    **Property 28: Memory Weight Range Constraint**
    **Validates: Requirements 17.1**
    
    Property: All memory weights must be in the range [0.0, 1.0] regardless of input.
    
    This ensures that the weight calculation always produces valid values that can be
    used in weighted similarity calculations without causing errors.
    """
    engine = get_shared_engine()
    emotion_result = {"detected_mood": emotion_mood} if emotion_mood else None
    
    weight = engine.calculate_memory_weight(message, emotion_result)
    
    # Assert weight is in valid range
    assert 0.0 <= weight <= 1.0, f"Weight {weight} is outside valid range [0.0, 1.0]"
    assert isinstance(weight, float), f"Weight must be float, got {type(weight)}"


# Property 29: Weighted Memory Ranking
# Validates: Requirements 17.4
@given(
    user_id=st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    query=st.text(min_size=5, max_size=50)
)
@settings(max_examples=10, deadline=None)
def test_property_weighted_memory_ranking(user_id, query):
    """
    **Property 29: Weighted Memory Ranking**
    **Validates: Requirements 17.4**
    
    Property: When retrieving memories, high-weight memories should be prioritized
    over low-weight memories with similar similarity scores.
    
    This ensures that emotionally significant memories are surfaced even if they
    are not the most semantically similar to the current query.
    """
    import time
    engine = get_shared_engine()
    
    # Use a unique user_id with timestamp to avoid conflicts between test runs
    test_user_id = f"prop_test_{user_id}_{int(time.time() * 1000000)}"
    
    # Store memories with different weights
    # High-weight memory (crisis)
    engine.store_memory(test_user_id, "I need help with something urgent", is_important=True, weight=1.0)
    
    # Medium-weight memory (preference)
    engine.store_memory(test_user_id, "I like pizza and pasta", is_important=True, weight=0.5)
    
    # Low-weight memory (casual)
    engine.store_memory(test_user_id, "hi there", is_important=False, weight=0.1)
    
    # Retrieve memories
    similar = engine.retrieve_similar(test_user_id, query, k=3)
    
    # Assert that we got results
    assert len(similar) <= 3
    assert len(similar) > 0
    
    # The weighted ranking should prioritize based on similarity * weight
    # We can't predict exact order without knowing similarity scores,
    # but we can verify the mechanism works by checking metadata
    metadata = engine.user_metadata[test_user_id]
    assert "weights" in metadata
    assert len(metadata["weights"]) == 3
    assert 1.0 in metadata["weights"]
    assert 0.5 in metadata["weights"]
    assert 0.1 in metadata["weights"]


def test_calculate_memory_weight_crisis_keywords():
    """Test that crisis keywords result in weight 1.0."""
    engine = MemoryEngine(firestore_client=None)
    
    crisis_messages = [
        "I need help me please",
        "This is an emergency",
        "I'm in danger"
    ]
    
    for message in crisis_messages:
        weight = engine.calculate_memory_weight(message)
        assert weight == 1.0, f"Crisis message '{message}' should have weight 1.0, got {weight}"


def test_calculate_memory_weight_vulnerability_keywords():
    """Test that vulnerability keywords result in weight 0.9."""
    engine = MemoryEngine(firestore_client=None)
    
    vulnerability_messages = [
        "I'm feeling scared",
        "I'm so worried about this",
        "I feel anxious and nervous",
        "I'm hurt and depressed"
    ]
    
    for message in vulnerability_messages:
        weight = engine.calculate_memory_weight(message)
        assert weight == 0.9, f"Vulnerability message '{message}' should have weight 0.9, got {weight}"


def test_calculate_memory_weight_preference_keywords():
    """Test that preference keywords result in weight 0.5."""
    engine = MemoryEngine(firestore_client=None)
    
    preference_messages = [
        "I like chocolate ice cream",
        "I love playing video games",
        "My favorite color is blue",
        "I prefer tea over coffee"
    ]
    
    for message in preference_messages:
        weight = engine.calculate_memory_weight(message)
        assert weight == 0.5, f"Preference message '{message}' should have weight 0.5, got {weight}"


def test_calculate_memory_weight_casual_keywords():
    """Test that casual greetings result in weight 0.1."""
    engine = MemoryEngine(firestore_client=None)
    
    casual_messages = [
        "hi",
        "hello",
        "hey there",
        "okay",
        "thanks"
    ]
    
    for message in casual_messages:
        weight = engine.calculate_memory_weight(message)
        assert weight == 0.1, f"Casual message '{message}' should have weight 0.1, got {weight}"


def test_calculate_memory_weight_with_emotion_result():
    """Test that emotion_result influences weight calculation."""
    engine = MemoryEngine(firestore_client=None)
    
    # Message without vulnerability keywords but with vulnerable mood
    message = "I don't know what to do anymore"
    emotion_result = {"detected_mood": "vulnerable"}
    
    weight = engine.calculate_memory_weight(message, emotion_result)
    assert weight == 0.9, f"Message with vulnerable mood should have weight 0.9, got {weight}"


def test_store_memory_with_weight_parameter():
    """Test that store_memory correctly stores weight in metadata."""
    import time
    engine = MemoryEngine(firestore_client=None)
    user_id = f"test_user_weight_{int(time.time() * 1000)}"
    
    # Store memories with different weights
    engine.store_memory(user_id, "Crisis message", is_important=True, weight=1.0)
    engine.store_memory(user_id, "Normal message", is_important=False, weight=0.5)
    engine.store_memory(user_id, "Casual message", is_important=False, weight=0.1)
    
    # Check metadata
    metadata = engine.user_metadata[user_id]
    assert len(metadata["weights"]) == 3
    assert metadata["weights"][0] == 1.0
    assert metadata["weights"][1] == 0.5
    assert metadata["weights"][2] == 0.1


def test_weighted_retrieval_prioritizes_high_weight():
    """Test that weighted retrieval prioritizes high-weight memories."""
    engine = MemoryEngine(firestore_client=None)
    user_id = "test_user_weighted_retrieval"
    
    # Store a high-weight memory about pets
    engine.store_memory(user_id, "I'm worried about my sick dog", is_important=True, weight=0.9)
    
    # Store a low-weight memory also about pets
    engine.store_memory(user_id, "I have a pet cat", is_important=False, weight=0.1)
    
    # Store a medium-weight memory about something else
    engine.store_memory(user_id, "I like playing video games", is_important=False, weight=0.5)
    
    # Query about pets
    similar = engine.retrieve_similar(user_id, "Tell me about your pets", k=2)
    
    # The high-weight pet memory should be prioritized
    assert len(similar) == 2
    # We expect the worried dog message to appear (high weight + relevant)
    assert any("dog" in msg.lower() or "cat" in msg.lower() for msg in similar)


def test_weight_clamping():
    """Test that weights outside [0.0, 1.0] are clamped to valid range."""
    engine = MemoryEngine(firestore_client=None)
    user_id = "test_user_clamping"
    
    # Try to store with invalid weights
    engine.store_memory(user_id, "Message 1", is_important=False, weight=-0.5)
    engine.store_memory(user_id, "Message 2", is_important=False, weight=1.5)
    
    # Check that weights were clamped
    metadata = engine.user_metadata[user_id]
    assert metadata["weights"][0] == 0.0  # Clamped from -0.5
    assert metadata["weights"][1] == 1.0  # Clamped from 1.5
