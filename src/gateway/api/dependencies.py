from fastapi import Header, HTTPException
import httpx
import logging
from typing import Dict

from ..core.config import settings
from ..core.exceptions import AuthServiceError

logger = logging.getLogger(__name__)

async def verify_token(authorization: str = Header(None)) -> Dict:
    """Verify JWT token with Auth service"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/verify",
                headers={"Authorization": authorization},
                timeout=settings.AUTH_TIMEOUT
            )
            
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        raise AuthServiceError("Auth service timeout")
    except httpx.HTTPStatusError as e:
        logger.error(f"Auth service error: {str(e)}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Unexpected error in auth verification: {str(e)}")
        raise AuthServiceError()