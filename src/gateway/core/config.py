from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Set
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MP3 Converter Gateway Service"
    
    # External Service URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001/api/v1")
    
    # RabbitMQ Configuration
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # Queue Names
    VIDEO_PROCESSING_QUEUE: str = "video_processing"
    NOTIFICATION_QUEUE: str = "notifications"
    
    # File Upload Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: Set[str] = {".mp4", ".avi", ".mkv", ".mov"}

    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "converter_db")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "conversions")
    
    # Service Timeouts
    AUTH_TIMEOUT: int = 5  # seconds
    QUEUE_TIMEOUT: int = 10  # seconds

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()