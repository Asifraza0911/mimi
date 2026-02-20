"""
Property-Based Tests for Emotion Detection

This module contains property-based tests for the EmotionEngine module,
validating jealousy detection, emotional keyword detection, and emotional
memory recording.

**Validates: Requirements 5.1.2, 5.1.3, 5.1.4, 5.1.6, 5.1.8, 5.1.9, 8.1, 8.5**
"""

from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis.strategies import composite
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from models import EmotionResult, UserData, EmotionalMemoryEntry
from modules.emotion_engine import EmotionEngine


# Strategy for generating user IDs
def user_id_strategy():
    return st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )
    )


# Strategy for generating messages with jealousy keywords
@composite
def message_with_jealousy_keyword(draw):
    """Generate messages containing jealousy keywords."""
    jealousy_keywords = [
        "she", "her", "another girl", "my girlfriend", 
        "my crush", "i like her", "she's cute",
        "talking to someone else", "other girl", "new girl"
    ]
    
    keyword = draw(st.sampled_from(jealousy_keywords))
    
    # Generate message with the keyword embedded
    prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), max_size=50))
    suffix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), max_size=50))
    
    # Construct message with keyword
    message = f"{prefix} {keyword} {suffix}".strip()
    
    return message, keyword


# Strategy for generating messages with emotional keywords
@composite
def message_with_emotion_keyword(draw):
    """Generate messages containing emotional keywords."""
    emotion_keywords = {
        "happy": ["happy", "excited", "great", "awesome", "love"],
        "sad": ["sad", "depressed", "down", "upset", "hurt"],
        "angry": ["angry", "mad", "furious", "annoyed"],
        "vulnerable": ["scared", "worried", "anxious", "nervous"]
    }
    
    mood = draw(st.sampled_from(list(emotion_keywords.keys())))
    keyword = draw(st.sampled_from(emotion_keywords[mood]))
    
    # Generate message with the keyword embedded
    prefix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), max_size=50))
    suffix = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), max_size=50))
    
    # Construct message with keyword
    message = f"{prefix} {keyword} {suffix}".strip()
    
    return message, mood, keyword


# Strategy for generating messages without emotional keywords
def neutral_message_strategy():
    """Generate messages without emotional or jealousy keywords."""
    # Use safe words that don't trigger emotions
    safe_words = ["hello", "hi", "okay", "yes", "no", "maybe", "thanks", "bye"]
    return st.lists(st.sampled_from(safe_words), min_size=1, max_size=5).map(lambda words: " ".join(words))


@pytest.fixture
def mock_firestore():
    """Create a mock Firestore client."""
    return Mock()


@pytest.fixture
def emotion_engine(mock_firestore):
    """Create an EmotionEngine instance with mocked Firestore."""
    return EmotionEngine(mock_firestore)


class TestJealousyDetection:
    """
    **Property 19: Jealousy Detection and Response**
    
    Tests that jealousy keywords trigger jealous mood and -2 affection delta.
    
    **Validates: Requirements 5.1.2, 5.1.3, 5.1.4, 5.1.6**
    """
    
    @given(
        message_data=message_with_jealousy_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_jealousy_keyword_triggers_jealous_mood(self, emotion_engine, message_data, user_id):
        """
        Test that messages containing jealousy keywords trigger jealous mood.
        
        **Property**: For all messages containing jealousy keywords,
        detect_emotions() returns detected_mood="jealous"
        """
        message, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify jealous mood is detected
        assert result.detected_mood == "jealous", \
            f"Expected jealous mood for message with keyword '{keyword}', got {result.detected_mood}"
    
    @given(
        message_data=message_with_jealousy_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_jealousy_keyword_triggers_affection_decrease(self, emotion_engine, message_data, user_id):
        """
        Test that jealousy keywords trigger -2 affection delta.
        
        **Property**: For all messages containing jealousy keywords,
        detect_emotions() returns affection_delta=-2
        """
        message, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify affection delta is -2
        assert result.affection_delta == -2, \
            f"Expected affection_delta=-2 for jealousy keyword '{keyword}', got {result.affection_delta}"
    
    @given(
        message_data=message_with_jealousy_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_jealousy_keyword_captured_in_triggers(self, emotion_engine, message_data, user_id):
        """
        Test that detected jealousy keywords are captured in triggers list.
        
        **Property**: For all messages containing jealousy keywords,
        detect_emotions() returns triggers list containing the keyword
        """
        message, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify keyword is in triggers
        assert len(result.triggers) > 0, \
            f"Expected triggers list to contain keyword '{keyword}', got empty list"
        assert keyword in result.triggers, \
            f"Expected keyword '{keyword}' in triggers {result.triggers}"
    
    @given(
        message_data=message_with_jealousy_keyword()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_check_jealousy_returns_true_for_jealousy_keywords(self, emotion_engine, message_data):
        """
        Test that check_jealousy() returns True for messages with jealousy keywords.
        
        **Property**: For all messages containing jealousy keywords,
        check_jealousy() returns True
        """
        message, keyword = message_data
        
        # Execute jealousy check
        result = emotion_engine.check_jealousy(message)
        
        # Verify jealousy is detected
        assert result is True, \
            f"Expected check_jealousy() to return True for message with keyword '{keyword}'"


class TestEmotionalKeywordDetection:
    """
    **Property 20: Emotional Keyword Detection and Mood Update**
    
    Tests that emotional keywords update mood appropriately.
    
    **Validates: Requirements 5.1.8, 5.1.9, 8.1**
    """
    
    @given(
        message_data=message_with_emotion_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_emotional_keyword_triggers_correct_mood(self, emotion_engine, message_data, user_id):
        """
        Test that emotional keywords trigger the correct mood.
        
        **Property**: For all messages containing emotional keywords,
        detect_emotions() returns the corresponding mood
        """
        message, expected_mood, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify correct mood is detected
        assert result.detected_mood == expected_mood, \
            f"Expected mood '{expected_mood}' for keyword '{keyword}', got {result.detected_mood}"
    
    @given(
        message_data=message_with_emotion_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_emotional_keyword_captured_in_triggers(self, emotion_engine, message_data, user_id):
        """
        Test that detected emotional keywords are captured in triggers list.
        
        **Property**: For all messages containing emotional keywords,
        detect_emotions() returns triggers list containing the keyword
        """
        message, expected_mood, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify keyword is in triggers
        assert len(result.triggers) > 0, \
            f"Expected triggers list to contain keyword '{keyword}', got empty list"
        assert keyword in result.triggers, \
            f"Expected keyword '{keyword}' in triggers {result.triggers}"
    
    @given(
        message_data=message_with_emotion_keyword(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_emotional_keyword_no_affection_delta(self, emotion_engine, message_data, user_id):
        """
        Test that non-jealousy emotional keywords don't change affection.
        
        **Property**: For all messages containing non-jealousy emotional keywords,
        detect_emotions() returns affection_delta=0
        """
        message, expected_mood, keyword = message_data
        
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify no affection change for non-jealousy emotions
        assert result.affection_delta == 0, \
            f"Expected affection_delta=0 for non-jealousy emotion '{expected_mood}', got {result.affection_delta}"
    
    @given(
        message=neutral_message_strategy(),
        user_id=user_id_strategy()
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.property_test
    def test_neutral_message_returns_neutral_mood(self, emotion_engine, message, user_id):
        """
        Test that messages without emotional keywords return neutral mood.
        
        **Property**: For all messages without emotional keywords,
        detect_emotions() returns detected_mood=None and affection_delta=0
        """
        # Execute emotion detection
        result = emotion_engine.detect_emotions(message, user_id)
        
        # Verify neutral result
        assert result.detected_mood is None, \
            f"Expected None mood for neutral message, got {result.detected_mood}"
        assert result.affection_delta == 0, \
            f"Expected affection_delta=0 for neutral message, got {result.affection_delta}"
        assert result.triggers == [], \
            f"Expected empty triggers for neutral message, got {result.triggers}"


class TestEmotionalMemoryRecording:
    """
    **Property 22: Emotional Memory Recording**
    
    Tests that emotional events are stored in emotional_memory.
    
    **Validates: Requirements 5.1.6, 8.5**
    """
    
    @given(
        user_id=user_id_strategy(),
        mood=st.sampled_from(["jealous", "happy", "sad", "angry", "vulnerable"]),
        affection_delta=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.property_test
    def test_update_mood_stores_emotional_memory(
        self, 
        user_id, 
        mood, 
        affection_delta
    ):
        """
        Test that update_mood() stores emotional events in emotional_memory.
        
        **Property**: For all mood updates, update_mood() creates an
        EmotionalMemoryEntry and stores it in Firestore
        """
        # Create emotion engine with mock firestore
        mock_firestore = Mock()
        emotion_engine = EmotionEngine(mock_firestore)
        
        # Create mock user data
        mock_user_data = UserData(
            user_id=user_id,
            affection_level=50,
            trust_level=50,
            mood="neutral",
            relationship_stage="friend",
            attachment_state="anxious",
            long_term_memory=[],
            emotional_memory=[],
            last_interaction=datetime.now(),
            last_chat_date=None,
            daily_interaction_streak=1,
            created_at=datetime.now(),
            platform_stats={"web": 0, "discord": 0}
        )
        
        # Mock the firestore_operations module
        with patch('modules.firestore_operations.get_user_data', return_value=mock_user_data) as mock_get, \
             patch('modules.firestore_operations.update_user_data') as mock_update:
            
            # Execute mood update
            emotion_engine.update_mood(user_id, mood, affection_delta)
            
            # Verify update_user_data was called
            assert mock_update.called, \
                "Expected update_user_data to be called"
            
            # Get the updates dictionary passed to update_user_data
            call_args = mock_update.call_args[0]
            updates = call_args[2]  # Third argument is the updates dict
            
            # Verify emotional_memory was updated
            assert "emotional_memory" in updates, \
                "Expected emotional_memory in updates"
            
            emotional_memory = updates["emotional_memory"]
            assert len(emotional_memory) > 0, \
                "Expected at least one emotional memory entry"
            
            # Verify the emotional memory entry has correct structure
            latest_entry = emotional_memory[-1]
            assert isinstance(latest_entry, EmotionalMemoryEntry), \
                f"Expected EmotionalMemoryEntry, got {type(latest_entry)}"
            assert latest_entry.event_type == mood, \
                f"Expected event_type={mood}, got {latest_entry.event_type}"
            assert latest_entry.mood_change == mood, \
                f"Expected mood_change={mood}, got {latest_entry.mood_change}"
            assert latest_entry.affection_delta == affection_delta, \
                f"Expected affection_delta={affection_delta}, got {latest_entry.affection_delta}"
    
    @given(
        user_id=user_id_strategy(),
        mood=st.sampled_from(["jealous", "happy", "sad", "angry"]),
        affection_delta=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.property_test
    def test_update_mood_updates_mood_field(
        self, 
        user_id, 
        mood, 
        affection_delta
    ):
        """
        Test that update_mood() updates the mood field in Firestore.
        
        **Property**: For all mood updates, update_mood() persists
        the new mood to Firestore
        """
        # Create emotion engine with mock firestore
        mock_firestore = Mock()
        emotion_engine = EmotionEngine(mock_firestore)
        
        # Create mock user data
        mock_user_data = UserData(
            user_id=user_id,
            affection_level=50,
            trust_level=50,
            mood="neutral",
            relationship_stage="friend",
            attachment_state="anxious",
            long_term_memory=[],
            emotional_memory=[],
            last_interaction=datetime.now(),
            last_chat_date=None,
            daily_interaction_streak=1,
            created_at=datetime.now(),
            platform_stats={"web": 0, "discord": 0}
        )
        
        # Mock the firestore_operations module
        with patch('modules.firestore_operations.get_user_data', return_value=mock_user_data) as mock_get, \
             patch('modules.firestore_operations.update_user_data') as mock_update:
            
            # Execute mood update
            emotion_engine.update_mood(user_id, mood, affection_delta)
            
            # Verify update_user_data was called
            assert mock_update.called, \
                "Expected update_user_data to be called"
            
            # Get the updates dictionary
            call_args = mock_update.call_args[0]
            updates = call_args[2]
            
            # Verify mood was updated
            assert "mood" in updates, \
                "Expected mood in updates"
            assert updates["mood"] == mood, \
                f"Expected mood={mood}, got {updates['mood']}"
    
    @given(
        user_id=user_id_strategy(),
        mood=st.sampled_from(["jealous", "happy", "sad"]),
        initial_affection=st.integers(min_value=10, max_value=90),
        affection_delta=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.property_test
    def test_update_mood_applies_affection_delta(
        self, 
        user_id, 
        mood, 
        initial_affection,
        affection_delta
    ):
        """
        Test that update_mood() correctly applies affection delta.
        
        **Property**: For all mood updates, update_mood() calculates
        new_affection = current_affection + affection_delta (clamped to 0-100)
        """
        # Create emotion engine with mock firestore
        mock_firestore = Mock()
        emotion_engine = EmotionEngine(mock_firestore)
        
        # Create mock user data
        mock_user_data = UserData(
            user_id=user_id,
            affection_level=initial_affection,
            trust_level=50,
            mood="neutral",
            relationship_stage="friend",
            attachment_state="anxious",
            long_term_memory=[],
            emotional_memory=[],
            last_interaction=datetime.now(),
            last_chat_date=None,
            daily_interaction_streak=1,
            created_at=datetime.now(),
            platform_stats={"web": 0, "discord": 0}
        )
        
        # Mock the firestore_operations module
        with patch('modules.firestore_operations.get_user_data', return_value=mock_user_data) as mock_get, \
             patch('modules.firestore_operations.update_user_data') as mock_update:
            
            # Execute mood update
            emotion_engine.update_mood(user_id, mood, affection_delta)
            
            # Calculate expected affection (clamped to 0-100)
            expected_affection = max(0, min(100, initial_affection + affection_delta))
            
            # Verify update_user_data was called
            assert mock_update.called, \
                "Expected update_user_data to be called"
            
            # Get the updates dictionary
            call_args = mock_update.call_args[0]
            updates = call_args[2]
            
            # Verify affection_level was updated correctly
            assert "affection_level" in updates, \
                "Expected affection_level in updates"
            assert updates["affection_level"] == expected_affection, \
                f"Expected affection_level={expected_affection}, got {updates['affection_level']}"
