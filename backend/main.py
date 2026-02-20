"""
FastAPI main application for AI Waifu Cross-Platform System.

This module initializes the FastAPI application and defines the REST API endpoints
for client communication. It serves as the entry point for the AI_Brain backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
import logging

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


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service availability.
    
    Returns:
        dict: Service status information
    """
    return {
        "status": "healthy",
        "service": "AI Waifu Backend",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return AI response.
    
    This endpoint accepts a user message from any client platform (web or Discord),
    processes it through the AI pipeline, and returns a contextually-aware response
    with updated relationship metrics.
    
    Args:
        request: ChatRequest containing user_id, message, and platform
        
    Returns:
        ChatResponse with reply, affection_level, and mood
        
    Raises:
        HTTPException: On validation or processing errors
    """
    try:
        logger.info(f"Received chat request from user {request.user_id} on {request.platform}")
        
        # TODO: Implement response pipeline integration
        # For now, return a placeholder response
        return ChatResponse(
            reply="H-hey! The system is still being set up... Don't expect too much from me yet, baka!",
            affection_level=10,
            mood="neutral"
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        # Return graceful error response (Requirement 15.7)
        return ChatResponse(
            reply="Hmph! Something went wrong... It's not like I care or anything!",
            affection_level=10,
            mood="neutral"
        )


@app.on_event("startup")
async def startup_event():
    """
    Initialize services on application startup.
    
    This will be expanded to initialize:
    - Firebase Firestore connection
    - Memory Engine with FAISS
    - All processing modules
    """
    logger.info("Starting AI Waifu Backend...")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup resources on application shutdown.
    """
    logger.info("Shutting down AI Waifu Backend...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
