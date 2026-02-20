# Discord Bot - AI Waifu Cross-Platform System

This Discord bot enables users to interact with Mimi (the tsundere AI character) through Discord messages. The bot acts as a thin client that forwards messages to the centralized AI_Brain backend.

## Features

- Real-time chat with Mimi through Discord
- Automatic message forwarding to AI_Brain backend
- Consistent personality and memory across platforms
- Status command to check bot and backend health

## Prerequisites

- Python 3.10 or higher
- Discord Bot Token (from Discord Developer Portal)
- Running AI_Brain backend service

## Setup Instructions

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
5. Copy the bot token (you'll need this for configuration)

### 2. Install Dependencies

```bash
cd discord-bot
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
DISCORD_BOT_TOKEN=your_actual_discord_bot_token
API_URL=http://localhost:8000
```

For production, set `API_URL` to your deployed backend URL.

### 4. Invite Bot to Your Server

1. In Discord Developer Portal, go to "OAuth2" → "URL Generator"
2. Select scopes:
   - `bot`
3. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select the server you want to add the bot to

### 5. Run the Bot

```bash
python discord_bot.py
```

You should see:
```
<BotName> has connected to Discord!
Connected to X guild(s)
```

## Usage

### Chat with Mimi

Simply send a message in any channel where the bot has access:

```
User: Hey Mimi!
Mimi: H-hey! What do you want?
```

### Check Status

Use the status command to verify the bot and backend are working:

```
!status
```

## Architecture

The Discord bot follows the thin client architecture:

```
Discord User → Discord Bot → AI_Brain Backend → Response
                    ↓                              ↓
              (discord_bot.py)              (FastAPI /chat)
```

All AI logic, memory, and personality are handled by the backend. The bot only:
1. Receives Discord messages
2. Forwards them to the backend with `platform="discord"`
3. Sends the backend's response back to Discord

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot authentication token | Required |
| `API_URL` | URL of the AI_Brain backend | `http://localhost:8000` |

## Troubleshooting

### Bot doesn't respond to messages

- Check that Message Content Intent is enabled in Discord Developer Portal
- Verify the bot has permission to read and send messages in the channel
- Check that the backend is running and accessible at the configured `API_URL`

### "Invalid Discord bot token" error

- Verify your `DISCORD_BOT_TOKEN` in `.env` is correct
- Make sure you copied the token from the "Bot" section, not the Client ID

### Backend connection errors

- Ensure the AI_Brain backend is running
- Verify `API_URL` in `.env` points to the correct backend address
- Check firewall settings if backend is on a different machine

## Development

### Testing Locally

1. Start the backend:
   ```bash
   cd ../backend
   uvicorn main:app --reload
   ```

2. In another terminal, start the bot:
   ```bash
   cd discord-bot
   python discord_bot.py
   ```

3. Send messages to the bot in Discord

### Adding New Commands

Add new commands using the `@bot.command()` decorator:

```python
@bot.command(name="mycommand")
async def my_command(ctx):
    await ctx.send("Response")
```

## Requirements Validation

This implementation satisfies:
- **Requirement 6.1**: Discord bot authentication using token from environment
- **Requirement 6.2**: Message capture with Discord user ID
- **Requirement 6.3**: POST request to AI_Brain with platform="discord"
- **Requirement 6.4**: Reply in Discord channel with backend response
- **Requirement 6.5**: Uses discord.py library for Discord API integration
- **Requirement 9.3**: Discord bot token loaded from environment variable

## License

Part of the AI Waifu Cross-Platform System.
