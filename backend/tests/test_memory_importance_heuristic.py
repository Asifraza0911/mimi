"""
Unit tests for memory importance heuristic in Response Pipeline.

Tests the is_important_memory method that determines whether a message
should be stored and assigns importance weights.

Requirements: 8.2, 8.3, 8.4, 17.2
"""

import pytest
from unittest.mock import Mock, MagicMock
from models import EmotionResult
from modules.response_pipeline import ResponsePipeline


class TestMemoryImportanceHeuristic:
    """Test suite for is_important_memory method."""
    
    @pytest.fixture
    def mock_memory_engine(self):
        """Create a mock memory engine."""
        engine = Mock()
        engine.calculate_memory_weight = Mock(return_value=0.5)
        return engine
    
    @pytest.fixture
    def response_pipeline(self, mock_memory_engine):
        """Create a ResponsePipeline instance with mocked dependencies."""
        pipeline = ResponsePipeline(
            firestore_client=Mock(),
            affection_decay_engine=Mock(),
            interaction_streak_system=Mock(),
            emotion_engine=Mock(),
            memory_engine=mock_memory_engine,
            personality_system=Mock(),
            relationship_engine=Mock(),
            attachment_style_engine=Mock(),
            temperature_scaling_system=Mock(),
            callback_memory_system=Mock(),
            llm_service=Mock()
        )
        return pipeline
    
    def test_emotional_content_is_important(self, response_pipeline, mock_memory_engine):
        """Test that messages with emotional content are marked as important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.9
        emotion_result = EmotionResult(
            detected_mood="sad",
            affection_delta=0,
            triggers=["sad"]
        )
        message = "I'm feeling really sad today"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is True
        assert weight == 0.9
        mock_memory_engine.calculate_memory_weight.assert_called_once()
    
    def test_personal_information_is_important(self, response_pipeline, mock_memory_engine):
        """Test that messages with personal information are marked as important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.5
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        message = "My favorite color is blue and I love pizza"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is True
        assert weight == 0.5
    
    def test_long_message_is_important(self, response_pipeline, mock_memory_engine):
        """Test that long messages (>20 words) are marked as important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.5
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        # Create a message with more than 20 words
        message = "Today I went to the park and saw many beautiful flowers blooming in the spring sunshine and it made me think about how wonderful nature is"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is True
        assert len(message.split()) > 20
    
    def test_high_weight_is_important(self, response_pipeline, mock_memory_engine):
        """Test that messages with weight >= 0.5 are marked as important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.7
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        message = "Just a regular message"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is True
        assert weight == 0.7
    
    def test_casual_greeting_not_important(self, response_pipeline, mock_memory_engine):
        """Test that casual greetings with low weight are not marked as important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.1
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        message = "hi"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is False
        assert weight == 0.1
    
    def test_neutral_short_message_not_important(self, response_pipeline, mock_memory_engine):
        """Test that neutral short messages with low weight are not important."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.3
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        message = "okay"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert is_important is False
        assert weight == 0.3
    
    def test_calls_memory_engine_calculate_weight(self, response_pipeline, mock_memory_engine):
        """Test that is_important_memory calls Memory Engine's calculate_memory_weight."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.6
        emotion_result = EmotionResult(
            detected_mood="happy",
            affection_delta=1,
            triggers=["happy"]
        )
        message = "I'm so happy today!"
        
        # Execute
        is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        mock_memory_engine.calculate_memory_weight.assert_called_once()
        call_args = mock_memory_engine.calculate_memory_weight.call_args
        assert call_args[0][0] == message
        assert call_args[0][1]["detected_mood"] == "happy"
        assert call_args[0][1]["affection_delta"] == 1
        assert call_args[0][1]["triggers"] == ["happy"]
    
    def test_returns_tuple_format(self, response_pipeline, mock_memory_engine):
        """Test that is_important_memory returns a tuple of (bool, float)."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.5
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        message = "test message"
        
        # Execute
        result = response_pipeline.is_important_memory(message, emotion_result)
        
        # Verify
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], float)
    
    def test_personal_keywords_detection(self, response_pipeline, mock_memory_engine):
        """Test various personal information keywords are detected."""
        # Setup
        mock_memory_engine.calculate_memory_weight.return_value = 0.4
        emotion_result = EmotionResult(
            detected_mood="neutral",
            affection_delta=0,
            triggers=[]
        )
        
        personal_messages = [
            "My name is John",
            "I am a software engineer",
            "I'm studying computer science",
            "I like reading books",
            "I love playing guitar",
            "I hate spicy food",
            "My favorite movie is Inception",
            "I work at a tech company",
            "I study at university",
            "I prefer tea over coffee",
            "I enjoy hiking",
            "I feel excited about this",
            "I think this is great",
            "I believe in hard work",
            "My job is challenging",
            "My family lives nearby"
        ]
        
        # Execute and verify each message
        for message in personal_messages:
            is_important, weight = response_pipeline.is_important_memory(message, emotion_result)
            assert is_important is True, f"Message '{message}' should be marked as important"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
