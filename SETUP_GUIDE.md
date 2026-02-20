# 🚀 Complete Setup Guide - AI Waifu Cross-Platform System

This guide will walk you through obtaining all necessary credentials and configuring the system from scratch.

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed (for web client)
- [ ] Git installed
- [ ] A Google account (for Firebase)
- [ ] A Discord account (if using Discord bot)

## 🔑 Step 1: Get HuggingFace API Token (Required)

HuggingFace provides the LLM models for Mimi's responses.

### How to Get It:

1. **Create Account**
   - Go to https://huggingface.co/
   - Click "Sign Up" (top right)
   - Use email or GitHub to register
   - Verify your email

2. **Generate API Token**
   - Click your profile picture (top right)
   - Select "Settings"
   - Click "Access Tokens" in the left sidebar
   - Click "New token"
   - Name it: `ai-waifu-backend`
   - Select "Read" permissions
   - Click "Generate token"
   - **COPY THE TOKEN** - you won't see it again!

3. **Token Format**
   ```
   hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Cost:
- ✅ **FREE** - HuggingFace Inference API has a free tier
- Rate limits: ~1000 requests/day (sufficient for personal use)
- First request may take 20-30 seconds (model cold start)

---

## 🔥 Step 2: Setup Firebase (Required)

Firebase Firestore stores user relationships, affection levels, and long-term memories.

### How to Get It:

1. **Create Firebase Project**
   - Go to https://console.firebase.google.com/
   - Click "Add project"
   - Enter project name: `ai-waifu-system` (or your choice)
   - Disable Google Analytics (optional, not needed)
   - Click "Create project"
   - Wait for setup to complete (~30 seconds)

2. **Enable Firestore Database**
   - In your project, click "Firestore Database" in left menu
   - Click "Create database"
   - Choose "Start in test mode" (for development)
     - **Note**: For production, use production mode with security rules
   - Select a location (choose closest to you):
     - `us-central1` (Iowa)
     - `europe-west1` (Belgium)
     - `asia-southeast1` (Singapore)
   - Click "Enable"

3. **Generate Service Account Credentials**
   - Click the ⚙️ gear icon (top left) → "Project settings"
   - Go to "Service accounts" tab
   - Click "Generate new private key"
   - Click "Generate key" in the popup
   - A JSON file will download: `ai-waifu-system-xxxxx.json`
   - **IMPORTANT**: Keep this file secure! Never commit to Git!

4. **Save Credentials File**
   ```bash
   # Move the downloaded file to your project
   mv ~/Downloads/ai-waifu-system-xxxxx.json ./firebase-credentials.json
   
   # Make sure it's in .gitignore (already configured)
   ```

5. **Firestore Security Rules (Optional - for production)**
   - In Firestore console, go to "Rules" tab
   - Replace with:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /waifu_memory/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
     }
   }
   ```

### Cost:
- ✅ **FREE** - Firestore free tier includes:
  - 1 GB storage
  - 50,000 reads/day
  - 20,000 writes/day
  - 20,000 deletes/day
- More than enough for personal use!

---

## 🤖 Step 3: Setup Discord Bot (Optional)

Only needed if you want Discord integration.

### How to Get It:

1. **Create Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Name it: `Mimi AI Waifu` (or your choice)
   - Accept Terms of Service
   - Click "Create"

2. **Create Bot User**
   - In your application, click "Bot" in left sidebar
   - Click "Add Bot"
   - Click "Yes, do it!"
   - Under "Privileged Gateway Intents", enable:
     - ✅ Message Content Intent (REQUIRED)
   - Click "Save Changes"

3. **Get Bot Token**
   - Still in "Bot" section
   - Under "TOKEN", click "Reset Token"
   - Click "Yes, do it!"
   - **COPY THE TOKEN** - you won't see it again!
   - Token format: `MTxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx`

4. **Invite Bot to Your Server**
   - Click "OAuth2" → "URL Generator" in left sidebar
   - Under "SCOPES", check:
     - ✅ `bot`
   - Under "BOT PERMISSIONS", check:
     - ✅ Read Messages/View Channels
     - ✅ Send Messages
     - ✅ Read Message History
   - Copy the generated URL at the bottom
   - Open URL in browser
   - Select your Discord server
   - Click "Authorize"

### Cost:
- ✅ **FREE** - Discord bots are completely free

---

## ⚙️ Step 4: Configure Backend

Now let's set up the backend with your credentials.

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Create .env File**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env File**
   Open `backend/.env` in your text editor and fill in:

   ```env
   # HuggingFace API Configuration
   HUGGINGFACE_API_TOKEN=hf_your_actual_token_here
   
   # Firebase Configuration
   FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
   
   # Application Configuration (defaults are fine)
   SESSION_TIMEOUT_MINUTES=30
   MEMORY_RETRIEVAL_COUNT=3
   CONTEXT_WINDOW_SIZE=5
   
   # Logging Configuration
   LOG_LEVEL=INFO
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Test Backend**
   ```bash
   uvicorn main:app --reload
   ```
   
   You should see:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete.
   ```

6. **Verify Health**
   Open browser to: http://localhost:8000/health
   
   Should see:
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

---

## 🌐 Step 5: Configure Web Client

1. **Navigate to Web Client Directory**
   ```bash
   cd ../web-client
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment (Development)**
   The file `src/environments/environment.ts` is already configured for local development:
   ```typescript
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:8000'
   };
   ```

4. **Configure Environment (Production)**
   Edit `src/environments/environment.prod.ts` when deploying:
   ```typescript
   export const environment = {
     production: true,
     apiUrl: 'https://your-backend-url.com'  // Replace with your actual backend URL
   };
   ```

5. **Test Web Client**
   ```bash
   ng serve
   ```
   
   Open browser to: http://localhost:4200

---

## 💬 Step 6: Configure Discord Bot (Optional)

Only if you want Discord integration.

1. **Navigate to Discord Bot Directory**
   ```bash
   cd ../discord-bot
   ```

2. **Create .env File**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env File**
   Open `discord-bot/.env` and fill in:
   ```env
   # Discord Bot Token (from Step 3)
   DISCORD_BOT_TOKEN=MTxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Backend API URL
   API_URL=http://localhost:8000
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Test Discord Bot**
   ```bash
   python discord_bot.py
   ```
   
   You should see:
   ```
   Mimi AI Waifu has connected to Discord!
   Connected to 1 guild(s)
   ```

6. **Test in Discord**
   - Go to your Discord server
   - Send a message: `Hey Mimi!`
   - Mimi should respond!

---

## 🎯 Quick Reference - Where to Find Everything

| What You Need | Where to Get It | Cost |
|---------------|-----------------|------|
| **HuggingFace Token** | https://huggingface.co/settings/tokens | FREE |
| **Firebase Credentials** | https://console.firebase.google.com/ | FREE |
| **Discord Bot Token** | https://discord.com/developers/applications | FREE |

---

## 📁 Final File Structure

After setup, your project should look like:

```
ai-waifu-system/
├── firebase-credentials.json    # ⚠️ NEVER commit this!
├── backend/
│   ├── .env                     # ⚠️ NEVER commit this!
│   ├── .env.example             # ✅ Template (safe to commit)
│   └── faiss_indices/           # Created automatically
├── web-client/
│   └── src/environments/
│       ├── environment.ts       # Development config
│       └── environment.prod.ts  # Production config
└── discord-bot/
    ├── .env                     # ⚠️ NEVER commit this!
    └── .env.example             # ✅ Template (safe to commit)
```

---

## 🔒 Security Checklist

Before committing to Git:

- [ ] `firebase-credentials.json` is in `.gitignore`
- [ ] `backend/.env` is in `.gitignore`
- [ ] `discord-bot/.env` is in `.gitignore`
- [ ] No tokens are hardcoded in source files
- [ ] `.env.example` files contain only placeholders

---

## ✅ Verification Steps

Test each component:

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", ...}`

### 2. Backend Chat Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "message": "Hello!", "platform": "web"}'
```
Expected: JSON response with `reply`, `affection_level`, `mood`

### 3. Web Client
- Open http://localhost:4200
- Type a message
- Should receive response from Mimi

### 4. Discord Bot
- Send message in Discord server
- Bot should respond

---

## 🆘 Troubleshooting

### "Firebase credentials not found"
- Check `FIREBASE_CREDENTIALS_PATH` in `backend/.env`
- Verify file exists at that path
- Use absolute path if relative path doesn't work

### "Invalid HuggingFace token"
- Verify token starts with `hf_`
- Check for extra spaces in `.env` file
- Generate a new token if needed

### "Discord bot not responding"
- Verify Message Content Intent is enabled
- Check bot has permissions in channel
- Ensure backend is running

### "First response takes 30 seconds"
- This is normal! HuggingFace models have cold start
- Subsequent responses will be faster (2-5 seconds)

---

## 🎉 You're All Set!

Your AI Waifu system is now configured and ready to use!

### Next Steps:
1. Chat with Mimi through web or Discord
2. Watch affection levels increase over time
3. Build daily interaction streaks
4. Experience personality evolution

### Tips:
- Be consistent - daily interactions build stronger relationships
- Emotional messages are remembered better
- Jealousy triggers affect mood and responses
- High affection unlocks callback memories

---

## 📞 Need Help?

- Check component READMEs for detailed docs
- Review troubleshooting sections
- Verify all credentials are correct
- Ensure all services are running

**Happy chatting with Mimi! 💕**
