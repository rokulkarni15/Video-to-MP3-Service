import aio_pika
import json
import logging
from typing import Optional
from datetime import datetime

from ..core.config import settings
from .email import email_service

logger = logging.getLogger(__name__)

class QueueConsumer:
   def __init__(self):
       self.connection: Optional[aio_pika.Connection] = None
       self.channel: Optional[aio_pika.Channel] = None
       self.email_service = email_service

   async def connect(self) -> None:
       """Establish connection to RabbitMQ"""
       if not self.connection or self.connection.is_closed:
           self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
           self.channel = await self.connection.channel()
           
           # Declare notification queue
           await self.channel.declare_queue(
               settings.NOTIFICATION_QUEUE,
               durable=True
           )
           
           logger.info("Connected to RabbitMQ")

   async def process_message(self, message: aio_pika.IncomingMessage):
       """Process incoming notification message"""
       async with message.process():
           try:
               # Parse message
               body = json.loads(message.body.decode())
               logger.info(f"Processing notification: {body}")
               
               # Extract message details
               job_id = body.get("job_id")
               user_id = body.get("user_id")
               status = body.get("status")
               error = body.get("error")
               
               if not all([job_id, user_id, status]):
                   logger.error("Missing required fields in message")
                   return

               # Validate email address
               if not isinstance(user_id, str) or '@' not in user_id:
                   logger.error(f"Invalid email address received: {user_id}")
                   return
               
               # Send notification
               success = await self.email_service.notify_conversion_status(
                   email=user_id,
                   job_id=job_id,
                   status=status,
                   error=error
               )
               
               if success:
                   logger.info(f"Successfully sent notification for job {job_id}")
               else:
                   logger.error(f"Failed to send notification for job {job_id}")
               
           except json.JSONDecodeError as e:
               logger.error(f"Invalid JSON message: {str(e)}")
           except Exception as e:
               logger.error(f"Error processing notification: {str(e)}")

   async def start_consuming(self) -> None:
       """Start consuming notification messages"""
       try:
           await self.connect()
           
           queue = await self.channel.declare_queue(
               settings.NOTIFICATION_QUEUE,
               durable=True
           )
           
           async with queue.iterator() as queue_iter:
               logger.info("Started consuming notification messages")
               async for message in queue_iter:
                   await self.process_message(message)
                   
       except Exception as e:
           logger.error(f"Error consuming messages: {str(e)}")
           raise

   async def close(self) -> None:
       """Close RabbitMQ connection"""
       try:
           if self.connection and not self.connection.is_closed:
               await self.connection.close()
               logger.info("Closed RabbitMQ connection")
       except Exception as e:
           logger.error(f"Error closing connection: {str(e)}")

queue_consumer = QueueConsumer()