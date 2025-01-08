import aio_pika
import json
import logging
from typing import Optional
from datetime import datetime

from ..core.config import settings
from ..core.exceptions import QueueError

logger = logging.getLogger(__name__)

class QueueService:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    settings.RABBITMQ_URL,
                    timeout=settings.QUEUE_TIMEOUT
                )
                self.channel = await self.connection.channel()
                
                # Declare queues
                await self.channel.declare_queue(
                    settings.VIDEO_PROCESSING_QUEUE,
                    durable=True
                )
                await self.channel.declare_queue(
                    settings.NOTIFICATION_QUEUE,
                    durable=True
                )
                
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                raise QueueError("Failed to connect to message queue")

    async def publish_conversion_task(
        self,
        job_id: str,
        file_path: str,
        user_email: str
    ) -> None:
        """Publish video conversion task to queue"""
        try:
            if not self.channel or self.connection.is_closed:
                await self.connect()

            message = {
                "job_id": job_id,
                "file_path": file_path,
                "user_id": user_email,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=settings.VIDEO_PROCESSING_QUEUE
            )

            logger.info(f"Published conversion task: {job_id}")

        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            raise QueueError("Failed to queue conversion task")

    async def close(self) -> None:
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")

queue_service = QueueService()