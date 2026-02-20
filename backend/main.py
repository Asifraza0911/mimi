"""
FastAPI main application for AI Waifu Cross-Platform System.

This module initializes the FastAPI application and defines the REST API endpoints
for client communication. It serves as the entry point for the AI_Brain backend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from container import ServiceContainer
from config import Config
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="AI Waifu Cross-Platform System",
    description="Centralized AI backend for Mimi, the tsundere anime girl character",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service container (initialized on startup)
service_container: ServiceContainer = None


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service availability.
    
    Performs health checks on all critical services:
    - Firestore database connection
    - LLM service availability
    - Memory engine readiness
    
    Returns:
        dict: Service status information with individual component health
    """
    if service_container is None:
        return {
            "status": "initializing",
            "service": "AI Waifu Backend",
            "version": "1.0.0"
        }
    
    # Get health status from service container
    health_status = service_container.health_check()
    
    # Determine overall status
    all_healthy = all(
        status in ["connected", "available", "ready"] 
        for status in health_status.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "AI Waifu Backend",
        "version": "1.0.0",
        "services": health_status
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return AI response.
    
    This endpoint accepts a user message from any client platform (web or Discord),
    processes it through the complete AI pipeline including:
    - Affection decay based on time since last interaction
    - Interaction streak tracking and penalties
    - Emotion detection and mood updates
    - Relationship progression and attachment style updates
    - Memory retrieval with importance weighting
    - Callback memory injection
    - Personality-driven prompt construction
    - Temperature-scaled LLM response generation
    
    Args:
        request: ChatRequest containing user_id, message, and platform
        
    Returns:
        ChatResponse with reply, affection_level, mood, and relationship_stage
        
    Raises:
        HTTPException: On validation or processing errors
    """
    try:
        logger.info(f"Received chat request from user {request.user_id} on {request.platform}")
        
        # Ensure service container is initialized
        if service_container is None:
            logger.error("Service container not initialized")
            return ChatResponse(
                reply="H-hey! The system is still starting up... Wait a moment, baka!",
                affection_level=10,
                mood="neutral"
            )
        
        # Process message through response pipeline
        response = await service_container.get_response_pipeline().process_message(
            user_id=request.user_id,
            message=request.message,
            platform=request.platform
        )
        
        logger.info(f"Successfully processed message for user {request.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        # Return graceful error response (Requirement 15.7)
        return ChatResponse(
            reply="Hmph! Something went wrong... It's not like I care or anything!",
            affection_level=10,
            mood="neutral"
        )


async def cleanup_inactive_sessions():
    """
    Background task to periodically clean up inactive session contexts.
    
    Runs every 30 minutes to remove session contexts that have been
    inactive for more than 30 minutes, freeing up memory.
    """
    while True:
        try:
            await asyncio.sleep(1800)  # Sleep for 30 minutes
            
            if service_container is not None:
                logger.info("Running session cleanup task")
                service_container.get_response_pipeline().clear_inactive_sessions()
                logger.info("Session cleanup completed")
        except Exception as e:
            logger.error(f"Error in session cleanup task: {str(e)}", exc_info=True)


@app.on_event("startup")
async def startup_event():
    """
    Initialize services on application startup.
    
    Initializes:
    - Configuration from environment variables
    - ServiceContainer with all modules
    - Firebase Firestore connection
    - Memory Engine with FAISS
    - All processing modules (Emotion, Personality, Relationship, etc.)
    - Background task for session cleanup
    """
    global service_container
    
    logger.info("Starting AI Waifu Backend...")
    
    try:
        # Load configuration
        logger.info("Loading configuration")
        config = Config()
        
        # Initialize service container
        logger.info("Initializing service container")
        service_container = ServiceContainer(config)
        
        # Start background task for session cleanup
        logger.info("Starting background session cleanup task")
        asyncio.create_task(cleanup_inactive_sessions())
        
        logger.info("Application startup complete - All systems ready!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup resources on application shutdown.
    """
    logger.info("Shutting down AI Waifu Backend...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
