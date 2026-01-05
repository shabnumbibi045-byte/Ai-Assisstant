"""Main FastAPI Application - Salim AI Assistant.

A comprehensive AI assistant for:
- Multi-country banking (Canada, US, Kenya)
- Stock portfolio management
- Travel booking with continuous price monitoring
- Legal research (Canada & US)
- Document management
- Voice commands
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import chat, memory, rag, tools, setup
from app.routers.voice import router as voice_router
from app.routers.auth import router as auth_router
from app.routers.plaid import router as plaid_router
from app.routers.banking import router as banking_router
from app.routers.stocks import router as stocks_router
from app.routers.travel import router as travel_router
from app.routers.research import router as research_router
from app.routers.dashboard import router as dashboard_router
from app.database.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AnIntelligentAI Backend...")
    
    # Startup - Initialize database
    try:
        await db_manager.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await db_manager.close()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS
)

# Include routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(memory.router, prefix=settings.API_PREFIX)
app.include_router(rag.router, prefix=settings.API_PREFIX)
app.include_router(tools.router, prefix=settings.API_PREFIX)
app.include_router(setup.router, prefix=settings.API_PREFIX)
app.include_router(voice_router, prefix=settings.API_PREFIX)
app.include_router(plaid_router, prefix=settings.API_PREFIX)
app.include_router(banking_router, prefix=settings.API_PREFIX)
app.include_router(stocks_router, prefix=settings.API_PREFIX)
app.include_router(travel_router, prefix=settings.API_PREFIX)
app.include_router(research_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for deployment platforms."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
