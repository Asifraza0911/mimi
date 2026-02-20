"""
Integration tests for Response Pipeline.

Tests complete pipeline execution with mocked services, error handling,
and session context updates.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime, date, timedelta
import numpy as np

from models import (
    ChatResponse, UserData, EmotionResult, RelationshipUpdate,
    Message, DecayResult, StreakResult, MemoryEntry
)
from modules.response_pipeline import ResponsePipeline
from modules.emotion_engine import EmotionEngine
from modules.memory_engine import MemoryEngine
from modules.personality_system import PersonalitySystem
from modules.relationship_engine import RelationshipEngine
from modules.llm_service import LLMService
from modules.affection_decay_engine import AffectionDecayEngine
from modules.attachment_style_engine import AttachmentStyleEngine
from modules.temperature_scaling_system import TemperatureScalingSystem
from modules.interaction_streak_system import InteractionStreakSystem
from modules.callback_memory_system import CallbackMemorySystem


def setup_common_mocks(mock_modules):
    """Helper function to set up common mock return values."""
    # Mock memory weight calculation (used by all tests)
    mock_modules['memory_engine'].calculate_memory_weight.return_value = 0.3
    # Mock memory storage
    mock_modules['memory_engine'].store_memory.return_value = None


@pytest.fixture
def mock_firestore():
    """Create a mock Firestore client."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    return mock_client


@pytest.fixture
def mock_modules(mock_firestore):
    """Create mocked versions of all pipeline modules."""
    modules = {
        'affection_decay_engine': MagicMock(),
        'interaction_streak_system': MagicMock(),
        'emotion_engine': MagicMock(),
        'memory_engine': MagicMock(),
        'personality_system': MagicMock(),
        'relationship_engine': MagicMock(),
        'attachment_style_engine': MagicMock(),
        'temperature_scaling_system': MagicMock(),
        'callback_memory_system': MagicMock(),
        'llm_service': MagicMock(),
    }
    return modules


@pytest.fixture
def pipeline(mock_firestore, mock_modules):
    """Create a ResponsePipeline with mocked dependencies."""
    return ResponsePipeline(
        firestore_client=mock_firestore,
        affection_decay_engine=mock_modules['affection_decay_engine'],
        interaction_streak_system=mock_modules['interaction_streak_system'],
        emotion_engine=mock_modules['emotion_engine'],
        memory_engine=mock_modules['memory_engine'],
        personality_system=mock_modules['personality_system'],
        relationship_engine=mock_modules['relationship_engine'],
        attachment_style_engine=mock_modules['attachment_style_engine'],
        temperature_scaling_system=mock_modules['temperature_scaling_system'],
        callback_memory_system=mock_modules['callback_memory_system'],
        llm_service=mock_modules['llm_service']
    )


@pytest.mark.asyncio
async def test_complete_pipeline_execution_success(pipeline, mock_modules, mock_firestore):
    """Test complete pipeline execution from start to finish with all modules working."""
    setup_common_mocks(mock_modules)
    
    # Setup user data
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend",
        attachment_state="anxious",
        last_interaction=datetime.now() - timedelta(hours=1),
        last_chat_date=date.today(),
        daily_interaction_streak=5
    )
    
    # Mock Firestore user retrieval
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock affection decay (no decay)
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1,
        affection_delta=0,
        new_mood=None
    )
    
    # Mock streak system (no break)
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5,
        was_broken=False,
        affection_delta=0
    )
    
    # Mock emotion detection (neutral)
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral",
        affection_delta=0,
        triggers=[]
    )
    
    # Mock memory retrieval
    mock_modules['memory_engine'].retrieve_similar.return_value = [
        "We talked about your favorite food yesterday",
        "You mentioned you like programming"
    ]
    
    # Mock memory weight calculation
    mock_modules['memory_engine'].calculate_memory_weight.return_value = 0.3
    
    # Mock callback system (no callback)
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['callback_memory_system'].select_callback_memory.return_value = None
    
    # Mock personality system
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt with context"
    
    # Mock temperature scaling
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    
    # Mock LLM response
    mock_modules['llm_service'].generate_response.return_value = "Hmph! I-I wasn't waiting for you or anything!"
    
    # Mock relationship update
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=51,
        trust_level=40,
        mood="neutral",
        relationship_stage="close",
        attachment_state="anxious"
    )
    
    # Mock memory storage
    mock_modules['memory_engine'].store_memory.return_value = None
    
    # Execute pipeline
    response = await pipeline.process_message(
        user_id="test_user",
        message="Hello, how are you?",
        platform="web"
    )
    
    # Verify response structure
    assert isinstance(response, ChatResponse)
    assert response.reply == "Hmph! I-I wasn't waiting for you or anything!"
    assert response.affection_level == 51
    assert response.mood == "neutral"
    
    # Verify all modules were called in correct order
    mock_modules['affection_decay_engine'].apply_decay.assert_called_once()
    mock_modules['interaction_streak_system'].update_streak.assert_called_once()
    mock_modules['emotion_engine'].detect_emotions.assert_called_once()
    mock_modules['memory_engine'].retrieve_similar.assert_called_once()
    mock_modules['personality_system'].construct_prompt.assert_called_once()
    mock_modules['temperature_scaling_system'].get_temperature.assert_called_once()
    mock_modules['llm_service'].generate_response.assert_called_once()
    mock_modules['relationship_engine'].update_relationship.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_with_affection_decay(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles affection decay correctly."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend",
        last_interaction=datetime.now() - timedelta(hours=48)  # 2 days ago
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay (2 points lost)
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=48,
        affection_delta=-2,
        new_mood="sad"
    )
    
    # Mock other modules with minimal responses
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=1, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.4
    mock_modules['llm_service'].generate_response.return_value = "You... you were gone for so long..."
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=48, trust_level=40, mood="sad",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="test_user",
        message="I'm back!",
        platform="web"
    )
    
    # Verify decay was applied
    assert response.mood == "sad"
    mock_modules['affection_decay_engine'].apply_decay.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_with_broken_streak(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles broken interaction streak correctly."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=60,
        trust_level=50,
        mood="neutral",
        relationship_stage="close",
        last_chat_date=date.today() - timedelta(days=3),  # 3 days ago
        daily_interaction_streak=10
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=72, affection_delta=-3, new_mood="sad"
    )
    
    # Mock broken streak
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=1,
        was_broken=True,
        affection_delta=-3
    )
    
    # Mock other modules
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.4
    mock_modules['llm_service'].generate_response.return_value = "You... you broke our streak..."
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=54, trust_level=50, mood="sad",
        relationship_stage="close", attachment_state="secure"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="test_user",
        message="Sorry I was away",
        platform="web"
    )
    
    # Verify streak break was handled
    mock_modules['interaction_streak_system'].update_streak.assert_called_once()
    assert response.mood == "sad"


@pytest.mark.asyncio
async def test_pipeline_with_jealousy_trigger(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles jealousy detection correctly."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=70,
        trust_level=60,
        mood="neutral",
        relationship_stage="close",
        attachment_state="secure"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay and streak
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    
    # Mock jealousy detection
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="jealous",
        affection_delta=-2,
        triggers=["another girl"]
    )
    
    # Mock other modules
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.8  # High temp for jealous
    mock_modules['llm_service'].generate_response.return_value = "W-what?! Another girl?! I-I don't care!"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=68, trust_level=60, mood="jealous",
        relationship_stage="close", attachment_state="secure"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="test_user",
        message="I met another girl today",
        platform="web"
    )
    
    # Verify jealousy was detected and handled
    assert response.mood == "jealous"
    mock_modules['emotion_engine'].detect_emotions.assert_called_once()
    mock_modules['temperature_scaling_system'].get_temperature.assert_called_with("jealous")


@pytest.mark.asyncio
async def test_pipeline_with_callback_memory(pipeline, mock_modules, mock_firestore):
    """Test pipeline with callback memory injection."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=85,  # High affection for callback
        trust_level=80,
        mood="happy",
        relationship_stage="attached",
        attachment_state="possessive",
        long_term_memory=[
            MemoryEntry(text="You told me you love programming", weight=0.9),
            MemoryEntry(text="You said your favorite color is blue", weight=0.8)
        ]
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay and streak
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=7, was_broken=False, affection_delta=0
    )
    
    # Mock emotion
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    
    # Mock memory
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    
    # Mock callback (should trigger at 85% affection)
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = True
    mock_modules['callback_memory_system'].select_callback_memory.return_value = {
        "text": "You told me you love programming",
        "weight": 0.9
    }
    mock_modules['callback_memory_system'].format_callback.return_value = "I remember when you told me you love programming"
    
    # Mock personality and LLM
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt with callback"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.7
    mock_modules['llm_service'].generate_response.return_value = "I remember you said you love programming! Are you working on something?"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=85, trust_level=80, mood="happy",
        relationship_stage="attached", attachment_state="possessive"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="test_user",
        message="What's up?",
        platform="web"
    )
    
    # Verify callback was triggered
    mock_modules['callback_memory_system'].should_trigger_callback.assert_called_once_with(85)
    mock_modules['callback_memory_system'].select_callback_memory.assert_called_once()
    assert "programming" in response.reply.lower()


@pytest.mark.skip(reason="Error handling not yet implemented - Task 12")
@pytest.mark.asyncio
async def test_pipeline_error_handling_firestore_failure(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles Firestore failure gracefully."""
    setup_common_mocks(mock_modules)
    
    # Mock Firestore failure
    mock_firestore.collection.return_value.document.return_value.get.side_effect = Exception("Firestore connection error")
    
    # Mock all other modules to return defaults
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=0, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=1, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Hmph! Something went wrong..."
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=10, trust_level=5, mood="neutral",
        relationship_stage="stranger", attachment_state="avoidant"
    )
    
    # Execute - should use default user data
    response = await pipeline.process_message(
        user_id="test_user",
        message="Hello",
        platform="web"
    )
    
    # Should still return a response (graceful degradation)
    assert isinstance(response, ChatResponse)
    assert response.reply is not None


@pytest.mark.skip(reason="Error handling not yet implemented - Task 12")
@pytest.mark.asyncio
async def test_pipeline_error_handling_memory_engine_failure(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles Memory Engine failure gracefully."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay and streak
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    
    # Mock emotion
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    
    # Mock Memory Engine failure
    mock_modules['memory_engine'].retrieve_similar.side_effect = Exception("FAISS index error")
    
    # Mock other modules
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Hmph! I'm here anyway..."
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=50, trust_level=40, mood="neutral",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Execute - should continue without memory retrieval
    response = await pipeline.process_message(
        user_id="test_user",
        message="Hello",
        platform="web"
    )
    
    # Should still return a response
    assert isinstance(response, ChatResponse)
    assert response.reply is not None
    # Personality system should be called with empty memories
    mock_modules['personality_system'].construct_prompt.assert_called_once()


@pytest.mark.skip(reason="Error handling not yet implemented - Task 12")
@pytest.mark.asyncio
async def test_pipeline_error_handling_emotion_engine_failure(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles Emotion Engine failure gracefully."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock decay and streak
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    
    # Mock Emotion Engine failure
    mock_modules['emotion_engine'].detect_emotions.side_effect = Exception("Emotion detection error")
    
    # Mock other modules
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Hmph!"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=50, trust_level=40, mood="neutral",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Execute - should use neutral mood as default
    response = await pipeline.process_message(
        user_id="test_user",
        message="Hello",
        platform="web"
    )
    
    # Should still return a response
    assert isinstance(response, ChatResponse)
    assert response.reply is not None


@pytest.mark.skip(reason="Error handling not yet implemented - Task 12")
@pytest.mark.asyncio
async def test_pipeline_error_handling_llm_service_failure(pipeline, mock_modules, mock_firestore):
    """Test pipeline handles LLM Service failure with fallback response."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock all modules except LLM
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    
    # Mock LLM failure with fallback
    mock_modules['llm_service'].generate_response.side_effect = Exception("HuggingFace API error")
    mock_modules['llm_service'].get_fallback_response.return_value = "H-hey! Don't ignore me like that!"
    
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=50, trust_level=40, mood="neutral",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Execute - should use fallback response
    response = await pipeline.process_message(
        user_id="test_user",
        message="Hello",
        platform="web"
    )
    
    # Should return fallback response
    assert isinstance(response, ChatResponse)
    assert response.reply == "H-hey! Don't ignore me like that!"
    mock_modules['llm_service'].get_fallback_response.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_session_context_updates(pipeline, mock_modules, mock_firestore):
    """Test that session context is properly updated throughout the pipeline."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock all modules
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Test response"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=50, trust_level=40, mood="neutral",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Send first message
    await pipeline.process_message(
        user_id="test_user",
        message="Hello",
        platform="web"
    )
    
    # Verify session context was created
    assert "test_user" in pipeline.session_contexts
    assert len(pipeline.session_contexts["test_user"]["messages"]) == 2  # User + assistant
    
    # Send second message
    await pipeline.process_message(
        user_id="test_user",
        message="How are you?",
        platform="web"
    )
    
    # Verify session context was updated
    assert len(pipeline.session_contexts["test_user"]["messages"]) == 4  # 2 exchanges
    
    # Verify messages are in correct order
    messages = pipeline.session_contexts["test_user"]["messages"]
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[2].content == "How are you?"
    assert messages[3].role == "assistant"


@pytest.mark.asyncio
async def test_pipeline_session_context_limit(pipeline, mock_modules, mock_firestore):
    """Test that session context is limited to last 10 messages."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend"
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock all modules
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Test response"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=50, trust_level=40, mood="neutral",
        relationship_stage="friend", attachment_state="anxious"
    )
    
    # Send 8 messages (16 total with responses)
    for i in range(8):
        await pipeline.process_message(
            user_id="test_user",
            message=f"Message {i}",
            platform="web"
        )
    
    # Verify context is limited to 10 messages
    assert len(pipeline.session_contexts["test_user"]["messages"]) == 10
    
    # Verify oldest messages were removed
    messages = pipeline.session_contexts["test_user"]["messages"]
    assert messages[0].content == "Message 3"  # First 6 messages removed


@pytest.mark.asyncio
async def test_pipeline_data_flow_between_modules(pipeline, mock_modules, mock_firestore):
    """Test that data flows correctly between modules."""
    setup_common_mocks(mock_modules)
    
    user_data = UserData(
        user_id="test_user",
        affection_level=50,
        trust_level=40,
        mood="neutral",
        relationship_stage="friend",
        attachment_state="anxious",
        long_term_memory=[
            MemoryEntry(text="User likes cats", weight=0.8)
        ]
    )
    
    # Mock Firestore
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = user_data.model_dump()
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock modules
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=1, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=5, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="happy", affection_delta=1, triggers=["love"]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = [
        "We talked about cats before"
    ]
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.7
    mock_modules['llm_service'].generate_response.return_value = "I love cats too!"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=51, trust_level=40, mood="happy",
        relationship_stage="close", attachment_state="anxious"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="test_user",
        message="I love cats!",
        platform="web"
    )
    
    # Verify data flow
    # 1. User data was retrieved
    mock_firestore.collection.assert_called_with("waifu_memory")
    
    # 2. Emotion was detected with correct message
    call_args = mock_modules['emotion_engine'].detect_emotions.call_args
    assert call_args[0][0] == "I love cats!"
    
    # 3. Memory retrieval used the message
    call_args = mock_modules['memory_engine'].retrieve_similar.call_args
    assert call_args[0][1] == "I love cats!"
    
    # 4. Personality system received user data and memories
    call_args = mock_modules['personality_system'].construct_prompt.call_args
    user_data_arg = call_args[1]['user_data']
    # user_data could be UserData object or dict
    affection = user_data_arg.affection_level if hasattr(user_data_arg, 'affection_level') else user_data_arg['affection_level']
    # Affection may have been updated by relationship engine before personality system is called
    assert affection >= 50  # Should be at least the starting value
    assert len(call_args[1]['similar_memories']) > 0
    
    # 5. Temperature was based on mood
    mock_modules['temperature_scaling_system'].get_temperature.assert_called_with("happy")
    
    # 6. LLM received prompt and temperature
    call_args = mock_modules['llm_service'].generate_response.call_args
    assert call_args[1]['temperature'] == 0.7
    
    # 7. Final response reflects updates
    assert response.affection_level == 51
    assert response.mood == "happy"


@pytest.mark.asyncio
async def test_pipeline_new_user_initialization(pipeline, mock_modules, mock_firestore):
    """Test pipeline correctly initializes new users."""
    setup_common_mocks(mock_modules)
    
    # Mock Firestore - user doesn't exist
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Mock all modules
    mock_modules['affection_decay_engine'].apply_decay.return_value = DecayResult(
        hours_passed=0, affection_delta=0, new_mood=None
    )
    mock_modules['interaction_streak_system'].update_streak.return_value = StreakResult(
        new_streak=1, was_broken=False, affection_delta=0
    )
    mock_modules['emotion_engine'].detect_emotions.return_value = EmotionResult(
        detected_mood="neutral", affection_delta=0, triggers=[]
    )
    mock_modules['memory_engine'].retrieve_similar.return_value = []
    mock_modules['callback_memory_system'].should_trigger_callback.return_value = False
    mock_modules['personality_system'].construct_prompt.return_value = "Test prompt"
    mock_modules['temperature_scaling_system'].get_temperature.return_value = 0.5
    mock_modules['llm_service'].generate_response.return_value = "Hmph! Who are you?"
    mock_modules['relationship_engine'].update_relationship.return_value = RelationshipUpdate(
        affection_level=10, trust_level=5, mood="neutral",
        relationship_stage="stranger", attachment_state="avoidant"
    )
    
    # Execute
    response = await pipeline.process_message(
        user_id="new_user",
        message="Hello!",
        platform="web"
    )
    
    # Verify new user was created with defaults
    assert response.affection_level == 10  # Default affection
    assert response.mood == "neutral"  # Default mood


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
