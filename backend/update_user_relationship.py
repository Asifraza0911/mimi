"""
Script to update user relationship status in Firestore.
This allows manually setting affection levels and relationship stages.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

# Initialize Firebase
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def update_user_to_close(user_id: str):
    """
    Update user to have a 'close' relationship with Mimi.
    
    Sets:
    - Affection level: 65 (Close range is 51-80)
    - Trust level: 60
    - Relationship stage: close
    - Mood: happy
    - Attachment state: secure
    - Daily interaction streak: 7 (milestone)
    """
    
    print(f"Updating relationship for user: {user_id}")
    
    # Get user document
    doc_ref = db.collection("waifu_memory").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"User {user_id} not found. Creating new user with close relationship...")
        # Create new user with close relationship
        user_data = {
            "user_id": user_id,
            "name": None,
            "affection_level": 65,
            "trust_level": 60,
            "mood": "happy",
            "relationship_stage": "close",
            "attachment_state": "secure",
            "long_term_memory": [],
            "emotional_memory": [],
            "last_interaction": datetime.now(),
            "last_chat_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "daily_interaction_streak": 7,
            "created_at": datetime.now(),
            "platform_stats": {"web": 0, "discord": 0}
        }
        doc_ref.set(user_data)
        print("✅ New user created with close relationship!")
    else:
        # Update existing user
        updates = {
            "affection_level": 65,
            "trust_level": 60,
            "mood": "happy",
            "relationship_stage": "close",
            "attachment_state": "secure",
            "daily_interaction_streak": 7,
            "last_interaction": datetime.now(),
            "last_chat_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }
        doc_ref.update(updates)
        print("✅ User relationship updated to close!")
    
    # Display final stats
    print("\n" + "="*50)
    print("Updated Relationship Status:")
    print("="*50)
    print(f"User ID:              {user_id}")
    print(f"Affection Level:      65/100 💜")
    print(f"Trust Level:          60/100")
    print(f"Relationship Stage:   Close")
    print(f"Mood:                 Happy 😊")
    print(f"Attachment State:     Secure")
    print(f"Interaction Streak:   7 days 🔥")
    print("="*50)
    print("\nMimi now considers this user as someone close to her!")
    print("She'll be more open, caring, and show her dere side more often. 💕")

if __name__ == "__main__":
    # Target user ID
    USER_ID = "1076883627083837573"
    
    try:
        update_user_to_close(USER_ID)
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        sys.exit(1)
