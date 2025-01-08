import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .api.routes import router
from .core.config import settings
from .services.queue import queue_service

def ensure_directories():
    """Ensure required directories exist with proper permissions"""
    directories = ['/tmp/uploads', '/tmp/converted']
    for directory in directories:
        os.makedirs(directory, mode=0o777, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await queue_service.connect()
        logger.info("Gateway service started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize gateway service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    try:
        await queue_service.close()
        logger.info("Gateway service shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)