import os
import aiofiles
from fastapi import UploadFile
from datetime import datetime
import uuid
from pathlib import Path
import logging
from typing import Tuple

from ..core.config import settings
from ..core.exceptions import (
    FileSizeExceededError, 
    InvalidFileTypeError,
    FileStorageError
)

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
    def validate_file(self, file: UploadFile) -> None:
        """Validate file type and size"""
        # Check file extension
        extension = Path(file.filename).suffix.lower()
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(settings.ALLOWED_EXTENSIONS)

    async def save_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Save uploaded file and return job_id and file path
        Returns: Tuple[job_id, file_path]
        """
        try:
            # Generate unique job ID and filename
            job_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{job_id}_{file.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

            # Save file in chunks
            async with aiofiles.open(file_path, 'wb') as out_file:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    await out_file.write(chunk)

            logger.info(f"File saved: {file_path}")
            return job_id, file_path

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise FileStorageError()

    async def cleanup_file(self, file_path: str) -> None:
        """Remove temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)

    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        return {
            "size": self.get_file_size(file_path),
            "created": datetime.fromtimestamp(
                os.path.getctime(file_path)
            ).isoformat(),
            "path": file_path,
        }

file_handler = FileHandler()