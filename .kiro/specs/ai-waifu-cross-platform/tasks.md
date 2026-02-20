# Implementation Plan: AI Waifu Cross-Platform System

## Overview

This implementation plan breaks down the AI Waifu Cross-Platform System into discrete coding tasks. The system consists of a FastAPI backend (AI_Brain) with 7 core modules, Firebase Firestore for persistent storage, FAISS for vector similarity memory, an Angular web client, and a Discord bot. The implementation follows an incremental approach, building core functionality first, then adding memory systems, emotion detection, relationship progression, and finally client integrations.

## Tasks

- [x] 1. Project setup and configuration
  - [x] 1.1 Initialize Python backend project structure
    - Create directory structure: `backend/`, `backend/modules/`, `backend/tests/`, `backend/config/`
    - Create `requirements.txt` with FastAPI, uvicorn, pydantic, firebase-admin, sentence-transformers, faiss-cpu, numpy, requests, python-dotenv, hypothesis, pytest
    - Create `.env.example` file with required environment variables
    - Create `backend/config.py` for configuration management
    - _Requirements: 9.1, 9.2, 9.4, 9.5_

  - [x] 1.2 Set up Firebase Firestore connection
    - Implement Firestore client initialization in `config.py`
    - Create helper function to load Firebase credentials from environment
    - Add Firestore connection validation
    - _Requirements: 2.1, 9.2_

  - [x] 1.3 Create personality definition file
    - Create `backend/waifu_personality.txt` with Mimi's character definition
    - Include core traits, speech patterns, tsundere expressions, emotional reactions, affection tier behaviors, and mood modifiers
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 1.4 Initialize Angular web client project
    - Create Angular 17+ project with standalone components: `ng new web-client --standalone`
    - Install TailwindCSS and configure
    - Create environment configuration files with API URL
    - _Requirements: 7.1, 7.2_

  - [x] 1.5 Initialize Discord bot project structure
    - Create `discord-bot/` directory
    - Create `discord_bot.py` main file
    - Create `requirements.txt` with discord.py and requests
    - _Requirements: 6.5_

- [x] 2. Implement core data models and API foundation
  - [x] 2.1 Create Pydantic data models
    - Create `backend/models.py` with ChatRequest, ChatResponse, UserData, EmotionResult, RelationshipUpdate, SentimentScore, Message models
    - Define field validation rules and type constraints
    - _Requirements: 1.2, 1.3_

  - [x] 2.2 Implement FastAPI application skeleton
    - Create `backend/main.py` with FastAPI app initialization
    - Implement POST /chat endpoint skeleton
    - Implement GET /health endpoint
    - Add CORS middleware configuration
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 2.3 Write property test for request validation
    - **Property 1: Request Validation**
    - **Validates: Requirements 1.2**
    - Use hypothesis to generate valid/invalid ChatRequest payloads
    - Verify API accepts valid requests and rejects invalid ones with 422

  - [x] 2.4 Implement Firestore user document operations
    - Create `backend/modules/firestore_operations.py`
    - Implement `get_or_create_user(user_id)` function with default values
    - Implement `update_user_data(user_id, updates)` function
    - Implement `get_user_data(user_id)` function
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 2.4.5 Update Firestore schema for advanced systems
    - Update `get_or_create_user()` to include attachment_state (default: "avoidant")
    - Update `get_or_create_user()` to include daily_interaction_streak (default: 0)
    - Update `get_or_create_user()` to include last_chat_date (default: None)
    - Update long_term_memory structure to store objects with text and weight fields
    - _Requirements: 2.8, 2.9, 2.10, 2.11, 18.2, 20.2_

  - [x] 2.5 Write property tests for user document operations
    - **Property 3: User Document Schema Integrity**
    - **Property 4: New User Initialization**
    - **Property 5: Timestamp Update on Interaction**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**
    - Test document structure, default values, and timestamp updates

- [x] 3. Checkpoint - Verify API and Firestore integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Memory Engine with FAISS
  - [x] 4.1 Create Memory Engine module
    - Create `backend/modules/memory_engine.py` with MemoryEngine class
    - Initialize sentence-transformers model (all-MiniLM-L6-v2)
    - Implement `generate_embedding(text)` method
    - Create directory for FAISS indices: `backend/faiss_indices/`
    - _Requirements: 3.1, 3.6_

  - [x] 4.2 Write property test for embedding generation
    - **Property 6: Embedding Dimension Consistency**
    - **Validates: Requirements 3.1**
    - Test that all generated embeddings have dimension 384

  - [x] 4.3 Implement FAISS index management
    - Implement `get_or_create_index(user_id)` method
    - Implement index persistence to disk
    - Implement metadata storage for message texts and timestamps
    - _Requirements: 3.3, 3.6_

  - [x] 4.4 Implement memory storage functionality
    - Implement `store_memory(user_id, message, is_important)` method
    - Add vector to FAISS index
    - Update metadata file
    - Optionally store in Firestore long_term_memory
    - _Requirements: 3.2, 3.3, 8.4_

  - [x] 4.5 Write property test for memory storage
    - **Property 7: Important Message Storage**
    - **Validates: Requirements 3.2, 3.3**
    - Test that important messages increase FAISS index size

  - [x] 4.6 Implement semantic memory retrieval
    - Implement `retrieve_similar(user_id, query, k)` method
    - Perform FAISS similarity search
    - Return k most similar messages
    - _Requirements: 3.4_

  - [x] 4.7 Write property tests for memory retrieval
    - **Property 8: Semantic Memory Retrieval**
    - **Property 10: User Memory Isolation**
    - **Validates: Requirements 3.4, 3.6**
    - Test similarity search and cross-user isolation

- [x] 5. Checkpoint - Verify Memory Engine functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Emotion Engine
  - [x] 6.1 Create Emotion Engine module
    - Create `backend/modules/emotion_engine.py` with EmotionEngine class
    - Define jealousy_keywords list
    - Define emotion_keywords dictionary for happy, sad, angry, vulnerable
    - _Requirements: 5.1.1, 5.1.2, 5.1.8_

  - [x] 6.2 Implement jealousy detection
    - Implement `check_jealousy(message)` method
    - Check for jealousy keywords in message
    - _Requirements: 5.1.2_

  - [x] 6.3 Implement emotion detection logic
    - Implement `detect_emotions(message, user_id)` method
    - Check jealousy first (highest priority)
    - Check other emotion keywords
    - Return EmotionResult with detected_mood, affection_delta, triggers
    - _Requirements: 5.1.8, 5.1.9, 5.1.10_

  - [x] 6.4 Implement mood and affection updates
    - Implement `update_mood(user_id, mood, affection_delta)` method
    - Update Firestore with new mood and affection_level
    - Store event in emotional_memory array
    - _Requirements: 5.1.3, 5.1.4, 5.1.5, 5.1.6, 8.5_

  - [x] 6.5 Write property tests for emotion detection
    - **Property 19: Jealousy Detection and Response**
    - **Property 20: Emotional Keyword Detection and Mood Update**
    - **Property 22: Emotional Memory Recording**
    - **Validates: Requirements 5.1.2, 5.1.3, 5.1.4, 5.1.6, 5.1.8, 5.1.9, 8.1, 8.5**
    - Test jealousy triggers, mood updates, and emotional memory storage

- [x] 7. Implement Personality System
  - [x] 7.1 Create Personality System module
    - Create `backend/modules/personality_system.py` with PersonalitySystem class
    - Implement `_load_personality(personality_file)` method
    - Load personality definition at initialization
    - _Requirements: 4.1, 4.10_

  - [x] 7.2 Define affection tier behaviors
    - Implement `_define_affection_tiers()` method
    - Define behavior instructions for affection ranges: 0-20, 21-50, 51-80, 81-100
    - Implement `get_behavior_instructions(affection_level)` method
    - _Requirements: 5.8, 5.9, 5.10, 5.11_

  - [x] 7.3 Define mood modifiers
    - Implement `_define_mood_modifiers()` method
    - Define tone adjustments for happy, neutral, sad, jealous, angry, flustered moods
    - Implement `get_mood_modifier(mood)` method
    - _Requirements: 5.12, 5.13, 5.14, 5.15, 5.16, 5.17, 5.1.7_

  - [x] 7.4 Implement prompt construction
    - Implement `construct_prompt(user_message, user_data, similar_memories, recent_context)` method
    - Combine personality definition, relationship state, behavior guidance, mood adjustment, long-term memory, similar memories, recent context, and current message
    - _Requirements: 4.8, 3.5, 14.2_

  - [x] 7.5 Write property tests for prompt construction
    - **Property 9: Memory Injection in Prompts**
    - **Property 11: Prompt Component Completeness**
    - **Property 24: Recent Context Inclusion**
    - **Validates: Requirements 3.5, 4.8, 14.2**
    - Test that prompts contain all required components

- [x] 8. Implement Relationship Engine
  - [x] 8.1 Create Relationship Engine module
    - Create `backend/modules/relationship_engine.py` with RelationshipEngine class
    - Define stage_thresholds dictionary
    - _Requirements: 5.5_

  - [x] 8.2 Implement sentiment analysis
    - Implement `analyze_sentiment(message)` method
    - Detect compliments, vulnerability, positive/negative/rude messages
    - Return SentimentScore
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 8.3 Implement affection calculation
    - Implement `calculate_affection_delta(sentiment)` method
    - Return affection change based on sentiment type
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 8.4 Implement relationship stage determination
    - Implement `determine_stage(affection_level)` method
    - Map affection level to relationship stage
    - _Requirements: 5.5_

  - [x] 8.5 Implement relationship update orchestration
    - Implement `update_relationship(user_id, message, current_state)` method
    - Analyze sentiment, calculate affection delta, determine new stage, update mood
    - Return RelationshipUpdate
    - _Requirements: 5.6, 5.7_

  - [x] 8.6 Implement relationship persistence
    - Implement `persist_update(user_id, update)` method
    - Save changes to Firestore
    - _Requirements: 5.7_

  - [x] 8.7 Write property tests for relationship progression
    - **Property 13: Compliment Affection Increase**
    - **Property 14: Vulnerability Trust Increase**
    - **Property 15: Rude Message Affection Decrease**
    - **Property 16: Affection Threshold Stage Transition**
    - **Property 17: Sentiment-Based Mood Update**
    - **Property 18: Relationship State Persistence**
    - **Validates: Requirements 5.1, 5.2, 5.4, 5.5, 5.6, 5.7**
    - Test affection changes, stage transitions, and persistence

- [ ] 9. Checkpoint - Verify core processing modules
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9.5 Implement Affection Decay Engine
  - [x] 9.5.1 Create Affection Decay Engine module
    - Create `backend/modules/affection_decay_engine.py` with AffectionDecayEngine class
    - Implement `calculate_decay(last_interaction, current_time)` method
    - Calculate hours_passed between timestamps
    - Return decay amount as integer division of hours_passed by 24
    - _Requirements: 16.1, 16.2, 16.3_

  - [x] 9.5.2 Implement decay application logic
    - Implement `apply_decay(user_id, user_data)` method
    - Decrease affection_level by decay amount
    - Ensure affection_level never drops below 0
    - Set mood to "sad" if hours_passed > 72
    - Update Firestore with decayed values
    - _Requirements: 16.4, 16.5, 16.7_

  - [x] 9.5.3 Write property tests for affection decay
    - **Property 26: Affection Decay Calculation**
    - **Property 27: Sad Mood on Extended Absence**
    - **Validates: Requirements 16.2, 16.3, 16.4, 16.7**
    - Test decay calculation and mood changes based on absence duration

- [ ] 9.6 Implement Memory Importance Scoring
  - [x] 9.6.1 Update Memory Engine with weight support
    - Modify `backend/modules/memory_engine.py` to support Memory_Weight
    - Update `store_memory()` to accept weight parameter
    - Store memories as objects with text and weight fields in Firestore
    - Update FAISS metadata to include weight values
    - _Requirements: 17.1, 17.3_

  - [x] 9.6.2 Implement memory weight assignment logic
    - Create `calculate_memory_weight(message, emotion_result)` method
    - Assign 0.1 for casual greetings
    - Assign 0.5 for preferences
    - Assign 0.9 for emotional vulnerability
    - Assign 1.0 for crisis statements
    - _Requirements: 17.2, 17.7, 17.8, 17.9_

  - [x] 9.6.3 Implement weighted memory retrieval
    - Update `retrieve_similar()` to rank by similarity_score * Memory_Weight
    - Return top 3 highest-weighted relevant memories
    - _Requirements: 17.4, 17.5, 17.6, 17.10_

  - [x] 9.6.4 Write property tests for memory importance scoring
    - **Property 28: Memory Weight Range Constraint**
    - **Property 29: Weighted Memory Ranking**
    - **Validates: Requirements 17.1, 17.4**
    - Test weight assignment and weighted ranking logic

- [ ] 9.7 Implement Attachment Style Engine
  - [x] 9.7.1 Create Attachment Style Engine module
    - Create `backend/modules/attachment_style_engine.py` with AttachmentStyleEngine class
    - Define attachment state thresholds: avoidant (0-30), anxious (31-59), secure (60-79), possessive (80-100)
    - Implement `determine_attachment_state(affection_level)` method
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_

  - [x] 9.7.2 Integrate attachment state into Relationship Engine
    - Update `backend/modules/relationship_engine.py` to call AttachmentStyleEngine
    - Update attachment_state in `update_relationship()` method
    - Persist attachment_state to Firestore
    - _Requirements: 18.7, 18.14_

  - [x] 9.7.3 Update Personality System with attachment behaviors
    - Modify `backend/modules/personality_system.py` to inject attachment_state into prompts
    - Define behavioral instructions for each attachment state
    - Add intensified possessive responses when attachment_state is "possessive" and jealousy is detected
    - _Requirements: 18.8, 18.9, 18.10, 18.11, 18.12, 18.13_

  - [x] 9.7.4 Write property test for attachment state mapping
    - **Property 30: Attachment State Mapping**
    - **Validates: Requirements 18.3, 18.4, 18.5, 18.6**
    - Test correct attachment state assignment for all affection levels

- [ ] 9.8 Implement Temperature Scaling System
  - [x] 9.8.1 Create Temperature Scaling System module
    - Create `backend/modules/temperature_scaling_system.py` with TemperatureScalingSystem class
    - Define mood_temperature_map: angry=0.3, sad=0.4, neutral=0.5, happy=0.7, jealous=0.8, flustered=0.9
    - Implement `get_temperature(mood)` method
    - _Requirements: 19.1, 19.2_

  - [x] 9.8.2 Update LLM Service to accept temperature parameter
    - Modify `backend/modules/llm_service.py` to accept temperature in `generate_response()`
    - Pass temperature to HuggingFace API request
    - Log temperature value used for each generation
    - _Requirements: 19.3, 19.10, 19.11_

  - [x] 9.8.3 Write property test for temperature mapping
    - **Property 31: Mood-Based Temperature Mapping**
    - **Validates: Requirements 19.4, 19.5, 19.6, 19.7, 19.8, 19.9**
    - Test correct temperature assignment for all mood values

- [ ] 9.9 Implement Interaction Streak System
  - [x] 9.9.1 Create Interaction Streak System module
    - Create `backend/modules/interaction_streak_system.py` with InteractionStreakSystem class
    - Implement `calculate_streak(last_chat_date, current_date, current_streak)` method
    - Return new streak value and streak_broken flag
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

  - [x] 9.9.2 Implement streak break penalty logic
    - Implement `apply_streak_penalty(user_id, user_data)` method
    - Decrease affection_level by 3 points when streak is broken
    - Ensure affection_level never drops below 0
    - Set mood to "sad" when streak is broken
    - Update last_chat_date to current date
    - _Requirements: 20.7, 20.8, 20.9, 20.13_

  - [x] 9.9.3 Update Personality System with streak context
    - Modify `construct_prompt()` to inject streak information for streaks >= 7 days
    - Add behavioral instructions for expressing hurt feelings when streak is broken
    - _Requirements: 20.11, 20.12_

  - [x] 9.9.4 Write property tests for interaction streak system
    - **Property 32: Interaction Streak Update Logic**
    - **Property 33: Streak Break Affection Penalty**
    - **Validates: Requirements 20.4, 20.5, 20.6, 20.7, 20.13**
    - Test streak calculation and penalty application

- [ ] 9.10 Implement Callback Memory System
  - [x] 9.10.1 Create Callback Memory System module
    - Create `backend/modules/callback_memory_system.py` with CallbackMemorySystem class
    - Implement `calculate_recall_probability(affection_level)` method returning affection_level / 100
    - Implement `should_trigger_callback(affection_level)` method with probabilistic logic
    - _Requirements: 21.1, 21.2, 21.3, 21.8_

  - [x] 9.10.2 Implement memory callback selection
    - Implement `select_callback_memory(long_term_memory)` method
    - Filter memories with Memory_Weight > 0.7
    - Randomly select one high-weight memory
    - Format with phrasing like "Last time you said..." or "I remember when you told me..."
    - _Requirements: 21.4, 21.5, 21.6_

  - [x] 9.10.3 Integrate callback system into Response Pipeline
    - Update `backend/modules/response_pipeline.py` to call CallbackMemorySystem
    - Trigger callback before prompt construction
    - Limit callbacks to once per conversation
    - Suppress callbacks when affection_level < 30
    - Inject selected callback into prompt context
    - _Requirements: 21.7, 21.8, 21.9, 21.10_

  - [x] 9.10.4 Write property tests for callback memory system
    - **Property 34: Callback Probability Calculation**
    - **Property 35: High-Weight Memory Selection for Callbacks**
    - **Property 36: Callback Suppression at Low Affection**
    - **Validates: Requirements 21.2, 21.4, 21.6, 21.8**
    - Test probability calculation, memory selection, and suppression logic

- [x] 9.11 Checkpoint - Verify advanced systems integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement LLM Service
  - [x] 10.1 Create LLM Service module
    - Create `backend/modules/llm_service.py` with LLMService class
    - Initialize with HuggingFace API token
    - Set model to google/flan-t5-large
    - Define fallback_responses list with tsundere messages
    - _Requirements: 13.1, 13.2, 13.5_

  - [x] 10.2 Implement text generation
    - Implement `generate_response(prompt, max_length)` method
    - Make POST request to HuggingFace Inference API
    - Handle retries and timeouts
    - _Requirements: 13.3_

  - [x] 10.3 Implement fallback response handling
    - Implement `get_fallback_response()` method
    - Return random fallback on API errors
    - _Requirements: 13.4, 15.4_

  - [x] 10.4 Write unit tests for LLM Service
    - Test API call with mocked responses
    - Test fallback on API errors
    - Test retry logic

- [ ] 11. Implement Response Pipeline
  - [x] 11.1 Create Response Pipeline module
    - Create `backend/modules/response_pipeline.py` with ResponsePipeline class
    - Initialize with all processing modules
    - Create session_contexts dictionary for in-memory context storage
    - _Requirements: 11.1, 14.1_

  - [x] 11.2 Implement user data retrieval
    - Implement `get_or_create_user(user_id)` method
    - Retrieve from Firestore or create with defaults
    - _Requirements: 11.1_

  - [x] 11.3 Implement session context management
    - Implement `update_session_context(user_id, message)` method
    - Keep last 10 messages (5 exchanges)
    - Implement `clear_inactive_sessions()` method with 30-minute timeout
    - _Requirements: 14.1, 14.2, 14.3_

  - [x] 11.4 Implement memory importance heuristic with weight assignment
    - Implement `is_important_memory(message, emotion_result)` method
    - Check for emotional content, personal information keywords, or long messages
    - Call Memory Engine's `calculate_memory_weight()` to assign weight
    - Return tuple of (is_important, weight)
    - _Requirements: 8.2, 8.3, 8.4, 17.2_

  - [x] 11.5 Implement complete message processing pipeline
    - Implement `process_message(user_id, message, platform)` async method
    - Step 1: Retrieve user data from Firestore
    - Step 2: Apply affection decay based on time since last_interaction
    - Step 3: Update interaction streak and apply penalties if broken
    - Step 4: Detect emotions and update mood
    - Step 5: Query similar memories from Memory Engine with weighted ranking
    - Step 6: Determine if callback memory should be triggered
    - Step 7: Get recent session context
    - Step 8: Construct prompt with Personality System including attachment_state and callback memory
    - Step 9: Get temperature from Temperature Scaling System based on mood
    - Step 10: Generate LLM response with mood-based temperature
    - Step 11: Update relationship state and attachment_state
    - Step 12: Store new memory with importance weight if important
    - Step 13: Update session context
    - Step 14: Return ChatResponse
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 16.6, 17.10, 18.7, 19.3, 20.10, 21.10_

  - [x] 11.6 Write property test for response structure
    - **Property 2: Response Structure Completeness**
    - **Validates: Requirements 1.3**
    - Test that all responses contain reply, affection_level, and mood

  - [x] 11.7 Write integration tests for pipeline
    - Test complete pipeline execution with mocked services
    - Test error handling at each step
    - Test session context updates

- [ ] 12. Implement error handling and graceful degradation
  - [x] 12.1 Create custom exception classes
    - Create `backend/exceptions.py` with AIWaifuException, FirestoreConnectionError, LLMServiceError, MemoryEngineError, EmotionEngineError
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 12.2 Add error handling to Response Pipeline
    - Wrap Firestore calls with try-except, use in-memory defaults on failure
    - Wrap Memory Engine calls with try-except, skip vector retrieval on failure
    - Wrap Emotion Engine calls with try-except, use neutral mood on failure
    - Wrap LLM Service calls with try-except, use fallback response on failure
    - Wrap Personality System calls with try-except, use minimal default on failure
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 12.3 Implement structured logging
    - Add logging configuration to `config.py`
    - Add log statements at critical points: user retrieval, emotion detection, memory operations, relationship updates, LLM calls, errors
    - _Requirements: 15.6_

  - [x] 12.4 Write property test for graceful error responses
    - **Property 25: Graceful Error Response Format**
    - **Validates: Requirements 15.7**
    - Test that errors return HTTP 200 with error message in reply field

- [x] 13. Checkpoint - Verify complete backend functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Wire backend components together
  - [ ] 14.1 Create service container
    - Create `backend/container.py` with ServiceContainer class
    - Initialize all modules with dependency injection: Memory Engine, Emotion Engine, Personality System, Relationship Engine, LLM Service, Affection Decay Engine, Attachment Style Engine, Temperature Scaling System, Interaction Streak System, Callback Memory System
    - _Requirements: 12.5_

  - [ ] 14.2 Complete FastAPI main application
    - Update `backend/main.py` to use ServiceContainer
    - Implement POST /chat endpoint with ResponsePipeline
    - Implement GET /health endpoint with service checks
    - Add startup event to initialize services
    - Add background task for session cleanup
    - _Requirements: 1.1, 1.6, 11.1_

  - [ ] 14.3 Write end-to-end integration tests
    - Test new user first interaction
    - Test jealousy trigger flow
    - Test affection progression and stage transition
    - Test cross-platform consistency (same user_id, different platforms)
    - Test affection decay after extended absence
    - Test interaction streak tracking and break penalties
    - Test attachment state transitions across affection levels
    - Test temperature scaling effects on response generation
    - Test callback memory injection at high affection levels
    - Test weighted memory retrieval prioritization
    - _Requirements: 1.4, 1.5, 10.3, 10.4, 10.5, 16.5, 17.4, 18.7, 19.3, 20.10, 21.10_

  - [ ] 14.4 Write property test for cross-platform consistency
    - **Property 12: Cross-Platform Personality Consistency**
    - **Property 23: Cross-Platform Identity Consistency**
    - **Validates: Requirements 4.11, 10.3, 10.4, 10.5**
    - Test that same user_id retrieves same state across platforms

- [ ] 15. Implement Angular web client
  - [ ] 15.1 Create chat service
    - Create `web-client/src/app/services/chat.service.ts`
    - Implement `sendMessage(userId, message)` method with HttpClient
    - Set platform to "web"
    - _Requirements: 7.4_

  - [ ] 15.2 Create chat component
    - Create `web-client/src/app/components/chat/chat.component.ts`
    - Implement message history array
    - Implement send message functionality
    - Display reply, mood, and affection_level
    - _Requirements: 7.3, 7.5_

  - [ ] 15.3 Create affection meter component
    - Create `web-client/src/app/components/affection-meter/affection-meter.component.ts`
    - Visualize affection_level as progress bar or heart meter
    - _Requirements: 7.6_

  - [ ] 15.4 Style chat interface with TailwindCSS
    - Apply TailwindCSS classes for modern chat UI
    - Style message bubbles, input field, affection meter
    - Add responsive design
    - _Requirements: 7.2_

  - [ ] 15.5 Write unit tests for web client components
    - Test chat service HTTP calls
    - Test chat component message handling
    - Test affection meter rendering

- [ ] 16. Implement Discord bot client
  - [ ] 16.1 Create Discord bot main file
    - Implement `discord-bot/discord_bot.py` with WaifuBot class
    - Initialize discord.py bot with intents
    - Load Discord bot token from environment
    - _Requirements: 6.1, 9.3_

  - [ ] 16.2 Implement message handling
    - Implement `on_message` event handler
    - Capture message content and author ID
    - Send POST request to AI_Brain with platform="discord"
    - Reply in Discord channel with response
    - _Requirements: 6.2, 6.3, 6.4_

  - [ ] 16.3 Write integration tests for Discord bot
    - Test message capture and API call
    - Test response handling
    - Use mocked Discord client

- [ ] 17. Checkpoint - Verify client integrations
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Create deployment configuration
  - [ ] 18.1 Create Dockerfile for backend
    - Create `backend/Dockerfile`
    - Use Python 3.10-slim base image
    - Install dependencies from requirements.txt
    - Create faiss_indices directory
    - Expose port 8000
    - Set CMD to run uvicorn
    - _Requirements: 9.1_

  - [ ] 18.2 Create environment configuration documentation
    - Create `backend/README.md` with setup instructions
    - Document required environment variables
    - Document Firebase credentials setup
    - Document HuggingFace API token setup
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 18.3 Create Angular build configuration
    - Update `web-client/angular.json` for production builds
    - Configure environment files for production API URL
    - _Requirements: 7.1_

  - [ ] 18.4 Create Discord bot deployment instructions
    - Create `discord-bot/README.md` with setup instructions
    - Document Discord bot token setup
    - Document API URL configuration
    - _Requirements: 6.1, 9.3_

- [ ] 19. Run comprehensive property-based test suite
  - [ ] 19.1 Execute all property tests
    - Run pytest with property test markers
    - Verify all 36 correctness properties pass (Properties 1-36)
    - Generate test coverage report
    - _Requirements: All requirements validated by properties_

  - [ ] 19.2 Run performance tests
    - Test concurrent requests
    - Test large FAISS index queries
    - Test long conversation histories
    - Verify response times meet targets

- [ ] 20. Final checkpoint - Complete system verification
  - Ensure all tests pass, verify deployment readiness, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties across randomized inputs (36 total properties)
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: data models → core modules → advanced systems → pipeline → clients
- All backend code uses Python 3.10+ with type hints
- All web client code uses TypeScript with Angular 17+ standalone components
- Testing uses pytest for backend and Jasmine/Karma for Angular frontend
- Advanced systems (Requirements 16-21) add emotional depth through decay, memory importance, attachment styles, temperature scaling, interaction streaks, and callback memories
