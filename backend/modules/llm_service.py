"""
LLM Service Module - Dual-Model Cognitive Architecture

This module implements a two-stage cognitive pipeline:
1. Thinking Model (Qwen3.5-397B-A17B): Emotional analysis and reasoning
2. Dialogue Model (Qwen2.5-7B-Instruct): Personality-driven response generation

The separation ensures:
- Accurate emotional detection and relationship analysis (thinking model)
- Natural tsundere personality in responses (dialogue model)

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 19.3, 19.10, 19.11
"""

import logging
import random
import json
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Exception raised for LLM service errors."""
    pass


class LLMService:
    """
    Dual-Model Cognitive Architecture for AI Waifu System.
    
    This service implements a two-stage pipeline:
    
    Stage 1 - Thinking Model (Qwen3.5-397B-A17B):
        - Emotional analysis
        - Sentiment detection
        - Jealousy triggers
        - Memory importance scoring
        - Relationship impact assessment
    
    Stage 2 - Dialogue Model (Qwen2.5-7B-Instruct):
        - Tsundere personality
        - Natural conversational output
        - Emotional speech patterns
    
    Attributes:
        api_token (str): HuggingFace API authentication token
        thinking_model (str): Reasoning model for emotional analysis
        dialogue_model (str): Instruction-tuned model for personality
        thinking_api_url (str): API endpoint for thinking model
        dialogue_api_url (str): API endpoint for dialogue model
        fallback_responses (list): Predefined responses for error cases
    """
    
    def __init__(self, api_token: str):
        """
        Initialize LLM Service with dual-model architecture using HuggingFace Router.
        
        Args:
            api_token: HuggingFace API token from environment configuration
            
        Requirements: 13.5
        """
        self.api_token = api_token
        
        # Initialize HuggingFace InferenceClient with router endpoint
        self.client = InferenceClient(
            base_url="https://router.huggingface.co",
            token=api_token
        )
        
        # Using Qwen2.5-7B-Instruct for both thinking and dialogue
        # Router will automatically route to available providers (Novita, Featherless, Together, Fireworks, Groq)
        self.thinking_model = "Qwen/Qwen2.5-7B-Instruct"
        self.dialogue_model = "Qwen/Qwen2.5-7B-Instruct"
        
        self.fallback_responses = [
            "H-hey! Don't ignore me like that!",
            "Hmph, I'm not talking to you right now...",
            "W-what? I wasn't waiting for you or anything!",
            "Baka! Something's not working right...",
            "D-don't look at me like that! I'm trying my best!"
        ]
        
        logger.info(f"LLM Service initialized with HuggingFace Router:")
        logger.info(f"  Router URL: https://router.huggingface.co")
        logger.info(f"  Thinking Model: {self.thinking_model}")
        logger.info(f"  Dialogue Model: {self.dialogue_model}")
    
    
    def analyze_emotional_state(
        self,
        user_message: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Stage 1: Use thinking model to analyze emotional and relational aspects.
        
        This method uses Qwen2.5-7B-Instruct to extract:
        - Emotion detection
        - Sentiment analysis
        - Jealousy triggers
        - Vulnerability indicators
        - Memory importance
        - Relationship impact
        
        Args:
            user_message: The user's message to analyze
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing emotional analysis results
            
        Example output:
            {
                "emotion": "neutral",
                "sentiment": "neutral",
                "jealousy_trigger": true,
                "vulnerability": false,
                "compliment": false,
                "rudeness": false,
                "memory_importance": 0.7,
                "relationship_impact": -2
            }
        """
        logger.info("Stage 1: Analyzing emotional state with thinking model")
        
        # Construct thinking prompt
        thinking_prompt = f"""Analyze the user's message emotionally and relationally.

Extract the following information and return ONLY valid JSON:

emotion: (happy/sad/angry/jealous/flustered/neutral)
sentiment: (positive/negative/neutral)
jealousy_trigger: (true/false)
vulnerability: (true/false)
compliment: (true/false)
rudeness: (true/false)
memory_importance: (0.0 to 1.0)
relationship_impact: (-5 to +5)

User message: "{user_message}"

Return ONLY JSON format:"""
        
        # Retry loop
        for attempt in range(max_retries):
            try:
                logger.debug(f"Sending thinking model request (attempt {attempt + 1}/{max_retries})")
                
                # Use chat completion API for conversational models
                messages = [
                    {"role": "user", "content": thinking_prompt}
                ]
                
                response = self.client.chat_completion(
                    messages=messages,
                    model=self.thinking_model,
                    max_tokens=200,
                    temperature=0.3
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                logger.debug(f"Thinking model output: {response_text}")
                
                # Parse JSON from response
                try:
                    # Extract JSON from response (may have extra text)
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        analysis = json.loads(json_str)
                        logger.info(f"Emotional analysis complete: {analysis}")
                        return analysis
                    else:
                        logger.warning("No JSON found in thinking model response")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from thinking model: {e}")
                    
            except Exception as e:
                logger.error(f"Thinking model request failed: {e}")
                if attempt < max_retries - 1:
                    continue
        
        # Fallback to neutral analysis
        logger.warning("Using fallback neutral emotional analysis")
        return {
            "emotion": "neutral",
            "sentiment": "neutral",
            "jealousy_trigger": False,
            "vulnerability": False,
            "compliment": False,
            "rudeness": False,
            "memory_importance": 0.3,
            "relationship_impact": 0
        }
    
    def generate_response(
        self,
        prompt: str,
        max_length: int = 150,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        Stage 2: Generate personality-driven dialogue response.
        
        This method uses Qwen2.5-7B-Instruct to generate natural tsundere
        responses based on the emotional state and personality context.
        
        The prompt should include:
        - Mimi's personality definition
        - Current emotional state (affection, mood, attachment)
        - User's message
        - Conversation context
        
        Args:
            prompt: Complete prompt with personality and emotional state
            max_length: Maximum response length in tokens (default: 150)
            temperature: Randomness control (0.0-1.0, default: 0.7)
                - Lower values (0.3-0.4): More controlled, predictable responses
                - Medium values (0.5-0.7): Standard to playful variation
                - Higher values (0.8-0.9): More chaotic, emotional responses
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Generated tsundere response from Mimi
            
        Raises:
            LLMServiceError: On API failures after retries
            
        Requirements: 13.2, 13.3, 19.3, 19.10, 19.11
        """
        logger.info(f"Stage 2: Generating dialogue with temperature: {temperature}")
        
        # Retry loop for handling transient failures
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.debug(f"Sending dialogue model request (attempt {attempt + 1}/{max_retries})")
                
                # Use chat completion API for conversational models
                # Add instruction for short, natural responses
                system_message = (
                    "You are Mimi, a tsundere anime girl. Respond in character. "
                    "IMPORTANT: Keep responses SHORT (1-2 sentences max), natural, and human-like. "
                    "Talk like a real person texting, not like an AI. Be casual and brief."
                )
                
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
                
                response = self.client.chat_completion(
                    messages=messages,
                    model=self.dialogue_model,
                    max_tokens=150,  # Increased to allow complete sentences
                    temperature=temperature
                )
                
                # Extract response text
                response_text = response.choices[0].message.content
                
                # Only truncate if response is excessively long (more than 3 sentences)
                sentences = response_text.split('.')
                if len(sentences) > 3:
                    response_text = '. '.join(sentences[:3]) + '.'
                
                logger.info(f"Successfully generated dialogue response (length: {len(response_text)})")
                return response_text.strip()
                    
            except Exception as e:
                logger.warning(f"Dialogue model request failed: {str(e)} (attempt {attempt + 1}/{max_retries})")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error(f"Max retries reached for request exception: {str(e)}")
                    return self.get_fallback_response()
        
        # Should not reach here, but return fallback just in case
        logger.error(f"Exhausted all retries. Last error: {last_error}")
        return self.get_fallback_response()
    
    def get_fallback_response(self) -> str:
        """
        Return random fallback response for error cases.
        
        This method provides a tsundere-appropriate response when the LLM
        service is unavailable or encounters errors.
        
        Returns:
            Random fallback response string
            
        Requirements: 13.4
        """
        response = random.choice(self.fallback_responses)
        logger.info(f"Using fallback response: {response}")
        return response
