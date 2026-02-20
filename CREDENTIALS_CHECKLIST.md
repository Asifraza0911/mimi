# 📝 Credentials Checklist

Use this checklist to track your setup progress.

## 🔑 Required Credentials

### 1. HuggingFace API Token
- [ ] Created HuggingFace account
- [ ] Generated API token
- [ ] Token saved: `hf_________________________________`
- [ ] Added to `backend/.env`

**Get it here:** https://huggingface.co/settings/tokens

---

### 2. Firebase Credentials
- [ ] Created Firebase project
- [ ] Enabled Firestore Database
- [ ] Downloaded service account JSON
- [ ] Saved as `firebase-credentials.json` in project root
- [ ] Path added to `backend/.env`

**Get it here:** https://console.firebase.google.com/

**File location:** `./firebase-credentials.json`

---

### 3. Discord Bot Token (Optional)
- [ ] Created Discord application
- [ ] Created bot user
- [ ] Enabled Message Content Intent
- [ ] Copied bot token
- [ ] Token saved: `MT________________________.______._________________________`
- [ ] Added to `discord-bot/.env`
- [ ] Invited bot to server

**Get it here:** https://discord.com/developers/applications

---

## ⚙️ Configuration Files

### Backend (.env)
- [ ] Created `backend/.env` from `.env.example`
- [ ] Added `HUGGINGFACE_API_TOKEN`
- [ ] Added `FIREBASE_CREDENTIALS_PATH`
- [ ] Verified other settings

**Location:** `backend/.env`

```env
HUGGINGFACE_API_TOKEN=hf_your_token_here
FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
SESSION_TIMEOUT_MINUTES=30
MEMORY_RETRIEVAL_COUNT=3
CONTEXT_WINDOW_SIZE=5
LOG_LEVEL=INFO
```

---

### Discord Bot (.env)
- [ ] Created `discord-bot/.env` from `.env.example`
- [ ] Added `DISCORD_BOT_TOKEN`
- [ ] Set `API_URL` (default: http://localhost:8000)

**Location:** `discord-bot/.env`

```env
DISCORD_BOT_TOKEN=your_discord_token_here
API_URL=http://localhost:8000
```

---

### Web Client (environment.ts)
- [ ] Reviewed `src/environments/environment.ts`
- [ ] Confirmed `apiUrl` points to backend (default: http://localhost:8000)
- [ ] Updated `environment.prod.ts` for production (if deploying)

**Location:** `web-client/src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

---

## 🧪 Testing

### Backend
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Started backend: `uvicorn main:app --reload`
- [ ] Health check passed: http://localhost:8000/health
- [ ] Test chat request successful

**Test command:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hi!", "platform": "web"}'
```

---

### Web Client
- [ ] Installed dependencies: `npm install`
- [ ] Started dev server: `ng serve`
- [ ] Opened http://localhost:4200
- [ ] Sent test message
- [ ] Received response from Mimi

---

### Discord Bot (Optional)
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Started bot: `python discord_bot.py`
- [ ] Bot connected to Discord
- [ ] Sent message in Discord
- [ ] Bot responded

---

## 🔒 Security Verification

- [ ] `firebase-credentials.json` is NOT in Git
- [ ] `backend/.env` is NOT in Git
- [ ] `discord-bot/.env` is NOT in Git
- [ ] `.gitignore` includes all sensitive files
- [ ] No tokens in source code

**Check with:**
```bash
git status
# Should NOT show .env files or firebase-credentials.json
```

---

## 📊 Quick Status Check

| Component | Status | URL/Command |
|-----------|--------|-------------|
| Backend | ⬜ Running | http://localhost:8000/health |
| Web Client | ⬜ Running | http://localhost:4200 |
| Discord Bot | ⬜ Running | Check Discord server |
| Firebase | ⬜ Connected | Check backend health endpoint |
| HuggingFace | ⬜ Working | Send test message |

---

## 🎯 All Set?

If all checkboxes are marked, you're ready to go! 🎉

### Start Everything:

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Web Client:**
```bash
cd web-client
ng serve
```

**Terminal 3 - Discord Bot (Optional):**
```bash
cd discord-bot
python discord_bot.py
```

---

## 📞 Need Help?

Refer to:
- `SETUP_GUIDE.md` - Detailed setup instructions
- `README.md` - Project overview
- `backend/README.md` - Backend documentation
- `discord-bot/README.md` - Discord bot documentation

---

**Last Updated:** Check this list as you complete each step!
