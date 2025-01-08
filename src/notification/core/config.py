from typing import Dict
from pydantic import EmailStr
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Service name
    SERVICE_NAME: str = "MP3 Converter Notification Service"
    
    # RabbitMQ Settings
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    NOTIFICATION_QUEUE: str = "notifications"
    
    # MongoDB Settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "notification_db")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "notifications")
    
    # Email Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "your-app-specific-password")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
    
    # Email Templates
    EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {
        "processing": {
            "subject": "Video Conversion Started",
            "template": """
            Your video conversion has started.
            Job ID: {job_id}
            We'll notify you when it's complete.
            """
        },
        "completed": {
            "subject": "Video Conversion Completed",
            "template": """
            Your video has been successfully converted to MP3.
            Job ID: {job_id}
            You can now download your converted file.
            """
        },
        "failed": {
            "subject": "Video Conversion Failed",
            "template": """
            Sorry, we couldn't convert your video.
            Job ID: {job_id}
            Error: {error}
            Please try again or contact support if the issue persists.
            """
        }
    }

    class Config:
        case_sensitive = True

settings = Settings()