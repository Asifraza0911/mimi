# AI MIMI Cross-Platform System

A conversational AI system featuring Mimi, a tsundere anime girl character with persistent memory, emotional intelligence, and relationship progression. The system provides a unified personality and memory experience across multiple platforms (web and Discord).

## 🌟 Features

### Core Capabilities
- **Persistent Memory**: Long-term relationship and conversation history stored in Firestore
- **Semantic Memory**: FAISS vector similarity search for contextual conversation recall
- **Emotional Intelligence**: Mood detection, jealousy triggers, and emotional responses
- **Relationship Progression**: Dynamic affection levels with trust building and relationship stages
- **Cross-Platform Consistency**: Same personality and memory across web and Discord

### Advanced Systems
- **Attachment Styles**: Behavioral patterns evolve from avoidant → anxious → secure → possessive
- **Interaction Streaks**: Daily consistency tracking with emotional reactions to broken streaks
- **Memory Importance Scoring**: Weighted retrieval prioritizes emotionally significant moments
- **Temperature Scaling**: Mood-based response randomness (chaotic when flustered, controlled when angry)
- **Callback Memory**: Self-initiated references to past conversations at high affection levels
- **Affection Decay**: Time-based emotional cooling with accelerated decay during absence

### Dual-Model LLM Architecture
- **Thinking Brain** (Qwen/Qwen3.5-397B-A17B): Emotional analysis and reasoning
- **Personality Brain** (Qwen/Qwen2.5-7B-Instruct): Natural dialogue generation with tsundere personality

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
- [Deployment](#deployment)
- [Testing](#testing)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Platforms                         │
├──────────────────────┬──────────────────────────────────────┤
│   Web Client         │        Discord Bot                   │
│   (Angular 19)       │        (discord.py)                  │
└──────────┬───────────┴──────────────┬───────────────────────┘
           │                          │
           │    HTTP POST /chat       │
           └──────────┬───────────────┘
                      │
           ┌──────────▼──────────┐
           │   AI_Brain Backend  │
           │   (FastAPI)         │
           └──────────┬──────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐   ┌───▼────┐   ┌───▼────┐
   │Firestore│   │ FAISS  │   │HuggingF│
   │Database │   │Vectors │   │ace API │
   └─────────┘   └────────┘   └────────┘
```

### Data Flow

```
User Message → Response Pipeline → Affection Decay → Interaction Streak
→ Emotion Detection → Relationship Update → Memory Retrieval
→ Callback Memory Check → Prompt Construction → Temperature Scaling
→ LLM Generation → Memory Storage → Response
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (for backend and Discord bot)
- **Node.js 18+** (for web client)
- **Firebase Project** with Firestore enabled
- **HuggingFace API Token** (free tier available)
- **Discord Bot Token** (if using Discord)

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-waifu-system
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Firebase credentials and HuggingFace token

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`

See [backend/README.md](backend/README.md) for detailed setup instructions.

### 3. Web Client Setup

```bash
cd web-client

# Install dependencies
npm install

# Configure environment
# Edit src/environments/environment.ts to point to your backend

# Run development server
ng serve
```

**Web client will be available at:** `http://localhost:4200`

### 4. Discord Bot Setup (Optional)

```bash
cd discord-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Discord bot token and backend URL

# Run bot
python discord_bot.py
```

See [discord-bot/README.md](discord-bot/README.md) for detailed setup instructions.

## 📦 Components

### Backend (FastAPI)

The centralized AI brain that handles all personality, memory, and relationship logic.

**Key Features:**
- REST API with `/chat` and `/health` endpoints
- Dual-model LLM architecture for accurate emotion detection and natural responses
- FAISS vector database for semantic memory
- Firestore for persistent storage
- Comprehensive test suite (337 tests, 100% passing)

**Tech Stack:** FastAPI, FAISS, sentence-transformers, Firebase Admin SDK, requests

[📖 Backend Documentation](backend/README.md)

### Web Client (Angular 19)

Modern web interface for chatting with Mimi.

**Key Features:**
- Real-time chat interface with message history
- Affection meter visualization
- Responsive design with TailwindCSS
- TypeScript for type safety

**Tech Stack:** Angular 19, TailwindCSS, RxJS

[📖 Web Client Documentation](web-client/README.md)

### Discord Bot (discord.py)

Thin client that enables Discord interactions.

**Key Features:**
- Message forwarding to backend
- Status command for health checks
- Automatic user ID mapping
- Platform-specific tagging

**Tech Stack:** discord.py, requests

[📖 Discord Bot Documentation](discord-bot/README.md)

## 🐳 Deployment

### Docker Deployment

Each component includes a Dockerfile for containerized deployment.

#### Backend

```bash
cd backend
docker build -t ai-waifu-backend .
docker run -d \
  --name ai-waifu-backend \
  -p 8000:8000 \
  -e HUGGINGFACE_API_TOKEN=your_token \
  -e FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json \
  -v /path/to/firebase-credentials.json:/app/config/firebase-credentials.json:ro \
  -v $(pwd)/faiss_indices:/app/faiss_indices \
  ai-waifu-backend
```

#### Web Client

```bash
cd web-client
docker build -t ai-waifu-web .
docker run -d \
  --name ai-waifu-web \
  -p 80:80 \
  ai-waifu-web
```

#### Discord Bot

```bash
cd discord-bot
docker build -t ai-waifu-discord .
docker run -d \
  --name ai-waifu-discord \
  -e DISCORD_BOT_TOKEN=your_token \
  -e API_URL=http://backend:8000 \
  ai-waifu-discord
```

### Docker Compose (Recommended)

Create `docker-compose.yml` in the project root:

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
    volumes:
      - ./firebase-credentials.json:/app/config/firebase-credentials.json:ro
      - ./faiss_indices:/app/faiss_indices
    restart: unless-stopped

  web:
    build: ./web-client
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  discord-bot:
    build: ./discord-bot
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run property-based tests only
pytest -m property_test
```

**Test Results:** 337 tests passing (100% pass rate)

### Discord Bot Tests

```bash
cd discord-bot
pytest test_discord_bot.py
```

### Web Client Tests

```bash
cd web-client
ng test
```

## ⚙️ Configuration

### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `HUGGINGFACE_API_TOKEN` | HuggingFace API token | Yes | None |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase JSON | Yes | None |
| `SESSION_TIMEOUT_MINUTES` | Session expiration | No | 30 |
| `MEMORY_RETRIEVAL_COUNT` | Similar memories to retrieve | No | 3 |
| `CONTEXT_WINDOW_SIZE` | Recent messages to include | No | 5 |
| `LOG_LEVEL` | Logging level | No | INFO |

### Discord Bot Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token | Yes | None |
| `API_URL` | Backend URL | No | http://localhost:8000 |

### Web Client Configuration

Edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

For production, edit `src/environments/environment.prod.ts`.

## 💻 Development

### Project Structure

```
ai-waifu-system/
├── backend/                 # FastAPI backend
│   ├── modules/            # Core AI modules
│   ├── tests/              # Test suite
│   ├── main.py             # FastAPI app
│   ├── container.py        # Dependency injection
│   └── waifu_personality.txt
├── web-client/             # Angular web app
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   └── services/
│   │   └── environments/
│   └── angular.json
├── discord-bot/            # Discord bot
│   ├── discord_bot.py
│   └── test_discord_bot.py
└── README.md               # This file
```

### Adding New Features

1. **Backend Module**: Create in `backend/modules/`, register in `container.py`
2. **Web Component**: Use `ng generate component <name>` in web-client
3. **Discord Command**: Add `@bot.command()` decorator in `discord_bot.py`

### Modifying Personality

Edit `backend/waifu_personality.txt` to adjust Mimi's character traits, speech patterns, and behavioral guidelines. Changes take effect on application restart.

## 🔧 Troubleshooting

### Backend Issues

**"Firebase credentials not found"**
- Verify `FIREBASE_CREDENTIALS_PATH` is correct
- Check file permissions
- Ensure path is absolute or relative to backend directory

**"HuggingFace API error"**
- Verify `HUGGINGFACE_API_TOKEN` is valid
- First request may take 20-30 seconds (cold start)
- Check HuggingFace account quota

**"FAISS index not found"**
- Normal for new users - indices created on first interaction
- Ensure write permissions to `faiss_indices/` directory

### Web Client Issues

**"Cannot connect to backend"**
- Verify backend is running at configured URL
- Check CORS settings in backend
- Inspect browser console for errors

### Discord Bot Issues

**"Bot doesn't respond"**
- Enable Message Content Intent in Discord Developer Portal
- Verify bot has read/send message permissions
- Check backend is accessible at configured `API_URL`

**"Invalid token"**
- Verify `DISCORD_BOT_TOKEN` in `.env`
- Ensure you copied from "Bot" section, not Client ID

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB (for FAISS indices and logs)
- **Network**: Stable internet for HuggingFace API

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 20GB+ SSD
- **Network**: Low-latency connection

## 🎯 Requirements Validation

This implementation satisfies all 21 core requirements:

- ✅ **Req 1-5**: Centralized backend, persistent memory, vector similarity, personality system, relationship progression
- ✅ **Req 6-7**: Discord bot integration, web client interface
- ✅ **Req 8-10**: Memory updates, environment config, cross-platform consistency
- ✅ **Req 11-15**: Response pipeline, LLM integration, context management, error handling
- ✅ **Req 16-21**: Affection decay, memory importance, attachment styles, temperature scaling, interaction streaks, callback memory

## 📝 API Reference

### POST /chat

Send a message and receive a response.

**Request:**
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

### GET /health

Check system health.

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

**Interactive Documentation:** Visit `http://localhost:8000/docs` when backend is running.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the AI Waifu Cross-Platform System.

## 🙏 Acknowledgments

- **HuggingFace** for LLM inference API
- **Firebase** for Firestore database
- **FAISS** for vector similarity search
- **sentence-transformers** for embedding generation
- **FastAPI** for backend framework
- **Angular** for web framework
- **discord.py** for Discord integration

## 📞 Support

For issues, questions, or feature requests:
- Check component-specific READMEs for detailed documentation
- Review troubleshooting sections
- Open an issue in the repository

---

**Built with ❤️ for anime AI enthusiasts**
