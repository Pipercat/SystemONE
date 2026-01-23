"""
SmartSortierer Pro - Security & Authentication
"""
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


# API Key Header scheme
api_key_header = APIKeyHeader(name="x-ss-api-key", auto_error=False)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce API key authentication on all endpoints
    except health checks and public documentation.
    """
    
    # Endpoints that don't require API key
    PUBLIC_PATHS = {
        "/api/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
    }
    
    async def dispatch(self, request: Request, call_next):
        from fastapi.responses import JSONResponse
        
        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Check for API key in header
        api_key = request.headers.get("x-ss-api-key")
        
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing API key. Provide 'x-ss-api-key' header."},
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        if api_key != settings.API_KEY:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API key"},
            )
        
        # API key valid, proceed with request
        response = await call_next(request)
        return response


def verify_api_key(api_key: Optional[str]) -> bool:
    """
    Verify if provided API key is valid.
    
    Args:
        api_key: API key to verify
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    return api_key == settings.API_KEY


def get_actor_info(request: Request) -> dict:
    """
    Extract actor information from request for audit logging.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with actor_type, actor_id, ip_address, user_agent
    """
    return {
        "actor_type": "API",  # Can be enhanced to detect USER vs API vs SYSTEM
        "actor_id": request.headers.get("x-ss-api-key", "unknown")[:16],  # Truncated for privacy
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }
