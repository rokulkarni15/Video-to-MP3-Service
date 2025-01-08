from fastapi import HTTPException
from starlette import status

class FileUploadError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class FileSizeExceededError(FileUploadError):
    def __init__(self):
        super().__init__("File size exceeds maximum allowed size")

class InvalidFileTypeError(FileUploadError):
    def __init__(self, allowed_types: set):
        super().__init__(f"Invalid file type. Allowed types: {allowed_types}")

class FileStorageError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error storing file"
        )

class QueueError(HTTPException):
    def __init__(self, detail: str = "Error communicating with message queue"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class AuthServiceError(HTTPException):
    def __init__(self, detail: str = "Error communicating with auth service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )