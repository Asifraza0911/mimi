"""
Unit tests for Discord bot message handling.

Tests verify that the bot correctly captures messages, sends requests
to the AI_Brain backend, and replies in Discord channels.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord_bot


class TestMessageHandling:
    """Test suite for Discord bot message handling functionality."""
    
    @pytest.mark.asyncio
    async def test_on_message_captures_user_id_and_content(self):
        """Test that on_message correctly captures Discord user ID and message content."""
        # Create mock message
        mock_message = MagicMock()
        mock_message.author = MagicMock()  # Different author from bot
        mock_message.author.id = 123456789
        mock_message.content = "Hello Mimi!"
        mock_message.channel.send = AsyncMock()
        
        # Mock requests.post
        with patch('discord_bot.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "reply": "H-hey! Don't just greet me like that!",
                "affection_level": 15,
                "mood": "neutral"
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify POST request was made with correct payload
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            assert call_args[1]['json']['user_id'] == "123456789"
            assert call_args[1]['json']['message'] == "Hello Mimi!"
            assert call_args[1]['json']['platform'] == "discord"
    
    @pytest.mark.asyncio
    async def test_on_message_sends_reply_to_channel(self):
        """Test that on_message sends AI response back to Discord channel."""
        # Create mock message
        mock_message = MagicMock()
        mock_message.author = MagicMock()  # Different author from bot
        mock_message.author.id = 123456789
        mock_message.content = "How are you?"
        mock_message.channel.send = AsyncMock()
        
        # Mock requests.post
        with patch('discord_bot.requests.post') as mock_post:
            expected_reply = "I-I'm fine! Not that you care..."
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "reply": expected_reply,
                "affection_level": 20,
                "mood": "flustered"
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify reply was sent to channel
            mock_message.channel.send.assert_called_once_with(expected_reply)
    
    @pytest.mark.asyncio
    async def test_on_message_ignores_bot_own_messages(self):
        """Test that bot ignores its own messages."""
        # Create mock message from bot itself
        mock_message = MagicMock()
        mock_message.author = discord_bot.bot.user  # Same as bot user
        mock_message.content = "I'm the bot!"
        
        # Mock requests.post
        with patch('discord_bot.requests.post') as mock_post:
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify no POST request was made
            mock_post.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_on_message_ignores_command_messages(self):
        """Test that bot ignores messages starting with command prefix."""
        # Create mock message with command
        mock_message = MagicMock()
        mock_message.author = MagicMock()  # Different author from bot
        mock_message.author.id = 123456789
        mock_message.content = "!status"
        
        # Mock bot.process_commands
        with patch('discord_bot.requests.post') as mock_post, \
             patch.object(discord_bot.bot, 'process_commands', new_callable=AsyncMock) as mock_process:
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify no POST request was made to chat endpoint
            mock_post.assert_not_called()
            
            # Verify process_commands was called
            mock_process.assert_called_once_with(mock_message)
    
    @pytest.mark.asyncio
    async def test_on_message_handles_api_errors_gracefully(self):
        """Test that bot sends fallback message when API fails."""
        # Create mock message
        mock_message = MagicMock()
        mock_message.author = MagicMock()  # Different author from bot
        mock_message.author.id = 123456789
        mock_message.content = "Hello!"
        mock_message.channel.send = AsyncMock()
        
        # Mock requests.post to raise exception
        with patch('discord_bot.requests.post') as mock_post:
            mock_post.side_effect = Exception("API connection failed")
            
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify fallback message was sent
            mock_message.channel.send.assert_called_once()
            call_args = mock_message.channel.send.call_args[0][0]
            assert "Hmph" in call_args or "not talking" in call_args
    
    @pytest.mark.asyncio
    async def test_on_message_uses_correct_api_endpoint(self):
        """Test that on_message sends POST request to correct endpoint."""
        # Create mock message
        mock_message = MagicMock()
        mock_message.author = MagicMock()  # Different author from bot
        mock_message.author.id = 123456789
        mock_message.content = "Test message"
        mock_message.channel.send = AsyncMock()
        
        # Mock requests.post
        with patch('discord_bot.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "reply": "Test reply",
                "affection_level": 50,
                "mood": "neutral"
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            # Call on_message
            await discord_bot.on_message(mock_message)
            
            # Verify correct endpoint was called
            call_args = mock_post.call_args
            assert "/chat" in call_args[0][0]
            assert call_args[1]['timeout'] == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
