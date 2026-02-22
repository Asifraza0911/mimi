"""
Memory Engine Module

This module handles semantic memory storage and retrieval using FAISS vector database
and sentence-transformers for embedding generation.

Requirements: 3.1, 3.6
"""

import os
import json
import logging
import hashlib
import numpy as np
import faiss
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from datetime import datetime

logger = logging.getLogger("ai_waifu.memory_engine")


class MemoryEngine:
    """
    Manages semantic memory using FAISS vector database and sentence transformers.
    
    Responsibilities:
    - Generate embeddings for messages using sentence-transformers
    - Store and retrieve vectors from FAISS indices
    - Manage per-user FAISS indices
    - Coordinate with Firestore for long-term memory
    """
    
    def __init__(self, firestore_client, indices_dir: str = "backend/faiss_indices"):
        """
        Initialize Memory Engine with sentence transformer model.
        
        Args:
            firestore_client: Firebase Firestore client instance
            indices_dir: Directory path for storing FAISS indices
        """
        self.firestore = firestore_client
        self.indices_dir = indices_dir
        
        # Initialize sentence transformer model (all-MiniLM-L6-v2)
        # This model generates 384-dimensional embeddings
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # In-memory cache of user FAISS indices
        self.user_indices: Dict[str, faiss.Index] = {}
        
        # In-memory cache of metadata (messages, timestamps, weights)
        self.user_metadata: Dict[str, Dict] = {}
        
        # Create indices directory if it doesn't exist
        os.makedirs(self.indices_dir, exist_ok=True)
    
    def _sanitize_user_id(self, user_id: str) -> str:
        """
        Sanitize user_id to create a safe filename.
        
        Uses SHA-256 hash to convert any user_id (including those with special
        Unicode characters) into a safe, filesystem-compatible filename.
        
        Args:
            user_id: Original user identifier (may contain Unicode or special chars)
            
        Returns:
            Sanitized filename-safe string (hex digest of SHA-256 hash)
        """
        # Use SHA-256 hash to create a safe, unique filename
        # This handles all Unicode characters and special characters
        return hashlib.sha256(user_id.encode('utf-8')).hexdigest()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector using sentence-transformers.
        
        Args:
            text: Input text to convert to embedding
            
        Returns:
            numpy array of shape (384,) representing the text embedding
            
        Requirements: 3.1
        """
        # Generate embedding using the sentence transformer model
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')
    
    def get_or_create_index(self, user_id: str) -> faiss.Index:
        """
        Get existing FAISS index for user or create a new one.
        
        Args:
            user_id: User identifier
            
        Returns:
            FAISS Index instance for the user
            
        Requirements: 3.3, 3.6
        """
        # Check if index is already in memory
        if user_id in self.user_indices:
            return self.user_indices[user_id]
        
        # Sanitize user_id for safe file paths
        safe_user_id = self._sanitize_user_id(user_id)
        
        # Try to load index from disk
        index_path = os.path.join(self.indices_dir, f"{safe_user_id}.index")
        metadata_path = os.path.join(self.indices_dir, f"{safe_user_id}_metadata.json")
        
        if os.path.exists(index_path):
            # Load existing index from disk
            index = faiss.read_index(index_path)
            
            # Load metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                # Create empty metadata if file doesn't exist
                metadata = {
                    "messages": [],
                    "timestamps": [],
                    "weights": [],
                    "vector_count": 0
                }
        else:
            # Create new index (IndexFlatL2 with dimension 384)
            index = faiss.IndexFlatL2(384)
            
            # Create empty metadata
            metadata = {
                "messages": [],
                "timestamps": [],
                "weights": [],
                "vector_count": 0
            }
        
        # Cache in memory
        self.user_indices[user_id] = index
        self.user_metadata[user_id] = metadata
        
        return index
    
    def _persist_index(self, user_id: str):
        """
        Save FAISS index and metadata to disk.
        
        Args:
            user_id: User identifier
        """
        if user_id not in self.user_indices:
            return
        
        # Sanitize user_id for safe file paths
        safe_user_id = self._sanitize_user_id(user_id)
        
        # Save index to disk
        index_path = os.path.join(self.indices_dir, f"{safe_user_id}.index")
        faiss.write_index(self.user_indices[user_id], index_path)
        
        # Save metadata to disk
        metadata_path = os.path.join(self.indices_dir, f"{safe_user_id}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_metadata[user_id], f, indent=2)
    
    def calculate_memory_weight(self, message: str, emotion_result: Optional[Dict] = None) -> float:
        """
        Calculate importance weight for a memory based on content and emotional context.
        
        Args:
            message: Message text to evaluate
            emotion_result: Optional emotion detection result with detected_mood and triggers
            
        Returns:
            Weight value between 0.0 and 1.0
            
        Weight categories:
        - 1.0: Crisis statements (help, emergency, danger)
        - 0.9: Emotional vulnerability (scared, worried, anxious, hurt, depressed)
        - 0.5: Preferences and factual information (I like, I prefer, my favorite)
        - 0.1: Casual greetings and acknowledgments (hi, hello, okay, thanks)
        
        Requirements: 17.2, 17.7, 17.8, 17.9
        """
        message_lower = message.lower()
        
        # Crisis keywords (weight 1.0)
        crisis_keywords = ["help me", "emergency", "danger", "crisis", "suicide", "kill myself", "end it all"]
        if any(keyword in message_lower for keyword in crisis_keywords):
            return 1.0
        
        # Emotional vulnerability keywords (weight 0.9)
        vulnerability_keywords = ["scared", "worried", "anxious", "nervous", "hurt", "depressed", "sad", "crying", "alone", "lonely"]
        if any(keyword in message_lower for keyword in vulnerability_keywords):
            return 0.9
        
        # Check emotion_result for vulnerability mood
        if emotion_result and emotion_result.get("detected_mood") in ["vulnerable", "sad"]:
            return 0.9
        
        # Preference keywords (weight 0.5)
        preference_keywords = ["i like", "i love", "i prefer", "my favorite", "i enjoy", "i hate", "i dislike"]
        if any(keyword in message_lower for keyword in preference_keywords):
            return 0.5
        
        # Casual greetings and acknowledgments (weight 0.1)
        casual_keywords = ["hi", "hello", "hey", "okay", "ok", "thanks", "thank you", "bye", "goodbye"]
        # Check if message is ONLY a casual greeting (short message)
        if len(message.split()) <= 3 and any(message_lower.strip() == keyword or message_lower.strip().startswith(keyword) for keyword in casual_keywords):
            return 0.1
        
        # Default weight for normal conversation
        return 0.5
    
    def store_memory(self, user_id: str, message: str, is_important: bool = False, weight: float = 0.5):
        """
        Store message in vector database and optionally in Firestore.
        
        Args:
            user_id: User identifier
            message: Message text to store
            is_important: Whether to persist to Firestore long_term_memory
            weight: Memory importance weight (0.0-1.0), default 0.5
            
        Requirements: 3.2, 3.3, 8.4, 17.1, 17.3
        """
        # Clamp weight to valid range [0.0, 1.0]
        weight = max(0.0, min(1.0, weight))
        
        logger.debug(f"Storing memory for user {user_id}: weight={weight:.2f}, important={is_important}")
        
        # Generate embedding for the message
        embedding = self.generate_embedding(message)
        
        # Get or create user's FAISS index
        index = self.get_or_create_index(user_id)
        
        # Add vector to FAISS index
        # FAISS expects 2D array, so reshape to (1, 384)
        index.add(embedding.reshape(1, -1))
        
        # Update metadata
        metadata = self.user_metadata[user_id]
        metadata["messages"].append(message)
        metadata["timestamps"].append(datetime.now().isoformat())
        metadata["weights"].append(weight)
        metadata["vector_count"] = index.ntotal
        
        # Persist to disk
        self._persist_index(user_id)
        
        logger.info(f"Memory stored for user {user_id}: total_vectors={index.ntotal}, weight={weight:.2f}")
        
        # Optionally store in Firestore long_term_memory
        if is_important and self.firestore:
            try:
                from google.cloud.firestore import ArrayUnion
                user_ref = self.firestore.collection('waifu_memory').document(user_id)
                user_ref.update({
                    'long_term_memory': ArrayUnion([{
                        'text': message,
                        'weight': weight,
                        'timestamp': datetime.now().isoformat()
                    }])
                })
                logger.info(f"Important memory persisted to Firestore for user {user_id}")
            except Exception as e:
                # Log error but don't fail the operation
                logger.error(f"Failed to store memory in Firestore for user {user_id}: {e}")
    
    def retrieve_similar(self, user_id: str, query: str, k: int = 3) -> List[str]:
        """
        Retrieve k most similar past conversations using weighted vector similarity search.
        
        Memories are ranked by the product of similarity_score * Memory_Weight.
        This prioritizes emotionally significant memories even if similarity is moderate.
        Each memory is returned with its timestamp for temporal context.
        
        Args:
            user_id: User identifier
            query: Current message to find similar memories for
            k: Number of results to return (default: 3)
            
        Returns:
            List of similar past messages with timestamps (up to k messages), ranked by weighted score
            Format: "[timestamp] message text"
            
        Requirements: 3.4, 17.4, 17.5, 17.6, 17.10
        """
        # Get user's FAISS index
        index = self.get_or_create_index(user_id)
        
        # Check if index has any vectors
        if index.ntotal == 0:
            logger.debug(f"No memories found for user {user_id}")
            return []
        
        logger.debug(f"Retrieving similar memories for user {user_id}: total_vectors={index.ntotal}, k={k}")
        
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        # Perform similarity search
        # FAISS expects 2D array, so reshape to (1, 384)
        # Retrieve more results than k to allow for weighted re-ranking
        search_k = min(index.ntotal, k * 3)  # Get 3x results for re-ranking
        
        # Search returns distances and indices
        # Lower distance = higher similarity
        distances, indices = index.search(query_embedding.reshape(1, -1), search_k)
        
        # Retrieve corresponding messages and weights from metadata
        metadata = self.user_metadata[user_id]
        
        # Calculate weighted scores
        weighted_results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(metadata["messages"]):
                # Convert L2 distance to similarity score (inverse relationship)
                # Use exponential decay: similarity = exp(-distance)
                similarity_score = np.exp(-distances[0][i])
                
                # Get weight for this memory (default to 0.5 if not present)
                weight = metadata["weights"][idx] if idx < len(metadata["weights"]) else 0.5
                
                # Get timestamp for this memory
                timestamp = metadata["timestamps"][idx] if idx < len(metadata["timestamps"]) else None
                
                # Calculate weighted score
                weighted_score = similarity_score * weight
                
                weighted_results.append({
                    "message": metadata["messages"][idx],
                    "timestamp": timestamp,
                    "weighted_score": weighted_score,
                    "similarity": similarity_score,
                    "weight": weight
                })
        
        # Sort by weighted score (descending)
        weighted_results.sort(key=lambda x: x["weighted_score"], reverse=True)
        
        # Return top k messages with timestamps
        similar_messages = []
        for result in weighted_results[:k]:
            # Format timestamp for readability
            if result["timestamp"]:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(result["timestamp"])
                    time_str = dt.strftime("%b %d at %I:%M %p")
                    similar_messages.append(f"[{time_str}] {result['message']}")
                except:
                    similar_messages.append(result["message"])
            else:
                similar_messages.append(result["message"])
        
        logger.info(f"Retrieved {len(similar_messages)} similar memories for user {user_id}")
        if weighted_results:
            logger.debug(f"Top memory: weight={weighted_results[0]['weight']:.2f}, similarity={weighted_results[0]['similarity']:.3f}")
        
        return similar_messages
