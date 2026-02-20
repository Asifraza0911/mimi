"""
Callback Memory System Integration Code Snippet

This file contains the exact code snippets to integrate the Callback Memory System
into the Response Pipeline module when it is created in Task 11.

Requirements: 21.7, 21.9, 21.10
"""

# ============================================================================
# SNIPPET 1: Import Statement
# ============================================================================
# Add this to the imports section of response_pipeline.py

from backend.modules.callback_memory_system import CallbackMemorySystem
from typing import Dict, Optional
import logging

logger = logging.getLogger("ai_waifu.response_pipeline")


# ============================================================================
# SNIPPET 2: Initialization in __init__()
# ============================================================================
# Add these lines to ResponsePipeline.__init__()

class ResponsePipeline:
    def __init__(
        self,
        firestore_client,
        affection_decay_engine,
        interaction_streak_system,
        emotion_engine,
        memory_engine,
        memory_importance_scoring,
        personality_system,
        relationship_engine,
        attachment_style_engine,
        temperature_scaling_system,
        callback_memory_system: CallbackMemorySystem,  # ADD THIS PARAMETER
        llm_service
    ):
        # ... existing initialization ...
        self.callback_memory_system = callback_memory_system
        
        # Track callbacks per conversation to limit to once
        self.session_callback_count: Dict[str, int] = {}


# ============================================================================
# SNIPPET 3: Callback Triggering Logic in process_message()
# ============================================================================
# Insert this code AFTER memory retrieval and BEFORE prompt construction

async def process_message(self, user_id: str, message: str, platform: str):
    """Execute complete response generation pipeline."""
    
    # ... earlier steps: retrieve user, decay, streak, emotions, relationship ...
    
    # Step 6: Query similar memories with importance weighting
    similar_memories = self.memory_engine.retrieve_similar(
        user_id=user_id,
        query=message,
        k=3
    )
    
    # ========================================================================
    # Step 7: CHECK AND TRIGGER CALLBACK (NEW INTEGRATION POINT)
    # ========================================================================
    callback_text = None
    
    # Limit callbacks to once per conversation (Requirement 21.7)
    if self.session_callback_count.get(user_id, 0) == 0:
        # Check if callback should trigger based on affection level
        # This automatically suppresses when affection < 30 (Requirement 21.9)
        if self.callback_memory_system.should_trigger_callback(user_data.affection_level):
            # Select a high-weight memory (weight > 0.7) for callback
            selected_memory = self.callback_memory_system.select_callback_memory(
                user_data.long_term_memory
            )
            
            if selected_memory:
                # Format the callback with natural phrasing
                callback_text = self.callback_memory_system.format_callback(selected_memory)
                
                # Increment callback count to prevent multiple callbacks
                self.session_callback_count[user_id] = 1
                
                # Log callback event for monitoring
                logger.info(
                    f"Callback triggered for user {user_id}: "
                    f"affection={user_data.affection_level}, "
                    f"memory_weight={selected_memory.get('weight', 0.0)}, "
                    f"callback='{callback_text}'"
                )
            else:
                logger.debug(
                    f"Callback trigger attempted but no high-weight memories found "
                    f"for user {user_id}"
                )
        else:
            # Log suppression reason
            if user_data.affection_level < 30:
                logger.debug(
                    f"Callback suppressed due to low affection: "
                    f"user={user_id}, affection={user_data.affection_level}"
                )
            else:
                logger.debug(
                    f"Callback not triggered by probability: "
                    f"user={user_id}, affection={user_data.affection_level}"
                )
    else:
        logger.debug(
            f"Callback limit reached for user {user_id} "
            f"(count: {self.session_callback_count[user_id]})"
        )
    
    # Step 8: Get recent session context
    recent_context = self.get_session_context(user_id)
    
    # Step 9: Construct prompt with callback injection (Requirement 21.10)
    prompt = self.personality_system.construct_prompt(
        user_message=message,
        user_data=user_data,
        similar_memories=similar_memories,
        recent_context=recent_context,
        callback_text=callback_text  # Pass callback to prompt construction
    )
    
    # ... continue with temperature scaling, LLM call, memory storage, etc. ...


# ============================================================================
# SNIPPET 4: Session Cleanup Update
# ============================================================================
# Update the clear_inactive_sessions() method to reset callback counts

def clear_inactive_sessions(self):
    """Remove session contexts inactive for 30+ minutes."""
    timeout = timedelta(minutes=self.config.SESSION_TIMEOUT_MINUTES)
    now = datetime.now()
    
    inactive_users = [
        user_id for user_id, context in self.session_contexts.items()
        if now - context["last_activity"] > timeout
    ]
    
    for user_id in inactive_users:
        # Clear session context
        del self.session_contexts[user_id]
        
        # Reset callback count for cleared sessions
        if user_id in self.session_callback_count:
            del self.session_callback_count[user_id]
            logger.debug(f"Reset callback count for inactive user {user_id}")


# ============================================================================
# SNIPPET 5: PersonalitySystem.construct_prompt() Update
# ============================================================================
# Update the construct_prompt() method signature in personality_system.py

def construct_prompt(
    self,
    user_message: str,
    user_data,  # UserData type
    similar_memories: list,
    recent_context: list,
    callback_text: Optional[str] = None  # NEW PARAMETER
) -> str:
    """
    Build complete prompt for LLM.
    
    Args:
        user_message: Current user input
        user_data: User relationship state from Firestore
        similar_memories: Relevant past conversations
        recent_context: Last 5 message exchanges
        callback_text: Optional callback memory reference to inject
        
    Returns:
        Complete prompt string for LLM
    """
    prompt_parts = []
    
    # 1. Personality definition
    prompt_parts.append(self.personality_definition)
    
    # 2. Current relationship state
    prompt_parts.append(f"\nCurrent Relationship:")
    prompt_parts.append(f"- Affection Level: {user_data.affection_level}/100")
    prompt_parts.append(f"- Relationship Stage: {user_data.relationship_stage}")
    prompt_parts.append(f"- Current Mood: {user_data.mood}")
    
    # 3. Behavior instructions based on affection
    behavior = self.get_behavior_instructions(user_data.affection_level)
    prompt_parts.append(f"\nBehavior Guidance: {behavior}")
    
    # 4. Mood modifier
    mood_mod = self.get_mood_modifier(user_data.mood)
    prompt_parts.append(f"Mood Adjustment: {mood_mod}")
    
    # 5. Long-term memory
    if user_data.long_term_memory:
        prompt_parts.append(f"\nThings I remember about them:")
        for memory in user_data.long_term_memory[-5:]:
            memory_text = memory.get("text", memory) if isinstance(memory, dict) else memory
            prompt_parts.append(f"- {memory_text}")
    
    # 6. Similar past conversations
    if similar_memories:
        prompt_parts.append(f"\nRelevant past conversations:")
        for memory in similar_memories:
            prompt_parts.append(f"- {memory}")
    
    # 7. INJECT CALLBACK IF PRESENT (NEW INTEGRATION)
    if callback_text:
        prompt_parts.append(f"\n[Mimi recalls: {callback_text}]")
    
    # 8. Recent context
    if recent_context:
        prompt_parts.append(f"\nRecent conversation:")
        for msg in recent_context[-10:]:
            role = "Them" if msg.get("role") == "user" else "Me"
            prompt_parts.append(f"{role}: {msg.get('content')}")
    
    # 9. Current message
    prompt_parts.append(f"\nThem: {user_message}")
    prompt_parts.append(f"Me:")
    
    return "\n".join(prompt_parts)


# ============================================================================
# SNIPPET 6: Service Container Update (container.py or main.py)
# ============================================================================
# Update the service container to include CallbackMemorySystem

class ServiceContainer:
    def __init__(self, config):
        self.config = config
        self.firestore_client = self._init_firestore()
        
        # Core modules
        self.emotion_engine = EmotionEngine(self.firestore_client)
        self.memory_engine = MemoryEngine(self.firestore_client)
        self.personality_system = PersonalitySystem()
        self.relationship_engine = RelationshipEngine(self.firestore_client)
        self.llm_service = LLMService(config.HUGGINGFACE_API_TOKEN)
        
        # Advanced systems
        self.affection_decay_engine = AffectionDecayEngine(self.firestore_client)
        self.memory_importance_scoring = MemoryImportanceScoring()
        self.attachment_style_engine = AttachmentStyleEngine(self.firestore_client)
        self.temperature_scaling_system = TemperatureScalingSystem()
        self.interaction_streak_system = InteractionStreakSystem(self.firestore_client)
        self.callback_memory_system = CallbackMemorySystem()  # ADD THIS LINE
        
        # Response pipeline with all modules including callback system
        self.response_pipeline = ResponsePipeline(
            self.firestore_client,
            self.affection_decay_engine,
            self.interaction_streak_system,
            self.emotion_engine,
            self.memory_engine,
            self.memory_importance_scoring,
            self.personality_system,
            self.relationship_engine,
            self.attachment_style_engine,
            self.temperature_scaling_system,
            self.callback_memory_system,  # ADD THIS PARAMETER
            self.llm_service
        )


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================
"""
When implementing Task 11 (Create Response Pipeline), ensure:

[ ] Import CallbackMemorySystem in response_pipeline.py
[ ] Add callback_memory_system parameter to ResponsePipeline.__init__()
[ ] Initialize self.session_callback_count dictionary
[ ] Add callback triggering logic after memory retrieval
[ ] Pass callback_text to personality_system.construct_prompt()
[ ] Update PersonalitySystem.construct_prompt() to accept callback_text parameter
[ ] Inject callback into prompt when present
[ ] Reset callback count in clear_inactive_sessions()
[ ] Update ServiceContainer to initialize CallbackMemorySystem
[ ] Pass callback_memory_system to ResponsePipeline constructor
[ ] Test callback triggering with various affection levels
[ ] Test callback suppression when affection < 30
[ ] Test once-per-conversation limit
[ ] Verify callback appears in generated prompts

Requirements Validated:
- 21.7: Limit callbacks to once per conversation
- 21.9: Suppress callbacks when affection_level < 30
- 21.10: Inject selected callback into prompt context
"""
