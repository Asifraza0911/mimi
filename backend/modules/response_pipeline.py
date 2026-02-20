"""
Response Pipeline module for AI Waifu Cross-Platform System.

This module orchestrates all processing modules to generate contextually-aware
responses with emotional intelligence, memory retrieval, and relationship progression.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from models import (
    ChatResponse,
    Message,
    UserData,
    EmotionResult,
    RelationshipUpdate,
    DecayResult,
    StreakResult,
    MemoryEntry
)
from exceptions import (
    FirestoreConnectionError,
    LLMServiceError,
    MemoryEngineError,
    EmotionEngineError
)

logger = logging.getLogger("ai_waifu.response_pipeline")


class ResponsePipeline:
    """
    Main orchestrator that coordinates all processing modules.
    
    Pipeline execution order:
    1. Retrieve user data from Firestore
    2. Apply affection decay based on time since last interaction
    3. Update interaction streak and apply penalties if broken
    4. Detect emotions and update mood
    5. Update relationship state and attachment style
    6. Query similar memories with importance weighting
    7. Determine if callback memory should be triggered
    8. Get recent session context
    9. Construct prompt with personality and callbacks
    10. Get temperature based on current mood
    11. Generate LLM response with scaled temperature
    12. Assign importance weight to new memory
    13. Store new memory with weight
    14. Return response
    """
    
    def __init__(
        self,
        firestore_client,
        affection_decay_engine,
        interaction_streak_system,
        emotion_engine,
        memory_engine,
        personality_system,
        relationship_engine,
        attachment_style_engine,
        temperature_scaling_system,
        callback_memory_system,
        llm_service
    ):
        """
        Initialize Response Pipeline with all processing modules.
        
        Args:
            firestore_client: Firebase Firestore client for persistent storage
            affection_decay_engine: AffectionDecayEngine instance
            interaction_streak_system: InteractionStreakSystem instance
            emotion_engine: EmotionEngine instance
            memory_engine: MemoryEngine instance
            personality_system: PersonalitySystem instance
            relationship_engine: RelationshipEngine instance
            attachment_style_engine: AttachmentStyleEngine instance
            temperature_scaling_system: TemperatureScalingSystem instance
            callback_memory_system: CallbackMemorySystem instance
            llm_service: LLMService instance
        """
        self.firestore = firestore_client
        self.affection_decay_engine = affection_decay_engine
        self.interaction_streak_system = interaction_streak_system
        self.emotion_engine = emotion_engine
        self.memory_engine = memory_engine
        self.personality_system = personality_system
        self.relationship_engine = relationship_engine
        self.attachment_style_engine = attachment_style_engine
        self.temperature_scaling_system = temperature_scaling_system
        self.callback_memory_system = callback_memory_system
        self.llm_service = llm_service
        
        # In-memory session context storage
        # Structure: {user_id: {"messages": List[Message], "last_activity": datetime}}
        self.session_contexts: Dict[str, Dict] = {}
        
        # Track callback usage per session to limit frequency
        # Structure: {user_id: callback_count}
        self.session_callback_count: Dict[str, int] = {}
        
        logger.info("Response Pipeline initialized with all modules")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        platform: str
    ) -> ChatResponse:
        """
        Execute complete response generation pipeline with advanced systems.
        
        Pipeline steps:
        1. Retrieve user data from Firestore
        2. Apply affection decay based on time since last interaction
        3. Update interaction streak and apply penalties if broken
        4. Detect emotions and update mood
        5. Query similar memories with importance weighting
        6. Determine if callback memory should be triggered
        7. Get recent session context
        8. Construct prompt with personality and callbacks
        9. Get temperature based on current mood
        10. Generate LLM response with scaled temperature
        11. Update relationship state and attachment_state
        12. Assign importance weight to new memory
        13. Store new memory with weight
        14. Update session context and return response
        
        Args:
            user_id: User identifier
            message: User's message
            platform: Source platform (web/discord)
            
        Returns:
            ChatResponse with reply, affection_level, mood
        """
        logger.info(f"Processing message for user {user_id} from {platform}")
        
        # Step 1: Retrieve or create user data with error handling
        try:
            user_data = self.get_or_create_user(user_id)
            logger.debug(f"User data retrieved: affection={user_data.affection_level}, mood={user_data.mood}")
        except FirestoreConnectionError as e:
            logger.error(f"Firestore connection failed for user {user_id}: {e}")
            logger.warning("Using in-memory default user data")
            # Use in-memory defaults
            user_data = self._get_default_user_data()
        
        # Step 2: Apply affection decay with error handling
        try:
            decay_result = self.affection_decay_engine.apply_decay(user_id, user_data)
            if decay_result.affection_delta < 0:
                user_data.affection_level = max(0, user_data.affection_level + decay_result.affection_delta)
                if decay_result.new_mood:
                    user_data.mood = decay_result.new_mood
                logger.info(f"Affection decay applied: {decay_result.affection_delta} points, {decay_result.hours_passed} hours passed")
        except Exception as e:
            logger.error(f"Affection decay engine failed: {e}")
            logger.warning("Skipping affection decay")
        
        # Step 3: Update interaction streak with error handling
        try:
            streak_result = self.interaction_streak_system.update_streak(user_id, user_data)
            user_data.daily_interaction_streak = streak_result.new_streak
            if streak_result.was_broken:
                user_data.affection_level = max(0, user_data.affection_level + streak_result.affection_delta)
                user_data.mood = "sad"
                logger.info(f"Streak broken: penalty of {streak_result.affection_delta} points applied")
        except Exception as e:
            logger.error(f"Interaction streak system failed: {e}")
            logger.warning("Skipping streak update")
            streak_result = StreakResult(new_streak=1, was_broken=False, affection_delta=0)
        
        # Step 4: Detect emotions with error handling
        try:
            emotion_result = self.emotion_engine.detect_emotions(message, user_id)
            if emotion_result.detected_mood and emotion_result.detected_mood != "neutral":
                user_data.mood = emotion_result.detected_mood
                user_data.affection_level = max(0, min(100, user_data.affection_level + emotion_result.affection_delta))
                logger.info(f"Emotion detected: {emotion_result.detected_mood}, affection delta: {emotion_result.affection_delta}")
        except EmotionEngineError as e:
            logger.error(f"Emotion engine failed: {e}")
            logger.warning("Using neutral mood as fallback")
            # Use neutral mood as fallback
            emotion_result = EmotionResult(detected_mood="neutral", affection_delta=0, triggers=[])
        
        # Step 5: Query similar memories with importance weighting with error handling
        similar_memories = []
        try:
            similar_memories = self.memory_engine.retrieve_similar(user_id, message, k=3)
            logger.debug(f"Retrieved {len(similar_memories)} similar memories")
        except MemoryEngineError as e:
            logger.error(f"Memory engine retrieval failed: {e}")
            logger.warning("Skipping vector memory retrieval")
            # Continue without vector memories
        
        # Step 6: Determine if callback memory should be triggered
        callback_text = None
        callback_count = self.session_callback_count.get(user_id, 0)
        if callback_count < 1:  # Limit to once per session
            if self.callback_memory_system.should_trigger_callback(user_data.affection_level):
                # Convert MemoryEntry objects to dicts for callback system
                long_term_memory_dicts = [
                    {"text": mem.text, "weight": mem.weight}
                    for mem in user_data.long_term_memory
                ]
                callback_memory = self.callback_memory_system.select_callback_memory(long_term_memory_dicts)
                if callback_memory:
                    callback_text = self.callback_memory_system.format_callback(callback_memory)
                    self.session_callback_count[user_id] = callback_count + 1
                    logger.info(f"Callback memory triggered for user {user_id}")
        
        # Step 7: Get recent session context
        recent_context = self.get_session_context(user_id)
        
        # Step 8: Construct prompt with personality and callbacks with error handling
        try:
            # Convert UserData to dict for personality_system compatibility
            user_data_dict = {
                "affection_level": user_data.affection_level,
                "mood": user_data.mood,
                "relationship_stage": user_data.relationship_stage,
                "attachment_state": user_data.attachment_state,
                "long_term_memory": [{"text": mem.text, "weight": mem.weight} for mem in user_data.long_term_memory]
            }
            
            # Convert Message objects to dicts for personality_system
            recent_context_dicts = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_context
            ]
            
            # Add callback to similar memories if present
            memories_with_callback = similar_memories.copy() if similar_memories else []
            if callback_text:
                memories_with_callback.insert(0, callback_text)
            
            prompt = self.personality_system.construct_prompt(
                user_message=message,
                user_data=user_data_dict,
                similar_memories=memories_with_callback,
                recent_context=recent_context_dicts,
                attachment_state=user_data.attachment_state,
                daily_interaction_streak=user_data.daily_interaction_streak,
                streak_broken=streak_result.was_broken
            )
            logger.debug("Prompt constructed with all context")
        except Exception as e:
            logger.error(f"Personality system failed to construct prompt: {e}")
            logger.warning("Using minimal default prompt")
            # Use minimal default prompt
            prompt = self._get_minimal_default_prompt(message, user_data)
        
        # Step 9: Get temperature based on current mood
        temperature = self.temperature_scaling_system.get_temperature(user_data.mood)
        logger.debug(f"Temperature for mood '{user_data.mood}': {temperature}")
        
        # Step 10: Generate LLM response with scaled temperature with error handling
        try:
            reply = self.llm_service.generate_response(prompt, temperature=temperature)
            logger.info(f"LLM response generated for user {user_id}")
        except LLMServiceError as e:
            logger.error(f"LLM service failed: {e}")
            logger.warning("Using fallback response")
            # Use fallback response
            reply = self.llm_service.get_fallback_response()
        
        # Step 11: Update relationship state and attachment_state with error handling
        try:
            relationship_update = self.relationship_engine.update_relationship(user_id, message, user_data)
            user_data.affection_level = relationship_update.affection_level
            user_data.trust_level = relationship_update.trust_level
            user_data.mood = relationship_update.mood
            user_data.relationship_stage = relationship_update.relationship_stage
            if relationship_update.attachment_state:
                user_data.attachment_state = relationship_update.attachment_state
            logger.debug(f"Relationship updated: stage={user_data.relationship_stage}, attachment={user_data.attachment_state}")
        except Exception as e:
            logger.error(f"Relationship engine failed: {e}")
            logger.warning("Skipping relationship update")
        
        # Step 12: Assign importance weight to new memory
        is_important, memory_weight = self.is_important_memory(message, emotion_result)
        logger.debug(f"Memory importance determined: important={is_important}, weight={memory_weight}")
        
        # Step 13: Store new memory with weight with error handling
        if is_important:
            try:
                self.memory_engine.store_memory(user_id, message, is_important, weight=memory_weight)
                logger.info(f"Memory stored with weight {memory_weight}")
            except MemoryEngineError as e:
                logger.error(f"Memory storage failed: {e}")
                logger.warning("Skipping memory storage")
        
        # Step 14: Update session context
        self.update_session_context(user_id, Message(role="user", content=message))
        self.update_session_context(user_id, Message(role="assistant", content=reply))
        
        # Update last interaction timestamp
        user_data.last_interaction = datetime.now()
        
        # Return response
        return ChatResponse(
            reply=reply,
            affection_level=user_data.affection_level,
            mood=user_data.mood
        )
    
    def get_or_create_user(self, user_id: str) -> UserData:
        """
        Retrieve user from Firestore or create with defaults.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserData instance with current state
        """
        # This will be implemented by calling firestore_operations module
        # For now, return a placeholder that will be replaced in integration
        from modules.firestore_operations import get_or_create_user
        return get_or_create_user(self.firestore, user_id)
    
    def get_session_context(self, user_id: str) -> List[Message]:
        """
        Get recent conversation context for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recent messages (last 5 exchanges = 10 messages)
        """
        if user_id not in self.session_contexts:
            return []
        
        return self.session_contexts[user_id].get("messages", [])
    
    def update_session_context(self, user_id: str, message: Message):
        """
        Add message to session context, keeping last 5 exchanges (10 messages).
        
        Args:
            user_id: User identifier
            message: Message to add to context
        """
        if user_id not in self.session_contexts:
            self.session_contexts[user_id] = {
                "messages": [],
                "last_activity": datetime.now()
            }
        
        context = self.session_contexts[user_id]
        context["messages"].append(message)
        context["last_activity"] = datetime.now()
        
        # Keep only last 10 messages (5 exchanges)
        if len(context["messages"]) > 10:
            context["messages"] = context["messages"][-10:]
        
        logger.debug(f"Session context updated for user {user_id}: {len(context['messages'])} messages")
    
    def is_important_memory(self, message: str, emotion_result: EmotionResult) -> tuple[bool, float]:
        """
        Determine if a message should be stored as an important memory and assign weight.
        
        This method checks for:
        - Emotional content (detected by emotion engine)
        - Personal information keywords (preferences, facts about user)
        - Long messages (indicating sharing/detailed information)
        
        Args:
            message: User's message text
            emotion_result: Emotion detection result from EmotionEngine
            
        Returns:
            Tuple of (is_important: bool, weight: float)
            - is_important: True if memory should be stored in Firestore
            - weight: Importance weight between 0.0 and 1.0
            
        Requirements: 8.2, 8.3, 8.4, 17.2
        """
        # Convert EmotionResult to dict for memory engine
        emotion_result_dict = {
            "detected_mood": emotion_result.detected_mood,
            "affection_delta": emotion_result.affection_delta,
            "triggers": emotion_result.triggers
        }
        
        # Call Memory Engine to calculate weight based on content and emotion
        weight = self.memory_engine.calculate_memory_weight(message, emotion_result_dict)
        
        # Additional heuristics for importance determination
        message_lower = message.lower()
        
        # Check for emotional content (non-neutral mood detected)
        has_emotional_content = emotion_result.detected_mood and emotion_result.detected_mood != "neutral"
        
        # Check for personal information keywords
        personal_keywords = [
            "my name", "i am", "i'm", "i like", "i love", "i hate", 
            "my favorite", "i work", "i study", "i prefer", "i enjoy",
            "i feel", "i think", "i believe", "my job", "my family"
        ]
        has_personal_info = any(keyword in message_lower for keyword in personal_keywords)
        
        # Check for long messages (indicates sharing/detailed information)
        word_count = len(message.split())
        is_long_message = word_count > 20
        
        # Determine if memory is important enough to store
        # Store if:
        # 1. Has emotional content, OR
        # 2. Contains personal information, OR
        # 3. Is a long message (detailed sharing), OR
        # 4. Weight is >= 0.5 (significant importance)
        is_important = (
            has_emotional_content or 
            has_personal_info or 
            is_long_message or 
            weight >= 0.5
        )
        
        logger.debug(
            f"Memory importance check: emotional={has_emotional_content}, "
            f"personal={has_personal_info}, long={is_long_message}, "
            f"weight={weight:.2f}, important={is_important}"
        )
        
        return (is_important, weight)
    
    def clear_inactive_sessions(self, timeout_minutes: int = 30):
        """
        Remove session contexts inactive for specified duration.
        
        Args:
            timeout_minutes: Inactivity timeout in minutes (default: 30)
        """
        timeout = timedelta(minutes=timeout_minutes)
        now = datetime.now()
        
        inactive_users = [
            user_id for user_id, context in self.session_contexts.items()
            if now - context["last_activity"] > timeout
        ]
        
        for user_id in inactive_users:
            del self.session_contexts[user_id]
            # Also clear callback count
            if user_id in self.session_callback_count:
                del self.session_callback_count[user_id]
        
        if inactive_users:
            logger.info(f"Cleared {len(inactive_users)} inactive sessions")
    
    def _get_default_user_data(self) -> UserData:
        """
        Create default user data for when Firestore is unavailable.
        
        Returns:
            UserData with default values
        """
        from datetime import date
        
        return UserData(
            user_id="default",
            name=None,
            affection_level=10,
            trust_level=5,
            mood="neutral",
            relationship_stage="stranger",
            attachment_state="avoidant",
            long_term_memory=[],
            emotional_memory=[],
            last_interaction=datetime.now(),
            last_chat_date=date.today(),
            daily_interaction_streak=1,
            created_at=datetime.now(),
            platform_stats={"web": 0, "discord": 0}
        )
    
    def _get_minimal_default_prompt(self, message: str, user_data: UserData) -> str:
        """
        Create a minimal default prompt when Personality System fails.
        
        Args:
            message: User's message
            user_data: Current user data
            
        Returns:
            Minimal prompt string
        """
        return f"""You are Mimi, a tsundere anime girl. You are sharp-tongued but secretly caring.

Current mood: {user_data.mood}
Affection level: {user_data.affection_level}/100

User says: {message}

Respond in character as Mimi:"""


