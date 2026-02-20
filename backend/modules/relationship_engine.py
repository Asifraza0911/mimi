"""
Relationship Engine module for AI Waifu Cross-Platform System.

This module analyzes user messages for sentiment, updates affection and trust levels,
determines relationship stages, and persists changes to Firestore.
"""

import logging
from typing import Optional
from models import SentimentScore, RelationshipUpdate, UserData
from modules.firestore_operations import update_user_data

logger = logging.getLogger("ai_waifu.relationship_engine")


class RelationshipEngine:
    """
    Manages relationship progression based on user interactions.
    
    Analyzes message sentiment, calculates affection/trust changes,
    determines relationship stages, and persists updates to Firestore.
    """
    
    def __init__(self, firestore_client, attachment_style_engine=None):
        """
        Initialize Relationship Engine.
        
        Args:
            firestore_client: Firebase Firestore client instance
            attachment_style_engine: Optional AttachmentStyleEngine instance
        """
        self.firestore = firestore_client
        self.attachment_style_engine = attachment_style_engine
        
        # Define relationship stage thresholds
        self.stage_thresholds = {
            "stranger": (0, 20),
            "friend": (21, 50),
            "close": (51, 80),
            "attached": (81, 100)
        }
        
        # Keywords for sentiment detection
        self.compliment_keywords = [
            "beautiful", "pretty", "cute", "amazing", "wonderful",
            "love you", "like you", "appreciate", "thank you",
            "you're great", "you're awesome", "you're the best"
        ]
        
        self.vulnerability_keywords = [
            "scared", "worried", "anxious", "nervous", "afraid",
            "sad", "depressed", "lonely", "hurt", "struggling",
            "need help", "feeling down", "not okay"
        ]
        
        self.rude_keywords = [
            "stupid", "dumb", "annoying", "shut up", "hate you",
            "go away", "leave me alone", "don't care", "whatever",
            "boring", "useless"
        ]
        
        self.positive_keywords = [
            "good", "great", "nice", "happy", "excited",
            "fun", "interesting", "cool", "awesome"
        ]
        
        self.negative_keywords = [
            "bad", "terrible", "awful", "horrible", "worst",
            "hate", "angry", "mad", "upset"
        ]
    
    def analyze_sentiment(self, message: str) -> SentimentScore:
        """
        Analyze message sentiment to classify emotional tone.
        
        Args:
            message: User's message text
            
        Returns:
            SentimentScore with sentiment type and intensity
        """
        message_lower = message.lower()
        
        # Check for compliments (highest priority for positive sentiment)
        if any(keyword in message_lower for keyword in self.compliment_keywords):
            return SentimentScore(sentiment_type="compliment", intensity=0.9)
        
        # Check for vulnerability/emotional sharing
        if any(keyword in message_lower for keyword in self.vulnerability_keywords):
            return SentimentScore(sentiment_type="vulnerability", intensity=0.8)
        
        # Check for rude/negative messages
        if any(keyword in message_lower for keyword in self.rude_keywords):
            return SentimentScore(sentiment_type="rude", intensity=0.9)
        
        # Check for general positive sentiment
        if any(keyword in message_lower for keyword in self.positive_keywords):
            return SentimentScore(sentiment_type="positive", intensity=0.6)
        
        # Check for general negative sentiment
        if any(keyword in message_lower for keyword in self.negative_keywords):
            return SentimentScore(sentiment_type="negative", intensity=0.6)
        
        # Default to neutral
        return SentimentScore(sentiment_type="neutral", intensity=0.5)
    
    def calculate_affection_delta(self, sentiment: SentimentScore) -> int:
        """
        Calculate affection level change based on sentiment.
        
        Args:
            sentiment: Analyzed sentiment score
            
        Returns:
            Affection points to add/subtract
        """
        if sentiment.sentiment_type == "compliment":
            return +3
        elif sentiment.sentiment_type == "vulnerability":
            return +2
        elif sentiment.sentiment_type == "positive":
            return +1
        elif sentiment.sentiment_type == "rude":
            return -3
        elif sentiment.sentiment_type == "negative":
            return -1
        else:  # neutral
            return 0
    
    def calculate_trust_delta(self, sentiment: SentimentScore) -> int:
        """
        Calculate trust level change based on sentiment.
        
        Vulnerability increases trust as user shares emotions.
        
        Args:
            sentiment: Analyzed sentiment score
            
        Returns:
            Trust points to add
        """
        if sentiment.sentiment_type == "vulnerability":
            return +2
        elif sentiment.sentiment_type == "compliment":
            return +1
        else:
            return 0
    
    def determine_stage(self, affection_level: int) -> str:
        """
        Map affection level to relationship stage.
        
        Args:
            affection_level: Current affection (0-100)
            
        Returns:
            Relationship stage: stranger, friend, close, or attached
        """
        if affection_level <= 20:
            return "stranger"
        elif affection_level <= 50:
            return "friend"
        elif affection_level <= 80:
            return "close"
        else:
            return "attached"
    
    def determine_mood(self, sentiment: SentimentScore, current_mood: str) -> str:
        """
        Update mood based on sentiment and current state.
        
        Args:
            sentiment: Analyzed sentiment score
            current_mood: Current mood state
            
        Returns:
            Updated mood string
        """
        # Compliments make Mimi flustered
        if sentiment.sentiment_type == "compliment":
            return "flustered"
        
        # Vulnerability triggers protective/caring mood
        elif sentiment.sentiment_type == "vulnerability":
            return "sad"  # Empathetic sadness
        
        # Rude messages make her angry
        elif sentiment.sentiment_type == "rude":
            return "angry"
        
        # Positive messages make her happy
        elif sentiment.sentiment_type == "positive":
            return "happy"
        
        # Negative messages make her concerned
        elif sentiment.sentiment_type == "negative":
            return "sad"
        
        # Otherwise maintain current mood or default to neutral
        else:
            return current_mood if current_mood != "flustered" else "neutral"
    
    def update_relationship(
        self,
        user_id: str,
        message: str,
        current_state: UserData
    ) -> RelationshipUpdate:
        """
        Analyze message and update relationship metrics.
        
        This is the main orchestration method that:
        1. Analyzes sentiment
        2. Calculates affection and trust deltas
        3. Determines new stage
        4. Updates mood
        5. Determines attachment state
        6. Returns the update (caller persists to Firestore)
        
        Args:
            user_id: User identifier
            message: User's message
            current_state: Current relationship state
            
        Returns:
            RelationshipUpdate with new affection, trust, mood, stage, attachment_state
        """
        logger.debug(f"Updating relationship for user {user_id}: current_affection={current_state.affection_level}, current_stage={current_state.relationship_stage}")
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(message)
        
        # Calculate deltas
        affection_delta = self.calculate_affection_delta(sentiment)
        trust_delta = self.calculate_trust_delta(sentiment)
        
        # Apply changes (ensure bounds)
        new_affection = max(0, min(100, current_state.affection_level + affection_delta))
        new_trust = max(0, min(100, current_state.trust_level + trust_delta))
        
        # Determine new stage
        new_stage = self.determine_stage(new_affection)
        
        # Update mood
        new_mood = self.determine_mood(sentiment, current_state.mood)
        
        # Determine attachment state based on new affection level
        new_attachment_state = None
        if self.attachment_style_engine:
            new_attachment_state = self.attachment_style_engine.determine_attachment_state(new_affection)
        
        logger.info(f"Relationship updated for user {user_id}: affection={new_affection} (Δ{affection_delta:+d}), trust={new_trust} (Δ{trust_delta:+d}), stage={new_stage}, mood={new_mood}, attachment={new_attachment_state}")
        
        return RelationshipUpdate(
            affection_level=new_affection,
            trust_level=new_trust,
            mood=new_mood,
            relationship_stage=new_stage,
            attachment_state=new_attachment_state
        )
    
    def persist_update(self, user_id: str, update: RelationshipUpdate):
        """
        Save relationship changes to Firestore.
        
        Args:
            user_id: User identifier
            update: RelationshipUpdate to persist
        """
        updates = {
            "affection_level": update.affection_level,
            "trust_level": update.trust_level,
            "mood": update.mood,
            "relationship_stage": update.relationship_stage
        }
        
        # Include attachment_state if present
        if update.attachment_state is not None:
            updates["attachment_state"] = update.attachment_state
        
        update_user_data(self.firestore, user_id, updates)
