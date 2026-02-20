# 🔍 Where to Find Your Credentials

A visual guide showing exactly where to get each credential.

---

## 1️⃣ HuggingFace API Token

### 🌐 Website
```
https://huggingface.co/settings/tokens
```

### 📸 Visual Steps

1. **Sign up/Login** at https://huggingface.co
   ```
   Top right corner → "Sign Up" or "Login"
   ```

2. **Go to Settings**
   ```
   Click your profile picture (top right) → "Settings"
   ```

3. **Access Tokens**
   ```
   Left sidebar → "Access Tokens"
   ```

4. **Create New Token**
   ```
   Click "New token" button
   Name: "ai-waifu-backend"
   Type: "Read"
   Click "Generate token"
   ```

5. **Copy Token**
   ```
   Format: hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ⚠️ Copy immediately - you won't see it again!
   ```

### 💰 Cost
**FREE** - No credit card required

### ⏱️ Time Required
**2 minutes**

---

## 2️⃣ Firebase Credentials

### 🌐 Website
```
https://console.firebase.google.com/
```

### 📸 Visual Steps

1. **Create Project**
   ```
   Click "Add project"
   Name: "ai-waifu-system"
   Disable Google Analytics (optional)
   Click "Create project"
   ```

2. **Enable Firestore**
   ```
   Left menu → "Firestore Database"
   Click "Create database"
   Mode: "Start in test mode" (for development)
   Location: Choose closest region
   Click "Enable"
   ```

3. **Get Service Account Key**
   ```
   Click ⚙️ gear icon (top left) → "Project settings"
   Tab: "Service accounts"
   Click "Generate new private key"
   Click "Generate key" in popup
   ```

4. **Download JSON File**
   ```
   File downloads automatically
   Name: ai-waifu-system-xxxxx-firebase-adminsdk-xxxxx.json
   ```

5. **Save in Project**
   ```bash
   # Rename and move to project root
   mv ~/Downloads/ai-waifu-system-*.json ./firebase-credentials.json
   ```

### 💰 Cost
**FREE** - Generous free tier:
- 1 GB storage
- 50,000 reads/day
- 20,000 writes/day

### ⏱️ Time Required
**5 minutes**

---

## 3️⃣ Discord Bot Token (Optional)

### 🌐 Website
```
https://discord.com/developers/applications
```

### 📸 Visual Steps

1. **Create Application**
   ```
   Click "New Application"
   Name: "Mimi AI Waifu"
   Accept ToS
   Click "Create"
   ```

2. **Create Bot**
   ```
   Left sidebar → "Bot"
   Click "Add Bot"
   Click "Yes, do it!"
   ```

3. **Enable Intents**
   ```
   Scroll to "Privileged Gateway Intents"
   ✅ Enable "Message Content Intent"
   Click "Save Changes"
   ```

4. **Get Token**
   ```
   Under "TOKEN" section
   Click "Reset Token"
   Click "Yes, do it!"
   Copy token immediately
   Format: MTxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Invite Bot to Server**
   ```
   Left sidebar → "OAuth2" → "URL Generator"
   
   Scopes:
   ✅ bot
   
   Bot Permissions:
   ✅ Read Messages/View Channels
   ✅ Send Messages
   ✅ Read Message History
   
   Copy generated URL
   Open in browser
   Select your server
   Click "Authorize"
   ```

### 💰 Cost
**FREE** - No limits

### ⏱️ Time Required
**3 minutes**

---

## 📝 Summary Table

| Credential | Website | Time | Cost | Required? |
|------------|---------|------|------|-----------|
| **HuggingFace Token** | https://huggingface.co/settings/tokens | 2 min | FREE | ✅ Yes |
| **Firebase Credentials** | https://console.firebase.google.com/ | 5 min | FREE | ✅ Yes |
| **Discord Bot Token** | https://discord.com/developers/applications | 3 min | FREE | ⬜ Optional |

---

## 🎯 What Each Credential Does

### HuggingFace Token
- Powers Mimi's AI responses
- Connects to LLM models (Qwen)
- Handles emotional analysis and dialogue generation

### Firebase Credentials
- Stores user relationships and affection levels
- Saves long-term memories
- Tracks interaction history

### Discord Bot Token
- Enables Discord integration
- Allows bot to read and send messages
- Connects Discord to backend

---

## 📂 Where to Put Credentials

### Backend (.env)
```env
# Location: backend/.env

HUGGINGFACE_API_TOKEN=hf_your_token_here
FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
```

### Firebase JSON
```
# Location: project root
./firebase-credentials.json
```

### Discord Bot (.env)
```env
# Location: discord-bot/.env

DISCORD_BOT_TOKEN=your_discord_token_here
API_URL=http://localhost:8000
```

---

## 🔒 Security Notes

### ⚠️ NEVER Commit These Files:
- `firebase-credentials.json`
- `backend/.env`
- `discord-bot/.env`

### ✅ Safe to Commit:
- `.env.example` files (templates only)
- Source code files
- Configuration templates

### 🛡️ Best Practices:
1. Keep credentials in `.env` files
2. Use `.gitignore` to exclude sensitive files
3. Never hardcode tokens in source code
4. Rotate tokens if accidentally exposed
5. Use different tokens for dev/prod

---

## 🆘 Troubleshooting

### Can't Find HuggingFace Token Page?
1. Make sure you're logged in
2. Click profile picture → Settings
3. Look for "Access Tokens" in left sidebar

### Firebase Download Didn't Work?
1. Check your Downloads folder
2. Look for file starting with your project name
3. File ends with `.json`

### Discord Bot Not Showing Up?
1. Make sure you used the OAuth2 URL
2. Check you selected the right server
3. Verify bot has permissions in server settings

---

## ✅ Verification

After getting all credentials, verify:

```bash
# Check files exist
ls firebase-credentials.json  # Should exist
ls backend/.env               # Should exist
ls discord-bot/.env           # Should exist (if using Discord)

# Check .env files have tokens
cat backend/.env | grep HUGGINGFACE_API_TOKEN
cat backend/.env | grep FIREBASE_CREDENTIALS_PATH
cat discord-bot/.env | grep DISCORD_BOT_TOKEN
```

---

## 🎉 Next Steps

Once you have all credentials:

1. ✅ Follow `QUICK_START.md` to start the system
2. ✅ Use `CREDENTIALS_CHECKLIST.md` to track progress
3. ✅ Read `SETUP_GUIDE.md` for detailed instructions

---

**All credentials are FREE and take ~10 minutes total to obtain!**
