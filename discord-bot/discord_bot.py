"""
Discord Bot Client for AI Waifu Cross-Platform System

This bot connects to the centralized AI_Brain backend and enables
users to interact with Mimi through Discord messages.
"""

import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Event handler for when the bot successfully connects to Discord."""
    print(f"{bot.user} has connected to Discord!")
    print(f"Connected to {len(bot.guilds)} guild(s)")


@bot.event
async def on_message(message):
    """
    Event handler for incoming Discord messages.
    
    Captures user messages, sends them to the AI_Brain backend,
    and replies with Mimi's response.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Ignore messages that are bot commands
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    
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
