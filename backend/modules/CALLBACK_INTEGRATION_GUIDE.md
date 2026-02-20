# Callback Memory System Integration Guide

## Overview

This document provides integration requirements for incorporating the Callback Memory System into the Response Pipeline module (to be created in Task 11).

**Related Requirements**: 21.7, 21.9, 21.10

## Integration Requirements

### 1. Module Import

```python
from backend.modules.callback_memory_system import CallbackMemorySystem
```

### 2. Initialization in ResponsePipeline

The `CallbackMemorySystem` should be initialized in the `ResponsePipeline.__init__()` method:

```python
class ResponsePipeline:
    def __init__(
        self,
        firestore_client,
        # ... other modules ...
        callback_memory_system: CallbackMemorySystem,
        # ... other modules ...
    ):
        self.callback_memory_system = callback_memory_system
        # Track callbacks per conversation to limit to once
        self.session_callback_count: Dict[str, int] = {}
```

### 3. Integration Point in process_message()

The callback system should be integrated **BEFORE** prompt construction in the response pipeline. The integration should occur after memory retrieval but before calling `PersonalitySystem.construct_prompt()`.

**Pipeline Order**:
1. Retrieve user data from Firestore
2. Apply affection decay
3. Update interaction streak
4. Detect emotions
5. Update relationship state
6. Query similar memories with importance weighting
7. **→ CHECK AND TRIGGER CALLBACK (NEW STEP)** ←
8. Get recent session context
9. Construct prompt with personality and callbacks
10. Get temperature based on mood
11. Generate LLM response
12. Store new memory

### 4. Implementation Logic

```python
async def process_message(
    self,
    user_id: str,
    message: str,
    platform: str
) -> ChatResponse:
    """
    Execute complete response generation pipeline.
    """
    # ... earlier pipeline steps (retrieve user, decay, streak, emotions, etc.) ...
    
    # Step 6: Query similar memories
    similar_memories = self.memory_engine.retrieve_similar(
        user_id=user_id,
        query=message,
        k=3
    )
    
    # Step 7: Check if callback should trigger
    callback_text = None
    
    # Limit callbacks to once per conversation
    if self.session_callback_count.get(user_id, 0) == 0:
        # Check if callback should trigger based on affection level
        if self.callback_memory_system.should_trigger_callback(user_data.affection_level):
            # Select a high-weight memory for callback
            selected_memory = self.callback_memory_system.select_callback_memory(
                user_data.long_term_memory
            )
            
            if selected_memory:
                # Format the callback
                callback_text = self.callback_memory_system.format_callback(selected_memory)
                
                # Increment callback count for this session
                self.session_callback_count[user_id] = 1
                
                # Log callback event
                logger.info(
                    f"Callback triggered for user {user_id}: "
                    f"affection={user_data.affection_level}, "
                    f"memory_weight={selected_memory.get('weight', 0.0)}"
                )
    
    # Step 8: Get recent session context
    recent_context = self.get_session_context(user_id)
    
    # Step 9: Construct prompt with callback injection
    prompt = self.personality_system.construct_prompt(
        user_message=message,
        user_data=user_data,
        similar_memories=similar_memories,
        recent_context=recent_context,
        callback_text=callback_text  # Pass callback to prompt construction
    )
    
    # ... continue with temperature scaling, LLM call, etc. ...
```

### 5. Callback Suppression Rules

**Requirement 21.9**: Suppress callbacks when `affection_level < 30`

This is already handled by `CallbackMemorySystem.should_trigger_callback()`, which returns `False` when affection is below 30.

### 6. Once-Per-Conversation Limit

**Requirement 21.7**: Limit callbacks to once per conversation

The `session_callback_count` dictionary tracks how many callbacks have been triggered for each user in the current session. The integration logic checks this count before attempting to trigger a callback.

**Session Management**:
- Initialize count to 0 for new sessions
- Increment to 1 when a callback is triggered
- Reset when session is cleared (after 30 minutes of inactivity)

### 7. Prompt Context Injection

**Requirement 21.10**: Inject selected callback into prompt context

The callback text should be passed to `PersonalitySystem.construct_prompt()` as a new parameter. The Personality System will be responsible for formatting and positioning the callback within the prompt.

**Expected Prompt Structure** (when callback is present):

```
[Personality Definition]
[Current Relationship State]
[Behavior Guidance]
[Mood Adjustment]
[Long-term Memory]
[Similar Past Conversations]
[Callback Reference] ← "I remember when you told me [memory text]"
[Recent Conversation]
[Current Message]
```

### 8. PersonalitySystem.construct_prompt() Update

The `construct_prompt()` method signature should be updated to accept an optional `callback_text` parameter:

```python
def construct_prompt(
    self,
    user_message: str,
    user_data: UserData,
    similar_memories: List[str],
    recent_context: List[Message],
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
    
    # ... existing prompt construction ...
    
    # Inject callback if present (before recent context)
    if callback_text:
        prompt_parts.append(f"\n[Mimi recalls: {callback_text}]")
    
    # ... continue with recent context and current message ...
```

### 9. Session Cleanup

When clearing inactive sessions in `clear_inactive_sessions()`, also reset the callback count:

```python
def clear_inactive_sessions(self):
    timeout = timedelta(minutes=self.config.SESSION_TIMEOUT_MINUTES)
    now = datetime.now()
    
    inactive_users = [
        user_id for user_id, context in self.session_contexts.items()
        if now - context["last_activity"] > timeout
    ]
    
    for user_id in inactive_users:
        del self.session_contexts[user_id]
        # Reset callback count for cleared sessions
        if user_id in self.session_callback_count:
            del self.session_callback_count[user_id]
```

### 10. Logging and Monitoring

Log callback events for monitoring and debugging:

```python
import logging

logger = logging.getLogger("ai_waifu.callback_system")

# Log when callback is triggered
logger.info(
    f"Callback triggered - user: {user_id}, "
    f"affection: {affection_level}, "
    f"memory_weight: {memory_weight}, "
    f"callback: {callback_text}"
)

# Log when callback is suppressed
logger.debug(
    f"Callback suppressed - user: {user_id}, "
    f"affection: {affection_level} (threshold: 30)"
)

# Log when callback limit reached
logger.debug(
    f"Callback limit reached - user: {user_id}, "
    f"count: {self.session_callback_count[user_id]}"
)
```

## Testing Considerations

When implementing the Response Pipeline (Task 11), ensure the following test scenarios:

1. **Callback Triggering**: Verify callbacks trigger probabilistically based on affection level
2. **Affection Threshold**: Verify callbacks are suppressed when affection < 30
3. **Once-Per-Conversation**: Verify only one callback occurs per session
4. **High-Weight Selection**: Verify only memories with weight > 0.7 are selected
5. **Prompt Injection**: Verify callback text appears in the constructed prompt
6. **Session Reset**: Verify callback count resets after session timeout

## Requirements Validation

- **Requirement 21.7**: Callback limit enforced via `session_callback_count` dictionary
- **Requirement 21.9**: Affection threshold enforced in `should_trigger_callback()`
- **Requirement 21.10**: Callback injection via `construct_prompt()` parameter

## Summary

The Callback Memory System is fully implemented and ready for integration. When creating the Response Pipeline module (Task 11), follow this guide to:

1. Import and initialize `CallbackMemorySystem`
2. Add callback triggering logic before prompt construction
3. Track callbacks per session to limit to once
4. Pass callback text to `PersonalitySystem.construct_prompt()`
5. Update `PersonalitySystem` to accept and inject callback text
6. Reset callback counts during session cleanup

This integration will enable Mimi to naturally reference past conversations, creating continuity and demonstrating genuine memory of the relationship.
