"""
Authentication service for QR Code API
"""

import time
from datetime import datetime, timedelta
from typing import Optional

import jwt
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings
from src.models.auth import TokenPayload, User


class AuthService:
    """Service for JWT token management and validation"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        
        # Password context (for future user management)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = TokenPayload(
            sub=user.id,
            exp=int(expire.timestamp()),
            iat=int(time.time()),
            scopes=user.scopes
        )
        
        encoded_jwt = jwt.encode(
            payload.dict(), 
            self.secret_key, 
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode JWT token"""
        
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            return TokenPayload(**payload)
        
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def has_permission(self, token_payload: TokenPayload, required_scope: str) -> bool:
        """Check if token has required permission scope"""
        
        return required_scope in token_payload.scopes
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        
        return self.pwd_context.verify(plain_password, hashed_password)


# Global auth service instance
auth_service = AuthService()
