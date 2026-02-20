"""Service container for dependency injection."""

import logging
from google.cloud.firestore import Client

from config import Config, initialize_firestore
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
from modules.response_pipeline import ResponsePipeline


logger = logging.getLogger("ai_waifu.container")


class ServiceContainer:
    """
    Service container for dependency injection.
    
    Initializes all backend modules with proper dependencies:
    - Firestore client
    - Core processing modules (Memory, Emotion, Personality, Relationship)
    - LLM Service
    - Advanced emotional systems (Decay, Attachment, Temperature, Streak, Callback)
    - Response Pipeline with all modules
    
    Provides a clean interface for the FastAPI app to access services.
    """
    
    def __init__(self, config: Config):
        """
        Initialize service container with all modules.
        
        Args:
            config: Application configuration
        """
        self.config = config
        logger.info("Initializing service container")
        
        # Initialize Firestore client
        logger.info("Initializing Firestore client")
        self.firestore_client: Client = initialize_firestore()
        
        # Initialize core modules
        logger.info("Initializing core processing modules")
        self.emotion_engine = EmotionEngine(self.firestore_client)
        self.memory_engine = MemoryEngine(self.firestore_client)
        self.personality_system = PersonalitySystem()
        self.relationship_engine = RelationshipEngine(self.firestore_client)
        self.llm_service = LLMService(config.HUGGINGFACE_API_TOKEN)
        
        # Initialize advanced emotional systems
        logger.info("Initializing advanced emotional systems")
        self.affection_decay_engine = AffectionDecayEngine(self.firestore_client)
        self.attachment_style_engine = AttachmentStyleEngine(self.firestore_client)
        self.temperature_scaling_system = TemperatureScalingSystem()
        self.interaction_streak_system = InteractionStreakSystem(self.firestore_client)
        self.callback_memory_system = CallbackMemorySystem()
        
        # Initialize response pipeline with all modules
        logger.info("Initializing response pipeline")
        self.response_pipeline = ResponsePipeline(
            firestore_client=self.firestore_client,
            affection_decay_engine=self.affection_decay_engine,
            interaction_streak_system=self.interaction_streak_system,
            emotion_engine=self.emotion_engine,
            memory_engine=self.memory_engine,
            personality_system=self.personality_system,
            relationship_engine=self.relationship_engine,
            attachment_style_engine=self.attachment_style_engine,
            temperature_scaling_system=self.temperature_scaling_system,
            callback_memory_system=self.callback_memory_system,
            llm_service=self.llm_service
        )
        
        logger.info("Service container initialized successfully")
    
    def get_response_pipeline(self) -> ResponsePipeline:
        """
        Get the response pipeline instance.
        
        Returns:
            ResponsePipeline: Configured response pipeline
        """
        return self.response_pipeline
    
    def get_firestore_client(self) -> Client:
        """
        Get the Firestore client instance.
        
        Returns:
            Client: Firestore client
        """
        return self.firestore_client
    
    def get_llm_service(self) -> LLMService:
        """
        Get the LLM service instance.
        
        Returns:
            LLMService: LLM service
        """
        return self.llm_service
    
    def health_check(self) -> dict:
        """
        Check health status of all services.
        
        Returns:
            dict: Health status of each service
        """
        logger.debug("Performing health check")
        
        health_status = {
            "firestore": "unknown",
            "llm": "unknown",
            "memory_engine": "unknown"
        }
        
        # Check Firestore connection
        try:
            # Attempt a lightweight operation
            list(self.firestore_client.collections(max_results=1))
            health_status["firestore"] = "connected"
            logger.debug("Firestore health check: connected")
        except Exception as e:
            health_status["firestore"] = f"error: {str(e)}"
            logger.error(f"Firestore health check failed: {str(e)}")
        
        # Check LLM service (just verify token is set)
        if self.llm_service.api_token:
            health_status["llm"] = "available"
            logger.debug("LLM service health check: available")
        else:
            health_status["llm"] = "error: no API token"
            logger.error("LLM service health check failed: no API token")
        
        # Check Memory Engine (verify model is loaded)
        try:
            if self.memory_engine.model is not None:
                health_status["memory_engine"] = "ready"
                logger.debug("Memory engine health check: ready")
            else:
                health_status["memory_engine"] = "error: model not loaded"
                logger.error("Memory engine health check failed: model not loaded")
        except Exception as e:
            health_status["memory_engine"] = f"error: {str(e)}"
            logger.error(f"Memory engine health check failed: {str(e)}")
        
        return health_status
