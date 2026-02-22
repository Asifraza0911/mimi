"""
Diagnostic script to check memory storage and retrieval for a user.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.memory_engine import MemoryEngine
from google.cloud import firestore

# Initialize Firestore
credentials_path = os.path.join(os.path.dirname(__file__), "..", "firebase-credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
db = firestore.Client()

# Initialize Memory Engine
memory_engine = MemoryEngine(db)

# User ID to check
USER_ID = "1076883627083837573"

print(f"=== Memory Diagnostic for User {USER_ID} ===\n")

# Check FAISS index
try:
    index = memory_engine.get_or_create_index(USER_ID)
    metadata = memory_engine.user_metadata.get(USER_ID, {})
    
    print(f"FAISS Vector Memory:")
    print(f"  Total vectors: {index.ntotal}")
    print(f"  Messages stored: {len(metadata.get('messages', []))}")
    print(f"  Timestamps stored: {len(metadata.get('timestamps', []))}")
    print(f"  Weights stored: {len(metadata.get('weights', []))}")
    print()
    
    if metadata.get('messages'):
        print("Recent memories:")
        messages = metadata['messages'][-10:]  # Last 10
        timestamps = metadata.get('timestamps', [])[-10:]
        weights = metadata.get('weights', [])[-10:]
        
        for i, msg in enumerate(messages):
            ts = timestamps[i] if i < len(timestamps) else "N/A"
            wt = weights[i] if i < len(weights) else "N/A"
            print(f"  [{ts}] (weight: {wt}) {msg[:80]}...")
        print()
    
    # Test retrieval
    test_query = "what was i doing"
    print(f"Testing retrieval with query: '{test_query}'")
    similar = memory_engine.retrieve_similar(USER_ID, test_query, k=5)
    print(f"  Retrieved {len(similar)} memories:")
    for mem in similar:
        print(f"    - {mem}")
    print()
    
except Exception as e:
    print(f"Error checking FAISS memory: {e}")
    import traceback
    traceback.print_exc()

# Check Firestore long-term memory
try:
    user_ref = db.collection('waifu_memory').document(USER_ID)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        data = user_doc.to_dict()
        long_term = data.get('long_term_memory', [])
        
        print(f"Firestore Long-Term Memory:")
        print(f"  Total entries: {len(long_term)}")
        
        if long_term:
            print("  Entries:")
            for entry in long_term[-10:]:  # Last 10
                if isinstance(entry, dict):
                    print(f"    - (weight: {entry.get('weight', 'N/A')}) {entry.get('text', entry)[:80]}...")
                else:
                    print(f"    - {entry[:80]}...")
        print()
    else:
        print(f"User {USER_ID} not found in Firestore")
        
except Exception as e:
    print(f"Error checking Firestore: {e}")
    import traceback
    traceback.print_exc()

print("=== Diagnostic Complete ===")
