from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import logging
from datetime import datetime
import motor.motor_asyncio
import os

from ..services.file_handler import file_handler
from ..services.queue import queue_service
from .dependencies import verify_token
from ..core.exceptions import FileUploadError
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/convert")
async def convert_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user_data: dict = Depends(verify_token)
):
    """
    Convert video file to MP3
    - Validates file
    - Stores file temporarily
    - Queues conversion job
    """
    try:
        # Validate file
        file_handler.validate_file(file)
        
        # Save file and get job ID
        job_id, file_path = await file_handler.save_file(file)
        
        # Queue conversion task
        await queue_service.publish_conversion_task(
            job_id=job_id,
            file_path=file_path,
            user_email=user_data["email"]
        )
        
        # Remove this line - let the converter service handle cleanup
        # background_tasks.add_task(file_handler.cleanup_file, file_path)
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Video conversion started",
                "job_id": job_id,
                "status": "processing",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except FileUploadError as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing conversion request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing conversion request"
        )

@router.get("/status/{job_id}")
async def get_conversion_status(
    job_id: str,
    user_data: dict = Depends(verify_token)
):
    """Get conversion job status from MongoDB"""
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB]
        collection = db[settings.MONGODB_COLLECTION]

        # Get job status
        job = await collection.find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "job_id": job_id,
            "status": job.get("status", "processing"),
            "output_path": job.get("output_path"),
            "timestamp": job.get("updated_at", datetime.utcnow()).isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting job status")

@router.get("/download/{job_id}")
async def download_file(
    job_id: str,
    user_data: dict = Depends(verify_token)
):
    """Download converted MP3 file"""
    try:
        # Get job status to verify completion and get output path
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB]
        collection = db[settings.MONGODB_COLLECTION]

        job = await collection.find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Conversion not completed")

        output_path = job.get("output_path")
        if not output_path or not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            output_path,
            media_type='audio/mpeg',
            filename=f"{job_id}.mp3"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file")
    


@router.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "gateway"
    }