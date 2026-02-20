"""Tests for configuration and Firestore connection."""

import os
import pytest
from unittest.mock import patch, MagicMock
from backend.config import (
    Config,
    load_firebase_credentials,
    initialize_firestore,
    validate_firestore_connection
)


class TestConfig:
    """Test Config class."""
    
    def test_config_loads_from_env(self):
        """Test that Config loads values from environment variables."""
        with patch.dict(os.environ, {
            "HUGGINGFACE_API_TOKEN": "test_token",
            "FIREBASE_CREDENTIALS_PATH": "/path/to/creds.json"
        }):
            # Reload config values
            Config.HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
            Config.FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
            
            assert Config.HUGGINGFACE_API_TOKEN == "test_token"
            assert Config.FIREBASE_CREDENTIALS_PATH == "/path/to/creds.json"
    
    def test_config_validate_raises_on_missing_vars(self):
        """Test that validate raises ValueError when required vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            Config.HUGGINGFACE_API_TOKEN = ""
            Config.FIREBASE_CREDENTIALS_PATH = ""
            
            with pytest.raises(ValueError, match="Missing required environment variables"):
                Config.validate()


class TestFirebaseCredentials:
    """Test Firebase credentials loading."""
    
    def test_load_firebase_credentials_raises_on_missing_path(self):
        """Test that load_firebase_credentials raises ValueError when path is not set."""
        with patch.object(Config, 'FIREBASE_CREDENTIALS_PATH', ''):
            with pytest.raises(ValueError, match="FIREBASE_CREDENTIALS_PATH environment variable is not set"):
                load_firebase_credentials()
    
    def test_load_firebase_credentials_raises_on_missing_file(self):
        """Test that load_firebase_credentials raises FileNotFoundError when file doesn't exist."""
        with patch.object(Config, 'FIREBASE_CREDENTIALS_PATH', '/nonexistent/path.json'):
            with pytest.raises(FileNotFoundError, match="Firebase credentials file not found"):
                load_firebase_credentials()
    
    @patch('os.path.exists')
    @patch('firebase_admin.credentials.Certificate')
    def test_load_firebase_credentials_success(self, mock_cert, mock_exists):
        """Test successful Firebase credentials loading."""
        mock_exists.return_value = True
        mock_cert.return_value = MagicMock()
        
        with patch.object(Config, 'FIREBASE_CREDENTIALS_PATH', '/valid/path.json'):
            cred = load_firebase_credentials()
            
            mock_exists.assert_called_once_with('/valid/path.json')
            mock_cert.assert_called_once_with('/valid/path.json')
            assert cred is not None


class TestFirestoreInitialization:
    """Test Firestore initialization."""
    
    @patch('backend.config.load_firebase_credentials')
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.firestore.client')
    @patch('firebase_admin._apps', {})
    def test_initialize_firestore_success(self, mock_client, mock_init_app, mock_load_creds):
        """Test successful Firestore initialization."""
        mock_cred = MagicMock()
        mock_load_creds.return_value = mock_cred
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        
        db = initialize_firestore()
        
        mock_load_creds.assert_called_once()
        mock_init_app.assert_called_once_with(mock_cred)
        mock_client.assert_called_once()
        assert db == mock_db
    
    @patch('firebase_admin.firestore.client')
    @patch('firebase_admin._apps', {'default': MagicMock()})
    def test_initialize_firestore_already_initialized(self, mock_client):
        """Test Firestore initialization when app is already initialized."""
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        
        db = initialize_firestore()
        
        # Should not call initialize_app again
        mock_client.assert_called_once()
        assert db == mock_db
    
    @patch('backend.config.load_firebase_credentials')
    @patch('firebase_admin._apps', {})
    def test_initialize_firestore_failure(self, mock_load_creds):
        """Test Firestore initialization failure."""
        mock_load_creds.side_effect = Exception("Invalid credentials")
        
        with pytest.raises(Exception, match="Failed to initialize Firestore"):
            initialize_firestore()


class TestFirestoreValidation:
    """Test Firestore connection validation."""
    
    def test_validate_firestore_connection_success(self):
        """Test successful Firestore connection validation."""
        mock_db = MagicMock()
        mock_db.collections.return_value = [MagicMock()]
        
        result = validate_firestore_connection(mock_db)
        
        assert result is True
        mock_db.collections.assert_called_once_with(max_results=1)
    
    def test_validate_firestore_connection_failure(self):
        """Test Firestore connection validation failure."""
        mock_db = MagicMock()
        mock_db.collections.side_effect = Exception("Connection failed")
        
        result = validate_firestore_connection(mock_db)
        
        assert result is False
