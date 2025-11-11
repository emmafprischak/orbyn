"""
Health Check Routes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Status information
    """
    return {
        "status": "healthy",
        "service": "Nova Voice Agent"
    }


@router.get("/")
async def root():
    """
    Root endpoint with API information

    Returns:
        API information
    """
    return {
        "name": "Nova Voice Agent API",
        "version": "1.0.0",
        "description": "AI-powered voice agent for Orbyn.ai",
        "endpoints": {
            "health": "/health",
            "incoming_call": "/webhooks/voice/incoming",
            "process_speech": "/webhooks/voice/process",
            "book_appointment": "/webhooks/voice/book",
            "call_status": "/webhooks/voice/status"
        }
    }
