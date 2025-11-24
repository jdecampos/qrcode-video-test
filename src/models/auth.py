"""
Authentication models for QR Code API
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    """Token data model"""
    user_id: Optional[str] = None
    exp: Optional[datetime] = None
    scopes: list[str] = []


class TokenPayload(BaseModel):
    """JWT Token payload"""
    sub: str  # Subject (user identifier)
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    scopes: list[str] = ["qr:generate"]  # Default permissions


class User(BaseModel):
    """User model for authentication"""
    id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True
    scopes: list[str] = ["qr:generate"]
