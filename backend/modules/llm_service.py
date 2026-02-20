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

import requests
import logging
import random
import json
from typing import Optional, Dict, Any

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
        Initialize LLM Service with dual-model architecture.
        
        Args:
            api_token: HuggingFace API token from environment configuration
            
        Requirements: 13.5
        """
        self.api_token = api_token
        
        # Thinking Model - Cognitive Brain (Qwen3.5-397B-A17B)
        self.thinking_model = "Qwen/Qwen3.5-397B-A17B"
        self.thinking_api_url = f"https://api-inference.huggingface.co/models/{self.thinking_model}"
        
        # Dialogue Model - Personality Brain (Qwen2.5-7B-Instruct)
        self.dialogue_model = "Qwen/Qwen2.5-7B-Instruct"
        self.dialogue_api_url = f"https://api-inference.huggingface.co/models/{self.dialogue_model}"
        
        self.fallback_responses = [
            "H-hey! Don't ignore me like that!",
            "Hmph, I'm not talking to you right now...",
            "W-what? I wasn't waiting for you or anything!",
            "Baka! Something's not working right...",
            "D-don't look at me like that! I'm trying my best!"
        ]
        
        logger.info(f"LLM Service initialized with dual-model architecture:")
        logger.info(f"  Thinking Model: {self.thinking_model}")
        logger.info(f"  Dialogue Model: {self.dialogue_model}")
    
    
    def analyze_emotional_state(
        self,
        user_message: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Stage 1: Use thinking model to analyze emotional and relational aspects.
        
        This method uses Qwen3.5-397B-A17B to extract:
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
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": thinking_prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.3,  # Low temperature for analytical reasoning
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        # Retry loop
        for attempt in range(max_retries):
            try:
                logger.debug(f"Sending thinking model request (attempt {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.thinking_api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract generated text
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        logger.debug(f"Thinking model output: {generated_text}")
                        
                        # Parse JSON from response
                        try:
                            # Extract JSON from response (may have extra text)
                            json_start = generated_text.find('{')
                            json_end = generated_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_str = generated_text[json_start:json_end]
                                analysis = json.loads(json_str)
                                logger.info(f"Emotional analysis complete: {analysis}")
                                return analysis
                            else:
                                logger.warning("No JSON found in thinking model response")
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON from thinking model: {e}")
                
                # Handle errors
                elif response.status_code == 503 and attempt < max_retries - 1:
                    logger.warning("Thinking model loading, retrying...")
                    continue
                else:
                    logger.error(f"Thinking model API error: {response.status_code}")
                    
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
        
        # Prepare request headers
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare request payload with temperature parameter
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": temperature,
                "do_sample": True,
                "top_p": 0.9,
                "repetition_penalty": 1.2
            }
        }
        
        # Retry loop for handling transient failures
        last_error = None
        for attempt in range(max_retries):
            try:
                # Send request to dialogue model
                logger.debug(f"Sending dialogue model request (attempt {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.dialogue_api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                # Check for successful response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract generated text
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        logger.info(f"Successfully generated dialogue response (length: {len(generated_text)})")
                        return generated_text.strip()
                    else:
                        logger.warning("Unexpected response format from dialogue model")
                        return self.get_fallback_response()
                
                # Handle API errors
                elif response.status_code == 503:
                    logger.warning(f"Dialogue model is loading (attempt {attempt + 1}/{max_retries})")
                    last_error = "Model loading"
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error("Max retries reached for model loading")
                        return self.get_fallback_response()
                
                elif response.status_code == 401:
                    logger.error("HuggingFace API authentication failed")
                    raise LLMServiceError("Invalid API token")
                
                elif response.status_code >= 500:
                    logger.warning(f"Dialogue model server error: {response.status_code} (attempt {attempt + 1}/{max_retries})")
                    last_error = f"Server error: {response.status_code}"
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error(f"Max retries reached for server error: {response.text}")
                        return self.get_fallback_response()
                
                else:
                    logger.error(f"Dialogue model API error: {response.status_code} - {response.text}")
                    return self.get_fallback_response()
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Dialogue model request timed out (attempt {attempt + 1}/{max_retries})")
                last_error = "Timeout"
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("Max retries reached for timeout")
                    return self.get_fallback_response()
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Dialogue model request failed: {str(e)} (attempt {attempt + 1}/{max_retries})")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error(f"Max retries reached for request exception: {str(e)}")
                    return self.get_fallback_response()
            
            except Exception as e:
                logger.error(f"Unexpected error in dialogue model: {str(e)}", exc_info=True)
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
