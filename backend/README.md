# AI Waifu Cross-Platform System - Backend

The AI_Brain backend is the centralized FastAPI service that powers Mimi, a tsundere anime girl character with persistent memory and emotional intelligence. This backend serves as the single source of truth for AI personality, memory, and relationship state across all client platforms (web app and Discord bot).

## Features

- **Persistent Memory**: Firestore database stores user relationships, affection levels, and long-term memories
- **Semantic Memory**: FAISS vector similarity search for contextual conversation recall
- **Emotional Intelligence**: Mood detection, jealousy triggers, and affection decay system
- **Relationship Progression**: Dynamic affection levels, trust building, and relationship stages
- **Attachment Styles**: Behavioral patterns evolve from avoidant to possessive based on affection
- **Interaction Streaks**: Daily consistency tracking with penalties for broken streaks
- **Memory Importance Scoring**: Weighted memory retrieval prioritizes emotionally significant moments
- **Temperature Scaling**: Mood-based response randomness (chaotic when flustered, controlled when angry)
- **Callback Memory System**: Self-initiated references to past conversations at high affection levels
- **Cross-Platform Consistency**: Same personality and memory across web and Discord clients

## Prerequisites

- Python 3.10 or higher
- Firebase project with Firestore enabled
- HuggingFace API token (free tier available)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Firebase Configuration

#### Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Firestore Database:
   - Go to "Firestore Database" in the left menu
   - Click "Create database"
   - Choose "Start in production mode" or "Start in test mode"
   - Select a location for your database

#### Generate Service Account Credentials

1. In Firebase Console, go to Project Settings (gear icon)
2. Navigate to "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file securely (e.g., `firebase-credentials.json`)
5. **IMPORTANT**: Never commit this file to version control!

#### Configure Firebase Path

Place your Firebase credentials JSON file in a secure location and note the path. You'll reference this in the environment variables.

### 3. HuggingFace API Token

#### Get API Token

1. Create a free account at [HuggingFace](https://huggingface.co/)
2. Go to Settings → Access Tokens
3. Click "New token"
4. Give it a name (e.g., "ai-waifu-backend")
5. Select "Read" permissions
6. Copy the generated token

### 4. Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# HuggingFace API Configuration
HUGGINGFACE_API_TOKEN=hf_your_actual_token_here

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json

# Application Configuration (optional, defaults provided)
SESSION_TIMEOUT_MINUTES=30
MEMORY_RETRIEVAL_COUNT=3
CONTEXT_WINDOW_SIZE=5

# Logging Configuration
LOG_LEVEL=INFO
```

### 5. Run the Backend

#### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-restart on code changes.

#### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "firestore": "connected",
    "memory_engine": "ready",
    "llm_service": "ready"
  }
}
```

## Docker Deployment

### Build Docker Image

```bash
cd backend
docker build -t ai-waifu-backend .
```

### Run Docker Container

```bash
docker run -d \
  --name ai-waifu-backend \
  -p 8000:8000 \
  -e HUGGINGFACE_API_TOKEN=your_token_here \
  -e FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json \
  -v /path/to/firebase-credentials.json:/app/config/firebase-credentials.json:ro \
  -v $(pwd)/faiss_indices:/app/faiss_indices \
  ai-waifu-backend
```

**Important**: Mount your Firebase credentials file as a read-only volume.

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - HUGGINGFACE_API_TOKEN=${HUGGINGFACE_API_TOKEN}
      - FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json
      - LOG_LEVEL=INFO
    volumes:
      - ./firebase-credentials.json:/app/config/firebase-credentials.json:ro
      - ./faiss_indices:/app/faiss_indices
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## API Documentation

### Endpoints

#### POST /chat

Send a message to Mimi and receive a response.

**Request Body:**
```json
{
  "user_id": "user123",
  "message": "Hey Mimi!",
  "platform": "web"
}
```

**Response:**
```json
{
  "reply": "H-hey! What do you want?",
  "affection_level": 25,
  "mood": "neutral"
}
```

**Fields:**
- `user_id` (string, required): Unique identifier for the user (consistent across platforms)
- `message` (string, required): User's message text
- `platform` (string, required): Either "web" or "discord"

#### GET /health

Check backend service health.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "firestore": "connected",
    "memory_engine": "ready",
    "llm_service": "ready"
  }
}
```

### Interactive API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `HUGGINGFACE_API_TOKEN` | HuggingFace API authentication token | Yes | None |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON file | Yes | None |
| `SESSION_TIMEOUT_MINUTES` | Session context expiration time | No | 30 |
| `MEMORY_RETRIEVAL_COUNT` | Number of similar memories to retrieve | No | 3 |
| `CONTEXT_WINDOW_SIZE` | Number of recent message exchanges to include | No | 5 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | No | INFO |

## Architecture

### Core Modules

- **Memory Engine** (`modules/memory_engine.py`): FAISS vector similarity search with sentence transformers
- **Emotion Engine** (`modules/emotion_engine.py`): Emotional keyword detection and jealousy triggers
- **Personality System** (`modules/personality_system.py`): Character definition and prompt construction
- **Relationship Engine** (`modules/relationship_engine.py`): Affection, trust, and relationship stage management
- **LLM Service** (`modules/llm_service.py`): HuggingFace Inference API integration

### Advanced Systems

- **Affection Decay Engine** (`modules/affection_decay_engine.py`): Time-based emotional decay
- **Attachment Style Engine** (`modules/attachment_style_engine.py`): Behavioral pattern evolution
- **Temperature Scaling System** (`modules/temperature_scaling_system.py`): Mood-based response randomness
- **Interaction Streak System** (`modules/interaction_streak_system.py`): Daily consistency tracking
- **Callback Memory System** (`modules/callback_memory_system.py`): Self-initiated memory references

### Data Flow

```
Client Request → Response Pipeline → Affection Decay → Interaction Streak
→ Emotion Detection → Relationship Update → Memory Retrieval
→ Callback Memory Check → Prompt Construction → Temperature Scaling
→ LLM Generation → Memory Storage → Response
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Property-Based Tests

```bash
pytest -m property
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Test Categories

- **Property Tests**: Universal correctness properties validated across randomized inputs (36 properties)
- **Unit Tests**: Specific examples and edge cases
- **Integration Tests**: End-to-end pipeline validation

## Troubleshooting

### "Firebase credentials not found" error

- Verify `FIREBASE_CREDENTIALS_PATH` points to the correct JSON file
- Check file permissions (must be readable by the application)
- Ensure the path is absolute or relative to the backend directory

### "HuggingFace API error" or slow responses

- Verify your `HUGGINGFACE_API_TOKEN` is valid
- HuggingFace Inference API may have cold start delays (first request can take 20-30 seconds)
- Check your HuggingFace account quota and rate limits
- Consider upgrading to HuggingFace Pro for faster inference

### "FAISS index not found" warnings

- This is normal for new users - indices are created on first interaction
- The `faiss_indices/` directory will be populated automatically
- Ensure the application has write permissions to this directory

### Memory/Performance Issues

- FAISS indices grow with usage - monitor disk space
- Consider implementing index cleanup for inactive users
- Increase Docker memory limits if running in containers
- Use `--workers` parameter with uvicorn for production load

### Firestore Connection Issues

- Verify your Firebase project has Firestore enabled
- Check that the service account has Firestore permissions
- Ensure your network allows connections to Firebase (check firewall/proxy)
- Review Firebase Console for any project-level issues

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── container.py            # Dependency injection container
├── models.py               # Pydantic data models
├── exceptions.py           # Custom exception classes
├── config.py               # Configuration management
├── waifu_personality.txt   # Mimi's character definition
├── modules/
│   ├── memory_engine.py
│   ├── emotion_engine.py
│   ├── personality_system.py
│   ├── relationship_engine.py
│   ├── llm_service.py
│   ├── affection_decay_engine.py
│   ├── attachment_style_engine.py
│   ├── temperature_scaling_system.py
│   ├── interaction_streak_system.py
│   ├── callback_memory_system.py
│   ├── response_pipeline.py
│   └── firestore_operations.py
├── tests/                  # Test suite
├── faiss_indices/          # Vector database storage
└── requirements.txt        # Python dependencies
```

### Adding New Features

The system uses a modular architecture with dependency injection. To add new features:

1. Create a new module in `modules/`
2. Register it in `container.py`
3. Inject it into `ResponsePipeline` if needed
4. Add corresponding tests

### Modifying Personality

Edit `waifu_personality.txt` to adjust Mimi's character traits, speech patterns, and behavioral guidelines. Changes take effect on next application restart.

## Requirements Validation

This implementation satisfies:
- **Requirement 1**: Centralized AI Backend with REST API
- **Requirement 2**: Persistent Memory Storage with Firestore
- **Requirement 3**: Vector Similarity Memory with FAISS
- **Requirement 4**: Personality System with character definition
- **Requirement 5**: Relationship Progression Engine
- **Requirement 5.1**: Emotion Detection Engine
- **Requirement 8**: Memory Update Logic
- **Requirement 9**: Environment Configuration
- **Requirement 11**: Response Generation Pipeline
- **Requirement 13**: LLM Service Integration
- **Requirement 14**: Conversation Context Management
- **Requirement 15**: Error Handling and Fallback Responses
- **Requirement 16**: Emotional Decay System
- **Requirement 17**: Memory Importance Scoring
- **Requirement 18**: Attachment Style Engine
- **Requirement 19**: Response Temperature Scaling
- **Requirement 20**: Interaction Streak System
- **Requirement 21**: Self-Initiated Callback Memory

## License

Part of the AI Waifu Cross-Platform System.

## Support

For issues, questions, or contributions, please refer to the main project repository.
