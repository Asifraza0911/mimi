# 🎯 Getting Started - Complete Guide

Welcome! This guide will help you set up the AI Waifu Cross-Platform System.

---

## 📚 Documentation Overview

We have several guides to help you:

| Guide | Purpose | Time | Best For |
|-------|---------|------|----------|
| **[WHERE_TO_FIND_CREDENTIALS.md](WHERE_TO_FIND_CREDENTIALS.md)** | Visual guide to getting credentials | 10 min | First-time setup |
| **[QUICK_START.md](QUICK_START.md)** | Fast setup instructions | 10 min | Experienced users |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Detailed step-by-step guide | 20 min | Comprehensive setup |
| **[CREDENTIALS_CHECKLIST.md](CREDENTIALS_CHECKLIST.md)** | Track your progress | - | Staying organized |
| **[TROUBLESHOOTING_CREDENTIALS.md](TROUBLESHOOTING_CREDENTIALS.md)** | Fix common issues | - | When things go wrong |
| **[README.md](README.md)** | Project overview | - | Understanding the system |

---

## 🚀 Recommended Path

### For First-Time Users:

1. **Start Here:** [WHERE_TO_FIND_CREDENTIALS.md](WHERE_TO_FIND_CREDENTIALS.md)
   - Shows exactly where to get each credential
   - Visual step-by-step instructions
   - Explains what each credential does

2. **Then Follow:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
   - Comprehensive setup instructions
   - Detailed configuration steps
   - Testing and verification

3. **Track Progress:** [CREDENTIALS_CHECKLIST.md](CREDENTIALS_CHECKLIST.md)
   - Check off items as you complete them
   - Ensure nothing is missed
   - Quick status overview

4. **If Issues:** [TROUBLESHOOTING_CREDENTIALS.md](TROUBLESHOOTING_CREDENTIALS.md)
   - Common problems and solutions
   - Debugging tips
   - Quick fixes

### For Experienced Users:

1. **Quick Setup:** [QUICK_START.md](QUICK_START.md)
   - Fast-track instructions
   - Minimal explanations
   - Get running in 10 minutes

---

## 🎯 What You'll Build

By the end of setup, you'll have:

- ✅ **Backend API** - Centralized AI brain running on port 8000
- ✅ **Web Client** - Chat interface running on port 4200
- ✅ **Discord Bot** (Optional) - Discord integration
- ✅ **Persistent Memory** - Firestore database storing relationships
- ✅ **Semantic Memory** - FAISS vector search for context
- ✅ **Emotional AI** - Mimi with personality and memory

---

## 📋 Prerequisites

Before starting, ensure you have:

### Software
- [ ] Python 3.10 or higher
- [ ] Node.js 18 or higher
- [ ] Git
- [ ] Text editor (VS Code, Sublime, etc.)

### Accounts (All FREE)
- [ ] Google account (for Firebase)
- [ ] HuggingFace account
- [ ] Discord account (optional, for bot)

### Time
- [ ] 10-20 minutes for setup
- [ ] Stable internet connection

---

## 🔑 Credentials You'll Need

### Required (FREE):

1. **HuggingFace API Token**
   - Get from: https://huggingface.co/settings/tokens
   - Time: 2 minutes
   - Cost: FREE
   - Used for: AI responses

2. **Firebase Credentials**
   - Get from: https://console.firebase.google.com/
   - Time: 5 minutes
   - Cost: FREE (generous limits)
   - Used for: Persistent storage

### Optional (FREE):

3. **Discord Bot Token**
   - Get from: https://discord.com/developers/applications
   - Time: 3 minutes
   - Cost: FREE
   - Used for: Discord integration

---

## 🎬 Quick Start (10 Minutes)

### 1. Get Credentials (7 minutes)

Follow [WHERE_TO_FIND_CREDENTIALS.md](WHERE_TO_FIND_CREDENTIALS.md) to get:
- HuggingFace token
- Firebase credentials JSON
- Discord token (optional)

### 2. Configure Backend (2 minutes)

```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Start Web Client (1 minute)

```bash
cd web-client
npm install
ng serve
```

### 4. Test (30 seconds)

- Backend: http://localhost:8000/health
- Web: http://localhost:4200
- Send a message to Mimi!

---

## 🗺️ Setup Roadmap

```
Start
  │
  ├─→ Get HuggingFace Token (2 min)
  │
  ├─→ Get Firebase Credentials (5 min)
  │
  ├─→ Configure Backend (2 min)
  │   ├─ Create .env
  │   ├─ Install dependencies
  │   └─ Start backend
  │
  ├─→ Configure Web Client (1 min)
  │   ├─ Install dependencies
  │   └─ Start dev server
  │
  └─→ [Optional] Setup Discord Bot (3 min)
      ├─ Get Discord token
      ├─ Configure .env
      └─ Start bot
  
Done! 🎉
```

---

## 📁 File Structure After Setup

```
ai-waifu-system/
├── firebase-credentials.json    # ⚠️ Your Firebase key (NEVER commit!)
│
├── backend/
│   ├── .env                     # ⚠️ Your credentials (NEVER commit!)
│   ├── .env.example             # ✅ Template (safe to commit)
│   └── faiss_indices/           # Created automatically
│
├── web-client/
│   └── src/environments/
│       ├── environment.ts       # Development config
│       └── environment.prod.ts  # Production config
│
└── discord-bot/
    ├── .env                     # ⚠️ Your Discord token (NEVER commit!)
    └── .env.example             # ✅ Template (safe to commit)
```

---

## ✅ Verification Steps

After setup, verify everything works:

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", ...}`

### 2. Test Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hello!", "platform": "web"}'
```
Expected: JSON with `reply`, `affection_level`, `mood`

### 3. Web Client
- Open http://localhost:4200
- Type a message
- Receive response from Mimi

### 4. Discord Bot (if configured)
- Send message in Discord
- Bot responds

---

## 🎯 Success Criteria

You're ready when:

- [ ] Backend returns "healthy" status
- [ ] Web client loads without errors
- [ ] Can send message and get response
- [ ] Mimi's personality shows through
- [ ] (Optional) Discord bot responds

---

## 🆘 Common Issues

### "Can't find credentials"
→ See [TROUBLESHOOTING_CREDENTIALS.md](TROUBLESHOOTING_CREDENTIALS.md)

### "First response takes 30 seconds"
→ Normal! HuggingFace model cold start. Next responses are faster.

### "Backend won't start"
→ Check .env file has correct credentials

### "Web client can't connect"
→ Verify backend is running on port 8000

---

## 📖 Next Steps After Setup

### Learn the System
1. Read [README.md](README.md) for architecture overview
2. Check component READMEs for details:
   - [backend/README.md](backend/README.md)
   - [web-client/README.md](web-client/README.md)
   - [discord-bot/README.md](discord-bot/README.md)

### Start Chatting
1. Send messages to Mimi
2. Watch affection levels increase
3. Build daily interaction streaks
4. Experience personality evolution

### Customize
1. Edit `backend/waifu_personality.txt` for different personality
2. Adjust affection decay rates
3. Modify emotional triggers
4. Add new features

---

## 💡 Tips for Success

### During Setup:
- Follow guides in order
- Don't skip verification steps
- Keep credentials secure
- Use checklist to track progress

### After Setup:
- Be consistent - daily interactions build relationships
- Emotional messages are remembered better
- High affection unlocks new behaviors
- Streaks affect Mimi's responses

---

## 🎉 Ready to Begin?

Choose your path:

**New to this?**
→ Start with [WHERE_TO_FIND_CREDENTIALS.md](WHERE_TO_FIND_CREDENTIALS.md)

**Want speed?**
→ Jump to [QUICK_START.md](QUICK_START.md)

**Need details?**
→ Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Having issues?**
→ Check [TROUBLESHOOTING_CREDENTIALS.md](TROUBLESHOOTING_CREDENTIALS.md)

---

## 📞 Support

If you get stuck:

1. Check the troubleshooting guide
2. Review component READMEs
3. Verify all prerequisites
4. Ensure credentials are correct
5. Try regenerating credentials

---

**Let's get started! 🚀**

Choose your guide above and begin your journey with Mimi! 💕
