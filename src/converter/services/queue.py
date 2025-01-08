import aio_pika
import json
import logging
import asyncio
from typing import Optional
from datetime import datetime

from ..core.config import settings
from ..core.exceptions import QueueError
from .converter import converter_service

logger = logging.getLogger(__name__)

class QueueConsumer:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.processing_queue: Optional[aio_pika.Queue] = None
        self.notification_queue: Optional[aio_pika.Queue] = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            # Connect to RabbitMQ
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=30
            )
            
            # Create channel
            self.channel = await self.connection.channel()
            
            # Declare queues
            self.processing_queue = await self.channel.declare_queue(
                settings.QUEUE_NAME,
                durable=True
            )
            
            self.notification_queue = await self.channel.declare_queue(
                settings.NOTIFICATION_QUEUE,
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise QueueError(str(e))

    async def publish_notification(self, user_id: str, job_id: str, status: str, error: Optional[str] = None) -> None:
        """Publish notification message"""
        try:
            message = {
                "user_id": user_id,
                "job_id": job_id,
                "status": status,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=settings.NOTIFICATION_QUEUE
            )
            
            logger.info(f"Published notification for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish notification: {str(e)}")

    async def process_message(self, message: aio_pika.IncomingMessage) -> None:
        """Process incoming conversion request"""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                job_id = body["job_id"]
                file_path = body["file_path"]
                user_id = body["user_id"]

                logger.info(f"Processing conversion job: {job_id}")

                # Process video conversion
                result = await converter_service.process_video(
                    job_id=job_id,
                    file_path=file_path,
                    user_id=user_id
                )

                # Send notification
                await self.publish_notification(
                    user_id=user_id,
                    job_id=job_id,
                    status="completed" if result["success"] else "failed",
                    error=result.get("error")
                )

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Send error notification
                if 'job_id' in locals() and 'user_id' in locals():
                    await self.publish_notification(
                        user_id=user_id,
                        job_id=job_id,
                        status="failed",
                        error=str(e)
                    )

    async def start_consuming(self) -> None:
        """Start consuming messages"""
        try:
            await self.connect()
            
            async with self.processing_queue.iterator() as queue_iter:
                logger.info("Started consuming messages")
                async for message in queue_iter:
                    await self.process_message(message)
                    
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}")
            raise

    async def close(self) -> None:
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")

queue_consumer = QueueConsumer()