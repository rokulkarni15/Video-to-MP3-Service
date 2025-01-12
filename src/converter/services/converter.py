import os
import logging
from datetime import datetime
import motor.motor_asyncio
from typing import Dict, Optional

from ..core.config import settings
from ..core.exceptions import StorageError, DatabaseError
from ..utils.ffmpeg import ffmpeg

logger = logging.getLogger(__name__)

class ConverterService:
    def __init__(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Initialize MongoDB connection
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        self.collection = self.db[settings.MONGODB_COLLECTION]

    async def process_video(self, job_id: str, file_path: str, user_id: str) -> Dict:
        """Process video conversion job"""
        try:
            # Log the incoming request
            logger.info(f"Starting conversion for job_id: {job_id}, file: {file_path}")

            # First verify the file exists
            if not os.path.exists(file_path):
                error_msg = f"Input file not found: {file_path}"
                logger.error(error_msg)
                await self.update_job_status(job_id, "failed", error_msg)
                return {"success": False, "error": error_msg}

            # Update job status in database
            await self.update_job_status(job_id, "processing")
            
            # Validate input file
            logger.info(f"Validating file for job {job_id}")
            is_valid, error = await ffmpeg.validate_file(file_path)
            if not is_valid:
                logger.error(f"File validation failed for job {job_id}: {error}")
                await self.update_job_status(job_id, "failed", error)
                return {"success": False, "error": error}

            # Generate output path
            output_path = os.path.join(
                settings.OUTPUT_DIR,
                f"{job_id}.mp3"
            )
            logger.info(f"Output path for job {job_id}: {output_path}")

            # Convert file
            logger.info(f"Starting conversion for job {job_id}")
            success, conv_output_path, error = await ffmpeg.convert_to_mp3(file_path, job_id)
            
            if not success:
                logger.error(f"Conversion failed for job {job_id}: {error}")
                await self.update_job_status(job_id, "failed", error)
                return {"success": False, "error": error}

            logger.info(f"Conversion successful for job {job_id}")

            # Update job status
            await self.update_job_status(
                job_id, 
                "completed",
                output_path=conv_output_path
            )

            return {
                "success": True,
                "job_id": job_id,
                "output_path": conv_output_path
            }

        except Exception as e:
            logger.error(f"Error processing video for job {job_id}: {str(e)}")
            await self.update_job_status(job_id, "failed", str(e))
            return {"success": False, "error": str(e)}

        finally:
            # Cleanup input file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up input file for job {job_id}: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up file for job {job_id}: {str(e)}")

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        error: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> None:
        """Update job status in database"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if error:
                update_data["error"] = error
            
            if output_path:
                update_data["output_path"] = output_path

            await self.collection.update_one(
                {"job_id": job_id},
                {"$set": update_data},
                upsert=True
            )
            
            logger.info(f"Updated job {job_id} status to {status}")

        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            raise DatabaseError(f"Failed to update job status: {str(e)}")

    async def get_job_status(self, job_id: str) -> Dict:
        """Get job status from database"""
        try:
            job = await self.collection.find_one({"job_id": job_id})
            if not job:
                return {"status": "not_found"}
            return job
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            raise DatabaseError(f"Failed to get job status: {str(e)}")

converter_service = ConverterService()