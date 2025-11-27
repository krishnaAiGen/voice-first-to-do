"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import voice, tasks, auth, chat
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice-First To-Do API",
    description="Voice-controlled to-do list with authentication and chat history",
    version="2.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")  # Auth endpoints (no auth required)
app.include_router(chat.router, prefix="/api")  # Chat history (requires auth)
app.include_router(voice.router, prefix="/api")  # Voice commands (requires auth)
app.include_router(tasks.router, prefix="/api")  # Task management (requires auth)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice-First To-Do API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting Voice-First To-Do API")
    logger.info(f"Environment: {settings.environment}")
    
    # Warm up database connection pool
    try:
        from app.clients.database_client import db_client
        from sqlalchemy import text
        async with db_client.async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection pool warmed up")
    except Exception as e:
        logger.warning(f"Failed to warm up connection pool: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down Voice-First To-Do API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3002,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )

