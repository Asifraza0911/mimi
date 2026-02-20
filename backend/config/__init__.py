"""Configuration management for AI Waifu backend."""

import os
import logging
import sys
from typing import Optional
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

# Load environment variables from .env file
load_dotenv()


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the AI Waifu system.
    
    Sets up logging with:
    - Timestamp, logger name, log level, and message
    - Console output with color-coded levels
    - Configurable log level from environment
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter with timestamp and context
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("firebase_admin").setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger("ai_waifu.config")
    logger.info(f"Logging configured with level: {log_level}")


class Config:
    """Application configuration loaded from environment variables."""
    
    # HuggingFace API Configuration
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    
    # Discord Bot Configuration
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    
    # Application Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MEMORY_RETRIEVAL_COUNT: int = int(os.getenv("MEMORY_RETRIEVAL_COUNT", "3"))
    CONTEXT_WINDOW_SIZE: int = int(os.getenv("CONTEXT_WINDOW_SIZE", "5"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required environment variables are set."""
        missing = []
        
        if not cls.HUGGINGFACE_API_TOKEN:
            missing.append("HUGGINGFACE_API_TOKEN")
        
        if not cls.FIREBASE_CREDENTIALS_PATH:
            missing.append("FIREBASE_CREDENTIALS_PATH")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables and validate."""
        cls.validate()
        # Initialize logging with configured level
        setup_logging(cls.LOG_LEVEL)
        return cls()


def load_firebase_credentials() -> credentials.Certificate:
    """
    Load Firebase credentials from environment configuration.
    
    Returns:
        credentials.Certificate: Firebase credentials object
        
    Raises:
        ValueError: If credentials path is not set or file doesn't exist
        FileNotFoundError: If credentials file is not found
    """
    logger = logging.getLogger("ai_waifu.config")
    creds_path = Config.FIREBASE_CREDENTIALS_PATH
    
    if not creds_path:
        logger.error("FIREBASE_CREDENTIALS_PATH environment variable is not set")
        raise ValueError(
            "FIREBASE_CREDENTIALS_PATH environment variable is not set"
        )
    
    if not os.path.exists(creds_path):
        logger.error(f"Firebase credentials file not found at: {creds_path}")
        raise FileNotFoundError(
            f"Firebase credentials file not found at: {creds_path}"
        )
    
    logger.info(f"Loading Firebase credentials from: {creds_path}")
    return credentials.Certificate(creds_path)


def initialize_firestore() -> Client:
    """
    Initialize and return Firestore client.
    
    Returns:
        Client: Firestore client instance
        
    Raises:
        ValueError: If Firebase credentials are invalid
        Exception: If Firestore initialization fails
    """
    logger = logging.getLogger("ai_waifu.config")
    
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            logger.info("Initializing Firebase app")
            cred = load_firebase_credentials()
            firebase_admin.initialize_app(cred)
            logger.info("Firebase app initialized successfully")
        else:
            logger.debug("Firebase app already initialized")
        
        # Get Firestore client
        db = firestore.client()
        logger.info("Firestore client created successfully")
        
        return db
    
    except Exception as e:
        logger.error(f"Failed to initialize Firestore: {str(e)}")
        raise Exception(f"Failed to initialize Firestore: {str(e)}")


def validate_firestore_connection(db: Client) -> bool:
    """
    Validate Firestore connection by attempting a simple operation.
    
    Args:
        db: Firestore client instance
        
    Returns:
        bool: True if connection is valid, False otherwise
    """
    logger = logging.getLogger("ai_waifu.config")
    
    try:
        # Attempt to list collections (lightweight operation)
        # This will fail if connection is invalid
        collections = list(db.collections(max_results=1))
        logger.info("Firestore connection validated successfully")
        return True
    except Exception as e:
        logger.error(f"Firestore connection validation failed: {str(e)}")
        return False
