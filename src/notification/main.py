import asyncio
import logging
import signal
from typing import Set
import sys

from .services.queue import queue_consumer
from .core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.tasks: Set[asyncio.Task] = set()

    async def start(self):
        """Start the notification service"""
        try:
            # Setup signal handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                asyncio.get_event_loop().add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self.shutdown(sig))
                )

            logger.info("Starting Notification Service")
            
            # Start consuming messages
            consumer_task = asyncio.create_task(queue_consumer.start_consuming())
            self.tasks.add(consumer_task)
            consumer_task.add_done_callback(self.tasks.discard)

            # Keep the service running
            await asyncio.gather(*self.tasks)

        except Exception as e:
            logger.error(f"Error starting service: {str(e)}")
            await self.shutdown()

    async def shutdown(self, signal=None):
        """Shutdown the notification service"""
        if signal:
            logger.info(f"Received exit signal {signal.name}")
        
        logger.info("Shutting down Notification Service")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Close RabbitMQ connection
        await queue_consumer.close()
        
        # Stop the event loop
        loop = asyncio.get_event_loop()
        loop.stop()

def main():
    """Main entry point"""
    service = NotificationService()
    asyncio.run(service.start())

if __name__ == "__main__":
    main()