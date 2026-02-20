"""
Firestore user document operations for AI Waifu Cross-Platform System.

This module provides functions for creating, retrieving, and updating
user relationship data in Firebase Firestore.
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from google.cloud.firestore import Client
from models import UserData, MemoryEntry, EmotionalMemoryEntry

logger = logging.getLogger("ai_waifu.firestore_operations")


def get_or_create_user(db: Client, user_id: str) -> UserData:
    """
    Retrieve user data from Firestore or create a new user with default values.
    
    This function implements the user initialization logic as specified in
    Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7.
    
    Args:
        db: Firestore client instance
        user_id: Unique user identifier
        
    Returns:
        UserData: User relationship state with all fields populated
        
    Raises:
        Exception: If Firestore operation fails
    """
    try:
        # Reference to the user document
        user_ref = db.collection("waifu_memory").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            # User exists, retrieve and parse data
            logger.info(f"Retrieved existing user data for user_id: {user_id}")
            data = user_doc.to_dict()
            
            # Convert Firestore timestamps to datetime objects
            if "last_interaction" in data and data["last_interaction"]:
                data["last_interaction"] = data["last_interaction"]
            
            if "created_at" in data and data["created_at"]:
                data["created_at"] = data["created_at"]
            
            # Convert last_chat_date to date object if it exists
            if "last_chat_date" in data and data["last_chat_date"]:
                if isinstance(data["last_chat_date"], datetime):
                    data["last_chat_date"] = data["last_chat_date"].date()
            
            # Parse long_term_memory entries
            if "long_term_memory" in data and data["long_term_memory"]:
                data["long_term_memory"] = [
                    MemoryEntry(**entry) if isinstance(entry, dict) else entry
                    for entry in data["long_term_memory"]
                ]
            
            # Parse emotional_memory entries
            if "emotional_memory" in data and data["emotional_memory"]:
                data["emotional_memory"] = [
                    EmotionalMemoryEntry(**entry) if isinstance(entry, dict) else entry
                    for entry in data["emotional_memory"]
                ]
            
            # Ensure user_id is set
            data["user_id"] = user_id
            
            logger.debug(f"User {user_id}: affection={data.get('affection_level')}, mood={data.get('mood')}, stage={data.get('relationship_stage')}")
            
            return UserData(**data)
        
        else:
            # User doesn't exist, create with default values
            logger.info(f"Creating new user with default values for user_id: {user_id}")
            now = datetime.now()
            today = date.today()
            
            default_user_data = UserData(
                user_id=user_id,
                name=None,
                affection_level=10,
                trust_level=5,
                mood="neutral",
                relationship_stage="stranger",
                attachment_state="avoidant",
                long_term_memory=[],
                emotional_memory=[],
                last_interaction=now,
                last_chat_date=today,
                daily_interaction_streak=1,
                created_at=now,
                platform_stats={"web": 0, "discord": 0}
            )
            
            # Convert to dictionary for Firestore storage
            user_dict = default_user_data.model_dump()
            
            # Convert MemoryEntry and EmotionalMemoryEntry objects to dicts
            user_dict["long_term_memory"] = [
                entry.model_dump() if hasattr(entry, "model_dump") else entry
                for entry in user_dict["long_term_memory"]
            ]
            user_dict["emotional_memory"] = [
                entry.model_dump() if hasattr(entry, "model_dump") else entry
                for entry in user_dict["emotional_memory"]
            ]
            
            # Store in Firestore
            user_ref.set(user_dict)
            logger.info(f"New user {user_id} created successfully with default values")
            
            return default_user_data
    
    except Exception as e:
        logger.error(f"Failed to get or create user {user_id}: {str(e)}")
        raise Exception(f"Failed to get or create user {user_id}: {str(e)}")


def update_user_data(db: Client, user_id: str, updates: Dict[str, Any]) -> None:
    """
    Update specific fields in a user's Firestore document.
    
    This function allows partial updates to user relationship data without
    overwriting the entire document.
    
    Args:
        db: Firestore client instance
        user_id: Unique user identifier
        updates: Dictionary of field names and values to update
        
    Raises:
        Exception: If Firestore operation fails
        
    Example:
        update_user_data(db, "user123", {
            "affection_level": 25,
            "mood": "happy",
            "last_interaction": datetime.now()
        })
    """
    try:
        user_ref = db.collection("waifu_memory").document(user_id)
        
        # Convert Pydantic models to dicts if present in updates
        processed_updates = {}
        for key, value in updates.items():
            if hasattr(value, "model_dump"):
                processed_updates[key] = value.model_dump()
            elif isinstance(value, list):
                # Handle lists of Pydantic models
                processed_updates[key] = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in value
                ]
            else:
                processed_updates[key] = value
        
        # Update the document
        user_ref.update(processed_updates)
        logger.info(f"Updated user {user_id} with fields: {list(processed_updates.keys())}")
        logger.debug(f"Update values for user {user_id}: {processed_updates}")
    
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {str(e)}")
        raise Exception(f"Failed to update user {user_id}: {str(e)}")


def get_user_data(db: Client, user_id: str) -> Optional[UserData]:
    """
    Retrieve user data from Firestore without creating if it doesn't exist.
    
    This function is useful for checking if a user exists without side effects.
    
    Args:
        db: Firestore client instance
        user_id: Unique user identifier
        
    Returns:
        UserData: User relationship state if user exists
        None: If user doesn't exist
        
    Raises:
        Exception: If Firestore operation fails
    """
    try:
        user_ref = db.collection("waifu_memory").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
        
        # Parse document data
        data = user_doc.to_dict()
        
        # Convert Firestore timestamps to datetime objects
        if "last_interaction" in data and data["last_interaction"]:
            data["last_interaction"] = data["last_interaction"]
        
        if "created_at" in data and data["created_at"]:
            data["created_at"] = data["created_at"]
        
        # Convert last_chat_date to date object if it exists
        if "last_chat_date" in data and data["last_chat_date"]:
            if isinstance(data["last_chat_date"], datetime):
                data["last_chat_date"] = data["last_chat_date"].date()
        
        # Parse long_term_memory entries
        if "long_term_memory" in data and data["long_term_memory"]:
            data["long_term_memory"] = [
                MemoryEntry(**entry) if isinstance(entry, dict) else entry
                for entry in data["long_term_memory"]
            ]
        
        # Parse emotional_memory entries
        if "emotional_memory" in data and data["emotional_memory"]:
            data["emotional_memory"] = [
                EmotionalMemoryEntry(**entry) if isinstance(entry, dict) else entry
                for entry in data["emotional_memory"]
            ]
        
        # Ensure user_id is set
        data["user_id"] = user_id
        
        return UserData(**data)
    
    except Exception as e:
        raise Exception(f"Failed to get user {user_id}: {str(e)}")
