"""
Authentication endpoints for QR Code API
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.config import settings

router = APIRouter()
security = HTTPBearer()

# Load credentials from environment variable
def get_valid_credentials():
    """Load valid credentials from environment variable"""
    try:
        # Simple single user configuration
        username = getattr(settings, 'auth_username', 'admin')
        password = getattr(settings, 'auth_password', 'secure_password_123')
        
        return {username: password}
            
    except AttributeError as e:
        print(f"Warning: Could not load auth credentials: {e}")
        # Fallback to demo credentials
        return {
            "admin": "secure_password_123"
        }


VALID_CREDENTIALS = get_valid_credentials()


class TokenRequest(BaseModel):
    """Request model for token generation"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for token"""
    access_token: str
    token_type: str
    expires_in: int


@router.post("/auth/token", response_model=TokenResponse)
async def create_access_token(request: TokenRequest):
    """
    Generate JWT access token
    
    Authentication endpoint that validates credentials against environment-configured user.
    
    Environment variable setup:
    AUTH_USERNAME=admin
    AUTH_PASSWORD=secure_password_123
    
    In production, replace this with proper user database authentication.
    """
    
    # Validate credentials against configured user list
    if request.username not in VALID_CREDENTIALS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if VALID_CREDENTIALS[request.username] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    try:
        # Generate JWT token using python-jose
        from jose import jwt
        from datetime import datetime, timedelta
        
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "sub": request.username,
            "exp": expire,
            "iat": datetime.utcnow(),
            "scopes": ["qr:generate"]
        }
        
        # Generate token
        access_token = jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
        )
        
    except Exception as e:
        print(f"Token generation error: {e}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate access token"
        )


@router.post("/auth/validate")
async def validate_token(token: str = security):
    """
    Validate JWT token
    
    Endpoint to check if a token is still valid
    """
    try:
        from jose import jwt
        
        payload = jwt.decode(
            token.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "expires_at": payload.get("exp")
        }
    except Exception as e:
        return {
            "valid": False,
            "error": "Invalid or expired token"
        }
