# 🔧 Troubleshooting Credentials

Common issues and solutions when setting up credentials.

---

## 🔑 HuggingFace Issues

### ❌ "Invalid API token" or "Unauthorized"

**Symptoms:**
- Backend logs show authentication errors
- Responses fail with 401 errors
- Health check shows LLM service as "not ready"

**Solutions:**

1. **Verify Token Format**
   ```bash
   # Token should start with hf_
   echo $HUGGINGFACE_API_TOKEN
   # Should output: hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

2. **Check for Extra Spaces**
   ```bash
   # Open .env and check for spaces
   cat backend/.env | grep HUGGINGFACE_API_TOKEN
   # Should be: HUGGINGFACE_API_TOKEN=hf_xxx (no spaces around =)
   ```

3. **Regenerate Token**
   - Go to https://huggingface.co/settings/tokens
   - Delete old token
   - Create new token with "Read" permissions
   - Update `backend/.env`

4. **Verify Token is Active**
   ```bash
   # Test token with curl
   curl https://huggingface.co/api/whoami-v2 \
     -H "Authorization: Bearer hf_your_token_here"
   # Should return your username
   ```

---

### ⏱️ "First request takes 30+ seconds"

**Symptoms:**
- First message to Mimi takes very long
- Subsequent messages are fast (2-5 seconds)

**This is NORMAL!**
- HuggingFace Inference API has "cold start"
- Models need to load on first request
- This happens once per session

**Not a Problem:**
- Just wait for first response
- Future responses will be fast

---

### 🚫 "Model loading error" or 503 errors

**Symptoms:**
- Responses fail with 503 Service Unavailable
- Backend logs show model loading errors

**Solutions:**

1. **Wait and Retry**
   - HuggingFace may be loading the model
   - Wait 30 seconds and try again

2. **Check HuggingFace Status**
   - Visit https://status.huggingface.co/
   - Check if Inference API is operational

3. **Verify Model Access**
   - Models used: `Qwen/Qwen2.5-7B-Instruct` and `Qwen/Qwen3.5-397B-A17B`
   - These are public models (no special access needed)

---

## 🔥 Firebase Issues

### ❌ "Firebase credentials not found"

**Symptoms:**
- Backend fails to start
- Error: "FileNotFoundError: firebase-credentials.json"
- Health check shows Firestore as "disconnected"

**Solutions:**

1. **Check File Exists**
   ```bash
   ls firebase-credentials.json
   # Should show the file
   ```

2. **Verify Path in .env**
   ```bash
   cat backend/.env | grep FIREBASE_CREDENTIALS_PATH
   # Should show: FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json
   ```

3. **Use Absolute Path**
   ```env
   # In backend/.env, use full path
   FIREBASE_CREDENTIALS_PATH=/full/path/to/firebase-credentials.json
   ```

4. **Check File Permissions**
   ```bash
   # File should be readable
   chmod 644 firebase-credentials.json
   ```

---

### ❌ "Permission denied" or "Insufficient permissions"

**Symptoms:**
- Backend starts but can't read/write Firestore
- Error mentions "PERMISSION_DENIED"

**Solutions:**

1. **Check Firestore Rules**
   - Go to Firebase Console → Firestore → Rules
   - For development, use test mode:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if true;
       }
     }
   }
   ```

2. **Verify Service Account Permissions**
   - Firebase Console → Project Settings → Service Accounts
   - Ensure service account has "Firebase Admin" role

3. **Regenerate Credentials**
   - Delete old service account key
   - Generate new private key
   - Update `firebase-credentials.json`

---

### ❌ "Invalid JSON" or "Malformed credentials"

**Symptoms:**
- Error parsing Firebase credentials
- Backend fails to initialize Firestore

**Solutions:**

1. **Verify JSON Format**
   ```bash
   # Check if file is valid JSON
   python -m json.tool firebase-credentials.json
   # Should output formatted JSON without errors
   ```

2. **Re-download Credentials**
   - Firebase Console → Project Settings → Service Accounts
   - Generate new private key
   - Replace `firebase-credentials.json`

3. **Check File Encoding**
   ```bash
   # File should be UTF-8
   file firebase-credentials.json
   # Should show: JSON data
   ```

---

## 🤖 Discord Bot Issues

### ❌ "Invalid Discord bot token"

**Symptoms:**
- Bot fails to connect
- Error: "Improper token has been passed"
- Bot doesn't appear online in Discord

**Solutions:**

1. **Verify Token Format**
   ```bash
   cat discord-bot/.env | grep DISCORD_BOT_TOKEN
   # Should be: DISCORD_BOT_TOKEN=MTxxxxxxxxx.xxxxxx.xxxxx
   # Token has 3 parts separated by dots
   ```

2. **Check for Spaces**
   ```env
   # In discord-bot/.env
   DISCORD_BOT_TOKEN=your_token_here
   # No spaces around = or in token
   ```

3. **Regenerate Token**
   - Discord Developer Portal → Your App → Bot
   - Click "Reset Token"
   - Copy new token
   - Update `discord-bot/.env`

---

### ❌ "Bot doesn't respond to messages"

**Symptoms:**
- Bot is online but doesn't reply
- No errors in console

**Solutions:**

1. **Enable Message Content Intent**
   - Discord Developer Portal → Your App → Bot
   - Scroll to "Privileged Gateway Intents"
   - ✅ Enable "Message Content Intent"
   - Click "Save Changes"
   - Restart bot

2. **Check Bot Permissions**
   - In Discord server settings → Roles
   - Find bot's role
   - Ensure it has:
     - ✅ Read Messages/View Channels
     - ✅ Send Messages
     - ✅ Read Message History

3. **Verify Backend Connection**
   ```bash
   # Check API_URL in discord-bot/.env
   cat discord-bot/.env | grep API_URL
   # Should point to running backend
   
   # Test backend is accessible
   curl http://localhost:8000/health
   ```

---

### ❌ "Bot can't see messages in channel"

**Symptoms:**
- Bot is online but doesn't see messages
- Works in some channels but not others

**Solutions:**

1. **Check Channel Permissions**
   - Right-click channel → Edit Channel → Permissions
   - Add bot role
   - Enable "View Channel" and "Read Message History"

2. **Verify Bot Role Position**
   - Server Settings → Roles
   - Bot role should be above @everyone
   - Drag to reorder if needed

---

## 🌐 Network Issues

### ❌ "Connection refused" or "Cannot connect to backend"

**Symptoms:**
- Web client or Discord bot can't reach backend
- Error: "Connection refused" or "ECONNREFUSED"

**Solutions:**

1. **Verify Backend is Running**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   # Should return JSON with "status": "healthy"
   ```

2. **Check Port**
   ```bash
   # Verify backend is on port 8000
   netstat -an | grep 8000
   # Should show LISTENING on port 8000
   ```

3. **Update URLs**
   ```env
   # In discord-bot/.env
   API_URL=http://localhost:8000
   
   # In web-client/src/environments/environment.ts
   apiUrl: 'http://localhost:8000'
   ```

4. **Check Firewall**
   - Ensure port 8000 is not blocked
   - Temporarily disable firewall to test

---

### ❌ "CORS error" in web client

**Symptoms:**
- Browser console shows CORS errors
- Web client can't make requests to backend

**Solutions:**

1. **Verify Backend CORS Settings**
   - Backend should allow `http://localhost:4200`
   - Check `main.py` for CORS middleware

2. **Use Correct URL**
   ```typescript
   // In environment.ts
   apiUrl: 'http://localhost:8000'  // Not https, not different port
   ```

---

## 🔍 Debugging Tips

### Check All Services

```bash
# Backend health
curl http://localhost:8000/health

# Backend test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hi", "platform": "web"}'

# Web client
open http://localhost:4200

# Discord bot logs
# Check terminal where bot is running
```

### View Logs

```bash
# Backend logs
# Check terminal where uvicorn is running
# Look for errors or warnings

# Discord bot logs
# Check terminal where bot is running
# Look for connection errors

# Web client logs
# Open browser console (F12)
# Check for errors
```

### Verify Environment Variables

```bash
# Backend
cd backend
cat .env
# Should show all required variables

# Discord bot
cd discord-bot
cat .env
# Should show DISCORD_BOT_TOKEN and API_URL
```

---

## 📞 Still Having Issues?

### Checklist

- [ ] All credentials are in correct format
- [ ] No extra spaces in .env files
- [ ] Files are in correct locations
- [ ] Backend is running and healthy
- [ ] Firewall is not blocking connections
- [ ] All services can reach each other

### Get Help

1. Check component-specific READMEs
2. Review setup guides
3. Verify all prerequisites are met
4. Try regenerating credentials
5. Test each component individually

---

## 🎯 Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Invalid token | Regenerate and update .env |
| File not found | Check path in .env |
| Permission denied | Check Firestore rules |
| Bot not responding | Enable Message Content Intent |
| Connection refused | Verify backend is running |
| CORS error | Check backend CORS settings |
| Slow first response | Normal - wait 30 seconds |

---

**Most issues are solved by:**
1. Checking .env files for typos
2. Verifying file paths
3. Regenerating credentials
4. Restarting services
