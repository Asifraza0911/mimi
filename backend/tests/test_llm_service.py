"""
Tests for LLM Service Module

This module tests the LLM service's ability to accept temperature parameters,
pass them to the HuggingFace API, log temperature values, handle API errors,
and implement retry logic for transient failures.

Requirements: 13.2, 13.3, 13.4, 19.3, 19.10, 19.11
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import requests
from backend.modules.llm_service import LLMService, LLMServiceError


class TestLLMServiceTemperature:
    """Test suite for LLM service temperature parameter handling."""
    
    def test_generate_response_accepts_temperature_parameter(self):
        """
        Test that generate_response accepts temperature parameter.
        
        Requirements: 19.3
        """
        llm_service = LLMService(api_token="test_token")
        
        # Mock the requests.post to avoid actual API calls
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Test response"}]
            mock_post.return_value = mock_response
            
            # Call with custom temperature
            result = llm_service.generate_response(
                prompt="Test prompt",
                temperature=0.8
            )
            
            # Verify the method accepts the parameter and completes
            assert result == "Test response"
    
    def test_generate_response_passes_temperature_to_api(self):
        """
        Test that temperature is passed to HuggingFace API request.
        
        Requirements: 19.10
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Test response"}]
            mock_post.return_value = mock_response
            
            # Call with specific temperature
            llm_service.generate_response(
                prompt="Test prompt",
                temperature=0.9
            )
            
            # Verify temperature was passed in the API request
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert 'parameters' in payload
            assert 'temperature' in payload['parameters']
            assert payload['parameters']['temperature'] == 0.9
    
    def test_generate_response_logs_temperature(self, caplog):
        """
        Test that temperature value is logged for each generation.
        
        Requirements: 19.11
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Test response"}]
            mock_post.return_value = mock_response
            
            # Call with specific temperature
            with caplog.at_level('INFO'):
                llm_service.generate_response(
                    prompt="Test prompt",
                    temperature=0.7
                )
            
            # Verify temperature was logged
            assert any("temperature: 0.7" in record.message for record in caplog.records)
    
    def test_generate_response_default_temperature(self):
        """
        Test that default temperature is 0.7 when not specified.
        
        Requirements: 19.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Test response"}]
            mock_post.return_value = mock_response
            
            # Call without temperature parameter
            llm_service.generate_response(prompt="Test prompt")
            
            # Verify default temperature (0.7) was used
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert payload['parameters']['temperature'] == 0.7
    
    def test_generate_response_with_different_temperatures(self):
        """
        Test that different temperature values are correctly passed.
        
        Requirements: 19.10
        """
        llm_service = LLMService(api_token="test_token")
        
        test_temperatures = [0.3, 0.4, 0.5, 0.7, 0.8, 0.9]
        
        for temp in test_temperatures:
            with patch('backend.modules.llm_service.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = [{"generated_text": "Test"}]
                mock_post.return_value = mock_response
                
                llm_service.generate_response(
                    prompt="Test prompt",
                    temperature=temp
                )
                
                # Verify correct temperature was passed
                call_args = mock_post.call_args
                payload = call_args[1]['json']
                assert payload['parameters']['temperature'] == temp
    
    def test_fallback_response_on_api_error(self):
        """
        Test that fallback response is returned on API errors.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(
                prompt="Test prompt",
                temperature=0.7
            )
            
            # Verify fallback response is returned
            assert result in llm_service.fallback_responses
    
    def test_api_request_includes_required_parameters(self):
        """
        Test that API request includes all required parameters.
        
        Requirements: 13.2, 19.10
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Test"}]
            mock_post.return_value = mock_response
            
            llm_service.generate_response(
                prompt="Test prompt",
                max_length=150,
                temperature=0.8
            )
            
            # Verify all required parameters are present
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            
            assert 'inputs' in payload
            assert payload['inputs'] == "Test prompt"
            assert 'parameters' in payload
            assert payload['parameters']['max_new_tokens'] == 150  # Changed from max_length
            assert payload['parameters']['temperature'] == 0.8
            assert payload['parameters']['do_sample'] is True


class TestLLMServiceAPICall:
    """Test suite for LLM service API call functionality with mocked responses."""
    
    def test_successful_api_call_returns_generated_text(self):
        """
        Test that successful API call returns generated text.
        
        Requirements: 13.2, 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Hello! How are you?"}]
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test prompt")
            
            assert result == "Hello! How are you?"
            assert mock_post.call_count == 1
    
    def test_api_call_with_correct_headers(self):
        """
        Test that API call includes correct authentication headers.
        
        Requirements: 13.2, 13.5
        """
        llm_service = LLMService(api_token="my_secret_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Response"}]
            mock_post.return_value = mock_response
            
            llm_service.generate_response(prompt="Test")
            
            # Verify headers
            call_args = mock_post.call_args
            headers = call_args[1]['headers']
            assert headers['Authorization'] == "Bearer my_secret_token"
            assert headers['Content-Type'] == "application/json"
    
    def test_api_call_with_correct_url(self):
        """
        Test that API call uses correct HuggingFace endpoint.
        
        Requirements: 13.2
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Response"}]
            mock_post.return_value = mock_response
            
            llm_service.generate_response(prompt="Test")
            
            # Verify URL
            call_args = mock_post.call_args
            url = call_args[0][0]
            assert url == "https://api-inference.huggingface.co/models/google/flan-t5-large"
    
    def test_api_call_with_timeout(self):
        """
        Test that API call includes timeout parameter.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "Response"}]
            mock_post.return_value = mock_response
            
            llm_service.generate_response(prompt="Test")
            
            # Verify timeout is set
            call_args = mock_post.call_args
            assert call_args[1]['timeout'] == 30
    
    def test_api_response_text_is_stripped(self):
        """
        Test that generated text is stripped of whitespace.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "  Response with spaces  \n"}]
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test")
            
            assert result == "Response with spaces"
    
    def test_unexpected_response_format_returns_fallback(self):
        """
        Test that unexpected API response format returns fallback.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}  # Unexpected format
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test")
            
            assert result in llm_service.fallback_responses


class TestLLMServiceFallbackOnErrors:
    """Test suite for LLM service fallback responses on various API errors."""
    
    def test_fallback_on_503_service_unavailable(self):
        """
        Test that 503 error returns fallback after retries.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Service Unavailable"
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test", max_retries=3)
            
            # Should retry 3 times then return fallback
            assert mock_post.call_count == 3
            assert result in llm_service.fallback_responses
    
    def test_fallback_on_500_internal_server_error(self):
        """
        Test that 500 error returns fallback after retries.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test", max_retries=2)
            
            # Should retry 2 times then return fallback
            assert mock_post.call_count == 2
            assert result in llm_service.fallback_responses
    
    def test_fallback_on_timeout_error(self):
        """
        Test that timeout error returns fallback after retries.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
            
            result = llm_service.generate_response(prompt="Test", max_retries=3)
            
            # Should retry 3 times then return fallback
            assert mock_post.call_count == 3
            assert result in llm_service.fallback_responses
    
    def test_fallback_on_connection_error(self):
        """
        Test that connection error returns fallback after retries.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = llm_service.generate_response(prompt="Test", max_retries=2)
            
            # Should retry 2 times then return fallback
            assert mock_post.call_count == 2
            assert result in llm_service.fallback_responses
    
    def test_fallback_on_request_exception(self):
        """
        Test that generic request exception returns fallback after retries.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Network error")
            
            result = llm_service.generate_response(prompt="Test", max_retries=3)
            
            # Should retry 3 times then return fallback
            assert mock_post.call_count == 3
            assert result in llm_service.fallback_responses
    
    def test_no_retry_on_401_authentication_error(self):
        """
        Test that 401 error returns fallback without retry.
        
        The implementation raises LLMServiceError but catches it in the
        generic exception handler and returns a fallback response.
        
        Requirements: 13.4, 13.5
        """
        llm_service = LLMService(api_token="invalid_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test")
            
            # Should not retry on authentication error
            assert mock_post.call_count == 1
            # Should return fallback response
            assert result in llm_service.fallback_responses
    
    def test_no_retry_on_400_client_error(self):
        """
        Test that 400 error returns fallback without retry.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test")
            
            # Should not retry on client error
            assert mock_post.call_count == 1
            assert result in llm_service.fallback_responses
    
    def test_fallback_on_unexpected_exception(self):
        """
        Test that unexpected exception returns fallback without retry.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = ValueError("Unexpected error")
            
            result = llm_service.generate_response(prompt="Test")
            
            # Should not retry on unexpected error
            assert mock_post.call_count == 1
            assert result in llm_service.fallback_responses
    
    def test_fallback_response_is_random(self):
        """
        Test that fallback responses are randomly selected.
        
        Requirements: 13.4
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Error"
            mock_post.return_value = mock_response
            
            # Get multiple fallback responses
            responses = set()
            for _ in range(20):
                result = llm_service.generate_response(prompt="Test", max_retries=1)
                responses.add(result)
            
            # Should get at least 2 different responses (probabilistic test)
            assert len(responses) >= 2
            # All responses should be from fallback list
            for response in responses:
                assert response in llm_service.fallback_responses


class TestLLMServiceRetryLogic:
    """Test suite for LLM service retry logic on transient failures."""
    
    def test_retry_on_503_model_loading(self):
        """
        Test that 503 errors trigger retry attempts.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Model is loading"
            mock_post.return_value = mock_response
            
            llm_service.generate_response(prompt="Test", max_retries=3)
            
            # Should attempt 3 times
            assert mock_post.call_count == 3
    
    def test_retry_on_500_server_error(self):
        """
        Test that 500 errors trigger retry attempts.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            llm_service.generate_response(prompt="Test", max_retries=5)
            
            # Should attempt 5 times
            assert mock_post.call_count == 5
    
    def test_retry_on_timeout(self):
        """
        Test that timeout errors trigger retry attempts.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Timeout")
            
            llm_service.generate_response(prompt="Test", max_retries=4)
            
            # Should attempt 4 times
            assert mock_post.call_count == 4
    
    def test_retry_on_network_error(self):
        """
        Test that network errors trigger retry attempts.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
            
            llm_service.generate_response(prompt="Test", max_retries=2)
            
            # Should attempt 2 times
            assert mock_post.call_count == 2
    
    def test_success_after_retry(self):
        """
        Test that successful response is returned after failed attempts.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            # First two calls fail, third succeeds
            fail_response = Mock()
            fail_response.status_code = 503
            fail_response.text = "Model loading"
            
            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = [{"generated_text": "Success!"}]
            
            mock_post.side_effect = [fail_response, fail_response, success_response]
            
            result = llm_service.generate_response(prompt="Test", max_retries=3)
            
            # Should succeed on third attempt
            assert result == "Success!"
            assert mock_post.call_count == 3
    
    def test_success_on_first_attempt_no_retry(self):
        """
        Test that no retry occurs when first attempt succeeds.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"generated_text": "First try success"}]
            mock_post.return_value = mock_response
            
            result = llm_service.generate_response(prompt="Test", max_retries=5)
            
            # Should only call once
            assert result == "First try success"
            assert mock_post.call_count == 1
    
    def test_retry_respects_max_retries_parameter(self):
        """
        Test that retry logic respects max_retries parameter.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Model loading"
            mock_post.return_value = mock_response
            
            # Test with different max_retries values
            for max_retries in [1, 2, 3, 5]:
                mock_post.reset_mock()
                llm_service.generate_response(prompt="Test", max_retries=max_retries)
                assert mock_post.call_count == max_retries
    
    def test_mixed_transient_errors_with_retry(self):
        """
        Test retry logic with mixed transient error types.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            # Mix of different transient errors
            error_503 = Mock()
            error_503.status_code = 503
            error_503.text = "Model loading"
            
            error_500 = Mock()
            error_500.status_code = 500
            error_500.text = "Server error"
            
            timeout_error = requests.exceptions.Timeout("Timeout")
            
            success = Mock()
            success.status_code = 200
            success.json.return_value = [{"generated_text": "Finally!"}]
            
            mock_post.side_effect = [error_503, timeout_error, error_500, success]
            
            result = llm_service.generate_response(prompt="Test", max_retries=4)
            
            # Should succeed after 4 attempts
            assert result == "Finally!"
            assert mock_post.call_count == 4
    
    def test_default_max_retries_is_three(self):
        """
        Test that default max_retries is 3.
        
        Requirements: 13.3
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.text = "Model loading"
            mock_post.return_value = mock_response
            
            # Call without specifying max_retries
            llm_service.generate_response(prompt="Test")
            
            # Should default to 3 retries
            assert mock_post.call_count == 3


class TestLLMServiceTemperatureHandling:
    """Test suite for temperature parameter handling across different scenarios."""
    
    def test_temperature_preserved_across_retries(self):
        """
        Test that temperature parameter is preserved across retry attempts.
        
        Requirements: 19.3, 19.10
        """
        llm_service = LLMService(api_token="test_token")
        
        with patch('backend.modules.llm_service.requests.post') as mock_post:
            fail_response = Mock()
            fail_response.status_code = 503
            fail_response.text = "Model loading"
            
            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = [{"generated_text": "Success"}]
            
            mock_post.side_effect = [fail_response, success_response]
            
            llm_service.generate_response(prompt="Test", temperature=0.85, max_retries=2)
            
            # Check that temperature was passed in both attempts
            for call_args in mock_post.call_args_list:
                payload = call_args[1]['json']
                assert payload['parameters']['temperature'] == 0.85
    
    def test_temperature_range_validation(self):
        """
        Test that various temperature values are accepted.
        
        Requirements: 19.10
        """
        llm_service = LLMService(api_token="test_token")
        
        # Test edge cases and typical values
        test_temps = [0.0, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        for temp in test_temps:
            with patch('backend.modules.llm_service.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = [{"generated_text": "Test"}]
                mock_post.return_value = mock_response
                
                result = llm_service.generate_response(prompt="Test", temperature=temp)
                
                # Should succeed with any valid temperature
                assert result == "Test"
                call_args = mock_post.call_args
                payload = call_args[1]['json']
                assert payload['parameters']['temperature'] == temp
