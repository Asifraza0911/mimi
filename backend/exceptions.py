"""
Custom exception classes for the AI Waifu Cross-Platform System.

This module defines a hierarchy of exceptions for different error types
that can occur throughout the system, enabling proper error handling
and graceful degradation.

Exception Hierarchy:
    AIWaifuException (base)
    ├── FirestoreConnectionError
    ├── LLMServiceError
    ├── MemoryEngineError
    └── EmotionEngineError
"""


class AIWaifuException(Exception):
    """
    Base exception for all AI Waifu system errors.
    
    All custom exceptions in the system inherit from this base class,
    allowing for centralized error handling and logging.
    """
    pass


class FirestoreConnectionError(AIWaifuException):
    """
    Raised when Firestore database is unavailable or connection fails.
    
    This exception indicates that the persistent storage layer cannot be
    accessed. The system should fall back to in-memory defaults when this
    occurs.
    
    Examples:
        - Firestore service is down
        - Network connectivity issues
        - Authentication failures
        - Quota exceeded
    """
    pass


class LLMServiceError(AIWaifuException):
    """
    Raised when HuggingFace API encounters an error or timeout.
    
    This exception indicates that the language model service cannot generate
    a response. The system should return a predefined fallback response when
    this occurs.
    
    Examples:
        - API rate limiting
        - Model loading timeout
        - Invalid API token
        - Service unavailable
        - Network timeout
    """
    pass


class MemoryEngineError(AIWaifuException):
    """
    Raised when FAISS vector database or embedding generation fails.
    
    This exception indicates that the semantic memory retrieval system
    cannot function. The system should proceed without vector memory
    retrieval when this occurs.
    
    Examples:
        - FAISS index corruption
        - Embedding model loading failure
        - Vector dimension mismatch
        - Out of memory errors
    """
    pass


class EmotionEngineError(AIWaifuException):
    """
    Raised when emotion detection processing encounters an error.
    
    This exception indicates that the emotional keyword detection system
    cannot analyze the user's message. The system should default to neutral
    mood when this occurs.
    
    Examples:
        - Invalid input format
        - Keyword matching failure
        - Mood update processing error
    """
    pass
