import asyncio
import logging
import signal
from typing import Set
import sys
from pathlib import Path

from .services.converter import converter_service
from .services.queue import queue_consumer
from .core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class ConverterService:
    def __init__(self):
        self.tasks: Set[asyncio.Task] = set()
        self.should_exit = False

        # Ensure directories exist
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    async def start(self):
        """Start the converter service"""
        try:
            # Setup signal handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                asyncio.get_event_loop().add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self.shutdown(sig))
                )

            logger.info("Starting Converter Service")
            
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
        """Shutdown the converter service"""
        if signal:
            logger.info(f"Received exit signal {signal.name}")
        
        logger.info("Shutting down Converter Service")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close queue connection
        await queue_consumer.close()
        
        # Stop the event loop
        asyncio.get_running_loop().stop()

async def main():
    """Main entry point"""
    service = ConverterService()
    
    try:
        await service.start()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        # Ensure clean shutdown
        await service.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")