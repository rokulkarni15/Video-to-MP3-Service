from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Service name
    SERVICE_NAME: str = "MP3 Converter Service"
    
    # RabbitMQ Settings
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    QUEUE_NAME: str = "video_processing"
    NOTIFICATION_QUEUE: str = "notifications"
    
    # MongoDB Settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "converter_db")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "conversions")
    
    # File Storage Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/tmp/converted")
    
    # FFmpeg Settings
    FFMPEG_AUDIO_CODEC: str = "libmp3lame"
    FFMPEG_AUDIO_BITRATE: str = "192k"
    FFMPEG_SAMPLE_RATE: str = "44100"
    
    # Processing Settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    MAX_WORKERS: int = 3

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()