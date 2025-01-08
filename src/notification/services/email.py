import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional
import motor.motor_asyncio
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Initialize MongoDB connection
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db[settings.MONGODB_COLLECTION]

    async def send_email(self, to_email: str, subject: str, body: str, job_id: str) -> bool:
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = str(settings.SMTP_FROM_EMAIL)  # Convert to string
            message["To"] = str(to_email)  # Convert to string
            message["Subject"] = str(subject)
            message.attach(MIMEText(str(body), "plain"))  # Convert body to string

            # Send email using SMTP
            await aiosmtplib.send(
                message=message,  # Pass the complete message object
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=True
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    async def log_notification(
        self,
        job_id: str,
        email: str,
        status: str,
        subject: str,
        error: Optional[str] = None
    ) -> None:
        """Log notification details to MongoDB"""
        log_entry = {
            "job_id": job_id,
            "email": email,
            "subject": subject,
            "status": status,
            "timestamp": datetime.utcnow(),
            "error": error
        }
        
        await self.collection.insert_one(log_entry)

    def get_template(self, status: str, context: dict) -> tuple[str, str]:
        """Get email template for given status"""
        template_config = settings.EMAIL_TEMPLATES.get(status, {
            "subject": "Video Conversion Update",
            "template": "Update on your video conversion. Job ID: {job_id}"
        })
        
        subject = template_config["subject"]
        body = template_config["template"].format(**context)
        
        return subject, body

    async def notify_conversion_status(
        self,
        email: str,
        job_id: str,
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """Send conversion status notification"""
        context = {
            "job_id": job_id,
            "error": error or "Unknown error"
        }
        
        subject, body = self.get_template(status, context)
        
        return await self.send_email(
            to_email=email,
            subject=subject,
            body=body,
            job_id=job_id
        )

email_service = EmailService()