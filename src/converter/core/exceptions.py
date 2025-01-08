class ConverterError(Exception):
    """Base exception for converter service"""
    pass

class FFmpegError(ConverterError):
    """Raised when FFmpeg conversion fails"""
    pass

class FileNotFoundError(ConverterError):
    """Raised when input file is not found"""
    pass

class InvalidFileError(ConverterError):
    """Raised when file format is invalid"""
    pass

class QueueError(ConverterError):
    """Raised when there's an error with message queue"""
    pass

class StorageError(ConverterError):
    """Raised when there's an error with file storage"""
    pass

class DatabaseError(ConverterError):
    """Raised when there's an error with database operations"""
    pass