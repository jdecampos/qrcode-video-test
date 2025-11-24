"""
JWT Authentication Middleware for QR Code API
"""

import time
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from src.config import settings


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware that validates JWT Bearer tokens
    """
    
    # Skip authentication for health check, docs, and auth endpoints
    if request.url.path in ["/v1/health", "/docs", "/redoc", "/openapi.json"] or \
       request.url.path.startswith("/v1/auth/"):
        response = await call_next(request)
        return response
    
    try:
        # Extract Authorization header
        authorization: Optional[str] = request.headers.get("Authorization")
        
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate Bearer token format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token format. Expected: 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.split(" ")[1]
        
        # Validate JWT token
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.token_exp = payload.get("exp")
            
            # Check token expiration
            if request.state.token_exp and request.state.token_exp < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        response = await call_next(request)
        return response
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return generic error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Authentication middleware error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )
