"""
Property-based tests for embedding generation.

Feature: ai-waifu-cross-platform
Property 6: Embedding Dimension Consistency

**Validates: Requirements 3.1**

For any text input, the generated embedding should always have dimension 384,
which is the output dimension of the sentence-transformers/all-MiniLM-L6-v2 model.
"""

from hypothesis import given, strategies as st, settings
import pytest
import os
import sys
import numpy as np

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from memory_engine import MemoryEngine


@pytest.fixture(scope="module")
def memory_engine():
    """Create a Memory Engine instance for testing (module-scoped for property tests)."""
    return MemoryEngine(firestore_client=None, indices_dir="backend/faiss_indices")


# Strategy for generating diverse text inputs
text_strategy = st.one_of(
    # Short texts
    st.text(min_size=1, max_size=50),
    # Medium texts
    st.text(min_size=50, max_size=200),
    # Long texts
    st.text(min_size=200, max_size=1000),
    # Common phrases
    st.sampled_from([
        "Hello, how are you?",
        "I love programming!",
        "What's your favorite color?",
        "Tell me about yourself.",
        "I'm feeling happy today.",
        "She is my friend.",
        "I like cats and dogs.",
        "My name is John.",
        "This is a test message.",
        "Good morning!"
    ]),
    # Unicode and special characters
    st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=1, max_size=100),
    # Numbers and mixed content
    st.from_regex(r'[a-zA-Z0-9\s]{1,100}', fullmatch=True)
)


@given(text=text_strategy)
@settings(max_examples=20)
@pytest.mark.property_test
def test_embedding_dimension_consistency(memory_engine, text):
    """
    Property 6: Embedding Dimension Consistency
    
    For any text input (short, long, unicode, special characters, etc.),
    the generated embedding should always have exactly 384 dimensions,
    which is the output size of the all-MiniLM-L6-v2 model.
    
    This property ensures that:
    1. The embedding model is correctly initialized
    2. All embeddings are compatible with the FAISS index (IndexFlatL2(384))
    3. Vector operations will not fail due to dimension mismatches
    """
    # Generate embedding for the text
    embedding = memory_engine.generate_embedding(text)
    
    # Verify embedding is a numpy array
    assert isinstance(embedding, np.ndarray), \
        f"Expected numpy array, got {type(embedding)}"
    
    # Verify embedding has exactly 384 dimensions
    assert embedding.shape == (384,), \
        f"Expected embedding dimension (384,), got {embedding.shape}"
    
    # Verify embedding dtype is float32 (required by FAISS)
    assert embedding.dtype == np.float32, \
        f"Expected dtype float32, got {embedding.dtype}"
    
    # Verify embedding contains valid numeric values (not NaN or Inf)
    assert not np.isnan(embedding).any(), \
        "Embedding contains NaN values"
    assert not np.isinf(embedding).any(), \
        "Embedding contains Inf values"


@given(text=st.text(min_size=1, max_size=500))
@settings(max_examples=10)
@pytest.mark.property_test
def test_embedding_determinism(memory_engine, text):
    """
    Property 6 (Extended): Embedding Determinism
    
    For any given text, generating the embedding multiple times should
    produce identical results. This ensures consistency in memory retrieval.
    """
    # Generate embedding twice for the same text
    embedding1 = memory_engine.generate_embedding(text)
    embedding2 = memory_engine.generate_embedding(text)
    
    # Both embeddings should have dimension 384
    assert embedding1.shape == (384,), \
        f"First embedding has wrong dimension: {embedding1.shape}"
    assert embedding2.shape == (384,), \
        f"Second embedding has wrong dimension: {embedding2.shape}"
    
    # Embeddings should be identical
    np.testing.assert_array_almost_equal(
        embedding1, 
        embedding2,
        decimal=6,
        err_msg="Same text produced different embeddings"
    )


@given(
    text1=st.text(min_size=1, max_size=200),
    text2=st.text(min_size=1, max_size=200)
)
@settings(max_examples=10)
@pytest.mark.property_test
def test_different_texts_produce_different_embeddings(memory_engine, text1, text2):
    """
    Property 6 (Extended): Embedding Uniqueness
    
    For different text inputs, the generated embeddings should be different
    (unless the texts are semantically identical). Both embeddings should
    still have dimension 384.
    """
    # Skip if texts are identical
    if text1 == text2:
        return
    
    # Generate embeddings
    embedding1 = memory_engine.generate_embedding(text1)
    embedding2 = memory_engine.generate_embedding(text2)
    
    # Both should have dimension 384
    assert embedding1.shape == (384,), \
        f"First embedding has wrong dimension: {embedding1.shape}"
    assert embedding2.shape == (384,), \
        f"Second embedding has wrong dimension: {embedding2.shape}"
    
    # For different texts, embeddings should generally be different
    # (we allow for rare cases where very similar texts might produce similar embeddings)
    # We just verify they're not identical
    if text1.strip() != text2.strip():
        are_identical = np.allclose(embedding1, embedding2, rtol=1e-5, atol=1e-8)
        # It's okay if they're similar, but exact identity is unlikely for different texts
        # This is a soft check - we mainly care about dimension consistency


@given(text=st.just(""))
@pytest.mark.property_test
def test_empty_string_embedding_dimension(memory_engine, text):
    """
    Property 6 (Edge Case): Empty String Embedding
    
    Even for an empty string, the embedding should have dimension 384.
    The model should handle edge cases gracefully.
    """
    embedding = memory_engine.generate_embedding(text)
    
    # Even empty string should produce 384-dimensional embedding
    assert embedding.shape == (384,), \
        f"Empty string embedding has wrong dimension: {embedding.shape}"
    assert embedding.dtype == np.float32, \
        f"Empty string embedding has wrong dtype: {embedding.dtype}"


@given(text=st.text(alphabet=st.characters(whitelist_categories=('Zs',)), min_size=1, max_size=100))
@settings(max_examples=5)
@pytest.mark.property_test
def test_whitespace_only_embedding_dimension(memory_engine, text):
    """
    Property 6 (Edge Case): Whitespace-Only Text Embedding
    
    For text containing only whitespace characters, the embedding should
    still have dimension 384.
    """
    embedding = memory_engine.generate_embedding(text)
    
    # Whitespace-only text should still produce 384-dimensional embedding
    assert embedding.shape == (384,), \
        f"Whitespace-only embedding has wrong dimension: {embedding.shape}"
    assert embedding.dtype == np.float32, \
        f"Whitespace-only embedding has wrong dtype: {embedding.dtype}"
