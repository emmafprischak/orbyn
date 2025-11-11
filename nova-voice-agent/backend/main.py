"""
Nova Voice Agent - Main Application
FastAPI backend for AI-powered voice agent
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import health, webhooks
from backend.config import HOST, PORT

# Create FastAPI application
app = FastAPI(
    title="Nova Voice Agent",
    description="AI-powered voice agent for Orbyn.ai",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, tags=["Health"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print("=" * 60)
    print("🚀 Nova Voice Agent Starting...")
    print("=" * 60)
    print(f"📱 Phone Number: +1 (814) 568-5796")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print(f"📝 Health Check: http://{HOST}:{PORT}/health")
    print(f"🔗 Webhooks: http://{HOST}:{PORT}/webhooks/voice/incoming")
    print("=" * 60)
    print("✅ Ready to receive calls!")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print("\n" + "=" * 60)
    print("👋 Nova Voice Agent Shutting Down...")
    print("=" * 60)


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
