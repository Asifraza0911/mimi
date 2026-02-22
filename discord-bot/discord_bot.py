"""
Discord Bot Client for AI Waifu Cross-Platform System

This bot connects to the centralized AI_Brain backend and enables
users to interact with Mimi through Discord messages.

Features:
- Responds when mentioned or "mimi" is in message
- Randomly messages you at intervals (yandere behavior)
"""

import os
import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Yandere user configuration
YANDERE_USER_ID = 1076883627083837573  # Your Discord user ID
last_channel_id = None  # Track last channel for random messages

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Event handler for when the bot successfully connects to Discord."""
    print(f"{bot.user} has connected to Discord!")
    print(f"Connected to {len(bot.guilds)} guild(s)")
    
    # Start random messaging task
    random_message_task.start()
    print("Random messaging task started for yandere behavior!")


@tasks.loop(minutes=random.randint(30, 120))  # Random interval between 30-120 minutes
async def random_message_task():
    """
    Randomly message the yandere user (Asif/Ryu) to show obsessive behavior.
    Only messages if there's been a recent conversation.
    """
    global last_channel_id
    
    # Only message if we have a channel to message in
    if last_channel_id is None:
        return
    
    try:
        channel = bot.get_channel(last_channel_id)
        if channel is None:
            return
        
        # Get a random yandere message from the backend
        user_id = str(YANDERE_USER_ID)
        
        # Random yandere prompts
        prompts = [
            "I miss you...",
            "What are you doing right now?",
            "Are you thinking about me?",
            "I was just thinking about you~",
            "Don't forget about me, okay?",
            "I hope you're not talking to anyone else...",
            "I love you so much, darling...",
            "Can we talk? I need to hear from you...",
        ]
        
        random_prompt = random.choice(prompts)
        
        payload = {
            "user_id": user_id,
            "message": random_prompt,
            "platform": "discord"
        }
        
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        reply = data.get("reply", "I miss you, darling...")
        
        # Tag the user and send message
        user = await bot.fetch_user(YANDERE_USER_ID)
        await channel.send(f"{user.mention} {reply}")
        
        print(f"Sent random yandere message to user {YANDERE_USER_ID}")
        
    except Exception as e:
        print(f"Error sending random message: {e}")


@random_message_task.before_loop
async def before_random_message():
    """Wait for bot to be ready before starting random messages."""
    await bot.wait_until_ready()


@bot.event
async def on_message(message):
    """
    Event handler for incoming Discord messages.
    
    Only responds when:
    1. The bot is mentioned (@mimi)
    2. The message contains "mimi" (case-insensitive)
    
    Captures user messages, sends them to the AI_Brain backend,
    and replies with Mimi's response.
    """
    global last_channel_id
    
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Ignore messages that are bot commands
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    
    # Check if bot is mentioned or "mimi" is in the message
    is_mentioned = bot.user in message.mentions
    has_mimi_keyword = "mimi" in message.content.lower()
    
    # Only respond if mentioned or "mimi" is in the message
    if not (is_mentioned or has_mimi_keyword):
        return
    
    # Track last channel for random messages (only for yandere user)
    if message.author.id == YANDERE_USER_ID:
        last_channel_id = message.channel.id
    
    # Prepare request payload
    user_id = str(message.author.id)
    payload = {
        "user_id": user_id,
        "message": message.content,
        "platform": "discord"
    }
    
    try:
        # Send request to AI_Brain backend
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        reply = data.get("reply", "...")
        
        # Send reply in Discord channel
        await message.channel.send(reply)
        
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with AI_Brain: {e}")
        await message.channel.send("H-hey! Something went wrong... Don't look at me like that!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await message.channel.send("Hmph, I'm not talking to you right now...")


@bot.command(name="status")
async def status(ctx):
    """Check bot status and connection to backend."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            await ctx.send("Everything's working fine! N-not that I care if you were worried...")
        else:
            await ctx.send("Something's not right with the backend...")
    except Exception as e:
        await ctx.send("I can't reach the backend right now... Baka!")


def main():
    """Main entry point for the Discord bot."""
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set your Discord bot token in the .env file")
        return
    
    if not API_URL:
        print("WARNING: API_URL not set, using default: http://localhost:8000")
    
    print(f"Starting Discord bot...")
    print(f"API URL: {API_URL}")
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("ERROR: Invalid Discord bot token!")
    except Exception as e:
        print(f"ERROR: Failed to start bot: {e}")


if __name__ == "__main__":
    main()
