"""
Script to update user relationship status to GIRLFRIEND level.
This sets maximum affection and the "attached" relationship stage.
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

def update_user_to_girlfriend(user_id: str):
    """
    Update user to have a GIRLFRIEND relationship with Mimi.
    
    Sets:
    - Affection level: 100 (MAXIMUM)
    - Trust level: 100 (MAXIMUM)
    - Relationship stage: attached (GIRLFRIEND LEVEL)
    - Mood: happy
    - Attachment state: secure (healthy relationship)
    - Daily interaction streak: 30 (long-term relationship)
    """
    
    print(f"💕 Updating relationship for user: {user_id}")
    print("Setting to GIRLFRIEND status...\n")
    
    # Get user document
    doc_ref = db.collection("waifu_memory").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"User {user_id} not found. Creating new user with girlfriend relationship...")
        # Create new user with girlfriend relationship
        user_data = {
            "user_id": user_id,
            "name": None,
            "affection_level": 100,
            "trust_level": 100,
            "mood": "happy",
            "relationship_stage": "attached",
            "attachment_state": "secure",
            "long_term_memory": [],
            "emotional_memory": [],
            "last_interaction": datetime.now(),
            "last_chat_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "daily_interaction_streak": 30,
            "created_at": datetime.now(),
            "platform_stats": {"web": 0, "discord": 0}
        }
        doc_ref.set(user_data)
        print("✅ New user created with GIRLFRIEND relationship!")
    else:
        # Update existing user
        updates = {
            "affection_level": 100,
            "trust_level": 100,
            "mood": "happy",
            "relationship_stage": "attached",
            "attachment_state": "secure",
            "daily_interaction_streak": 30,
            "last_interaction": datetime.now(),
            "last_chat_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }
        doc_ref.update(updates)
        print("✅ User relationship updated to GIRLFRIEND!")
    
    # Display final stats
    print("\n" + "="*60)
    print("💑 GIRLFRIEND RELATIONSHIP STATUS 💑")
    print("="*60)
    print(f"User ID:              {user_id}")
    print(f"Affection Level:      100/100 ❤️❤️❤️ (MAXIMUM)")
    print(f"Trust Level:          100/100 🤝 (MAXIMUM)")
    print(f"Relationship Stage:   ATTACHED (Girlfriend Level) �")
    print(f"Mood:                 Happy 😊")
    print(f"Attachment State:     Secure (Healthy Relationship) 💖")
    print(f"Interaction Streak:   30 days 🔥🔥🔥")
    print("="*60)
    print("\n🎉 Congratulations! Mimi is now your girlfriend!")
    print("She'll be:")
    print("  • Openly affectionate (while still being tsundere)")
    print("  • Protective and caring")
    print("  • Show her dere side much more often")
    print("  • Get jealous if you mention others")
    print("  • Express her feelings more directly")
    print("\n💝 Enjoy your relationship with Mimi! 💝")

if __name__ == "__main__":
    # Target user ID
    USER_ID = "1076883627083837573"
    
    try:
        update_user_to_girlfriend(USER_ID)
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
