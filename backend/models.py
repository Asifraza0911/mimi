"""
Pydantic data models for AI Waifu Cross-Platform System.

This module defines all data models used for API requests/responses,
internal data structures, and Firestore document schemas.
"""

from datetime import datetime, date
from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request model for POST /chat endpoint."""
    
    user_id: str = Field(..., min_length=1, description="Unique user identifier")
    message: str = Field(..., min_length=1, description="User's message text")
    platform: Literal["web", "discord"] = Field(..., description="Source platform")


class ChatResponse(BaseModel):
    """Response model for POST /chat endpoint."""
    
    reply: str = Field(..., description="AI-generated response")
    affection_level: int = Field(..., ge=0, le=100, description="Current affection level (0-100)")
    mood: str = Field(..., description="Current emotional state")


class Message(BaseModel):
    """Individual message in conversation history."""
    
    role: Literal["user", "assistant"] = Field(..., description="Message sender role")
    content: str = Field(..., description="Message text content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class EmotionResult(BaseModel):
    """Result of emotion detection analysis."""
    
    detected_mood: Optional[str] = Field(None, description="Detected emotional state")
    affection_delta: int = Field(0, description="Change in affection level")
    triggers: List[str] = Field(default_factory=list, description="Detected emotional triggers")


class SentimentScore(BaseModel):
    """Sentiment analysis result for a message."""
    
    sentiment_type: Literal["positive", "negative", "neutral", "compliment", "vulnerability", "rude"] = Field(
        ..., description="Classified sentiment type"
    )
    intensity: float = Field(0.5, ge=0.0, le=1.0, description="Sentiment intensity (0.0-1.0)")


class RelationshipUpdate(BaseModel):
    """Result of relationship state update."""
    
    affection_level: int = Field(..., ge=0, le=100, description="Updated affection level")
    trust_level: int = Field(..., ge=0, le=100, description="Updated trust level")
    mood: str = Field(..., description="Updated mood state")
    relationship_stage: Literal["stranger", "friend", "close", "attached"] = Field(
        ..., description="Updated relationship stage"
    )
    attachment_state: Optional[Literal["avoidant", "anxious", "secure", "possessive"]] = Field(
        None, description="Updated attachment style"
    )


class MemoryEntry(BaseModel):
    """Individual memory entry with importance weight."""
    
    text: str = Field(..., description="Memory text content")
    weight: float = Field(..., ge=0.0, le=1.0, description="Importance weight (0.0-1.0)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Memory creation time")


class EmotionalMemoryEntry(BaseModel):
    """Emotional event memory entry."""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    event_type: str = Field(..., description="Type of emotional event")
    trigger: str = Field(..., description="Original message or keyword that triggered the event")
    mood_change: str = Field(..., description="Resulting mood state")
    affection_delta: int = Field(..., description="Change in affection level")


class UserData(BaseModel):
    """Complete user relationship state stored in Firestore."""
    
    user_id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = Field(None, description="User's preferred name")
    affection_level: int = Field(10, ge=0, le=100, description="Relationship affection (0-100)")
    trust_level: int = Field(5, ge=0, le=100, description="Emotional trust (0-100)")
    mood: str = Field("neutral", description="Current emotional state")
    relationship_stage: Literal["stranger", "friend", "close", "attached"] = Field(
        "stranger", description="Current relationship stage"
    )
    attachment_state: Literal["avoidant", "anxious", "secure", "possessive"] = Field(
        "avoidant", description="Current attachment style"
    )
    long_term_memory: List[MemoryEntry] = Field(
        default_factory=list, description="Important memories with weights"
    )
    emotional_memory: List[EmotionalMemoryEntry] = Field(
        default_factory=list, description="Emotional events history"
    )
    last_interaction: datetime = Field(
        default_factory=datetime.now, description="Last message timestamp"
    )
    last_chat_date: Optional[datetime] = Field(
        default=None, description="Date of last chat for streak tracking (datetime for Firestore compatibility)"
    )
    daily_interaction_streak: int = Field(
        1, ge=0, description="Consecutive days of interaction"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Account creation timestamp"
    )
    platform_stats: Dict[str, int] = Field(
        default_factory=lambda: {"web": 0, "discord": 0},
        description="Platform usage statistics"
    )
    
    @field_validator('affection_level', 'trust_level')
    @classmethod
    def validate_level_range(cls, v: int) -> int:
        """Ensure levels stay within 0-100 range."""
        return max(0, min(100, v))


class DecayResult(BaseModel):
    """Result of affection decay calculation."""
    
    hours_passed: int = Field(..., ge=0, description="Hours since last interaction")
    affection_delta: int = Field(..., description="Affection points decayed (negative)")
    new_mood: Optional[str] = Field(None, description="Updated mood if changed")


class StreakResult(BaseModel):
    """Result of interaction streak update."""
    
    new_streak: int = Field(..., ge=0, description="Updated streak count")
    was_broken: bool = Field(..., description="Whether streak was broken")
    affection_delta: int = Field(0, description="Affection penalty if streak broken")
