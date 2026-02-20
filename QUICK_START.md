# ⚡ Quick Start Guide

Get up and running in 10 minutes!

## 🎯 What You'll Need

1. **HuggingFace Token** (2 minutes)
2. **Firebase Credentials** (5 minutes)
3. **Discord Bot Token** (3 minutes) - Optional

---

## 🚀 Fast Track Setup

### Step 1: Get HuggingFace Token (2 min)

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token" → Name it → Select "Read" → Generate
3. Copy token (starts with `hf_`)

### Step 2: Get Firebase Credentials (5 min)

1. Go to: https://console.firebase.google.com/
2. Create project → Enable Firestore (test mode)
3. Project Settings → Service Accounts → Generate Key
4. Download JSON file → Save as `firebase-credentials.json`

### Step 3: Configure Backend (1 min)

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
HUGGINGFACE_API_TOKEN=hf_your_token_here
FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
```

### Step 4: Start Backend (1 min)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit: http://localhost:8000/health

### Step 5: Start Web Client (1 min)

```bash
cd ../web-client
npm install
ng serve
```

Visit: http://localhost:4200

---

## 🎉 Done!

You can now chat with Mimi through the web interface!

---

## 🤖 Optional: Discord Bot

### Get Discord Token (3 min)

1. Go to: https://discord.com/developers/applications
2. New Application → Add Bot → Enable Message Content Intent
3. Copy token

### Configure & Run

```bash
cd discord-bot
cp .env.example .env
```

Edit `discord-bot/.env`:
```env
DISCORD_BOT_TOKEN=your_token_here
API_URL=http://localhost:8000
```

```bash
pip install -r requirements.txt
python discord_bot.py
```

Invite bot to server using OAuth2 URL Generator.

---

## 📋 Verification Checklist

- [ ] Backend health check returns "healthy"
- [ ] Web client loads at localhost:4200
- [ ] Can send message and get response
- [ ] (Optional) Discord bot responds to messages

---

## 🆘 Common Issues

**"Firebase credentials not found"**
→ Check path in `backend/.env` points to JSON file

**"Invalid HuggingFace token"**
→ Verify token starts with `hf_` and has no spaces

**"First response takes 30 seconds"**
→ Normal! Model cold start. Next responses are faster.

---

## 📚 More Help

- **Detailed Setup:** See `SETUP_GUIDE.md`
- **Credentials Tracking:** See `CREDENTIALS_CHECKLIST.md`
- **Full Documentation:** See `README.md`

---

**Ready to chat with Mimi! 💕**
