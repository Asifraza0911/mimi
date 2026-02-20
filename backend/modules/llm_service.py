"""
LLM Service Module

This module interfaces with the HuggingFace Inference API to generate responses
using the google/flan-t5-large model. It handles API authentication, request
formatting, retries, and provides fallback responses for error cases.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 19.3, 19.10, 19.11
"""

import requests
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Exception raised for LLM service errors."""
    pass


class LLMService:
    """
    Interface with HuggingFace Inference API for text generation.
    
    This service manages communication with the HuggingFace API, including
    authentication, request formatting, error handling, and fallback responses.
    It accepts a temperature parameter to control response randomness based on mood.
    
    Attributes:
        api_token (str): HuggingFace API authentication token
        model (str): Model identifier (google/flan-t5-large)
        api_url (str): Full API endpoint URL
        fallback_responses (list): Predefined responses for error cases
    """
    
    def __init__(self, api_token: str):
        """
        Initialize LLM Service with API credentials.
        
        Args:
            api_token: HuggingFace API token from environment configuration
            
        Requirements: 13.5
        """
        self.api_token = api_token
        self.model = "google/flan-t5-large"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.fallback_responses = [
            "H-hey! Don't ignore me like that!",
            "Hmph, I'm not talking to you right now...",
            "W-what? I wasn't waiting for you or anything!",
            "Baka! Something's not working right...",
            "D-don't look at me like that! I'm trying my best!"
        ]
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    def generate_response(
        self,
        prompt: str,
        max_length: int = 150,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        Generate text response from LLM with temperature control and retry logic.
        
        This method sends the constructed prompt to the HuggingFace API with
        the specified temperature parameter to control response randomness.
        Temperature is determined by the Temperature Scaling System based on
        current mood state. Implements retry logic for transient failures.
        
        Args:
            prompt: Complete prompt with personality and context
            max_length: Maximum response length in tokens (default: 150)
            temperature: Randomness control (0.0-1.0, default: 0.7)
                - Lower values (0.3-0.4): More controlled, predictable responses
                - Medium values (0.5-0.7): Standard to playful variation
                - Higher values (0.8-0.9): More chaotic, emotional responses
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Generated response text from the LLM
            
        Raises:
            LLMServiceError: On API failures after retries
            
        Requirements: 13.2, 13.3, 19.3, 19.10, 19.11
        """
        # Log temperature value used for generation (Requirement 19.11)
        logger.info(f"Generating response with temperature: {temperature}")
        
        # Prepare request headers
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare request payload with temperature parameter (Requirement 19.10)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": temperature,
                "do_sample": True,  # Enable sampling for temperature to take effect
                "top_p": 0.9,
                "repetition_penalty": 1.2
            }
        }
        
        # Retry loop for handling transient failures
        last_error = None
        for attempt in range(max_retries):
            try:
                # Send request to HuggingFace API
                logger.debug(f"Sending request to HuggingFace API (attempt {attempt + 1}/{max_retries}): {self.api_url}")
                response = requests.post(
                    self.api_url,
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
                        logger.info(f"Successfully generated response (length: {len(generated_text)})")
                        return generated_text.strip()
                    else:
                        logger.warning("Unexpected response format from HuggingFace API")
                        return self.get_fallback_response()
                
                # Handle API errors
                elif response.status_code == 503:
                    # Model loading - retry
                    logger.warning(f"HuggingFace model is loading (attempt {attempt + 1}/{max_retries})")
                    last_error = "Model loading"
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error("Max retries reached for model loading")
                        return self.get_fallback_response()
                
                elif response.status_code == 401:
                    # Authentication error - don't retry
                    logger.error("HuggingFace API authentication failed")
                    raise LLMServiceError("Invalid API token")
                
                elif response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"HuggingFace API server error: {response.status_code} (attempt {attempt + 1}/{max_retries})")
                    last_error = f"Server error: {response.status_code}"
                    if attempt < max_retries - 1:
                        continue
                    else:
                        logger.error(f"Max retries reached for server error: {response.text}")
                        return self.get_fallback_response()
                
                else:
                    # Client error - don't retry
                    logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                    return self.get_fallback_response()
                    
            except requests.exceptions.Timeout:
                # Timeout - retry
                logger.warning(f"HuggingFace API request timed out (attempt {attempt + 1}/{max_retries})")
                last_error = "Timeout"
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error("Max retries reached for timeout")
                    return self.get_fallback_response()
            
            except requests.exceptions.RequestException as e:
                # Network error - retry
                logger.warning(f"HuggingFace API request failed: {str(e)} (attempt {attempt + 1}/{max_retries})")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
                else:
                    logger.error(f"Max retries reached for request exception: {str(e)}")
                    return self.get_fallback_response()
            
            except Exception as e:
                # Unexpected error - don't retry
                logger.error(f"Unexpected error in LLM service: {str(e)}", exc_info=True)
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
