"""
Application configuration for QR Code API
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI Configuration
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # JWT Configuration
    secret_key: str = Field(default="your-super-secret-jwt-key-change-this-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # QR Code API Configuration
    max_data_length: int = Field(default=2000)
    default_size: str = Field(default="medium")
    default_format: str = Field(default="png")
    default_error_correction: str = Field(default="M")
    
    # Performance Configuration
    max_concurrent_requests: int = Field(default=100)
    generation_timeout_ms: int = Field(default=500)
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    
    # Authentication Configuration
    auth_username: str = Field(default="admin")
    auth_password: str = Field(default="secure_password_123")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow"  # Allow extra fields from environment
    }


# Global settings instance
settings = Settings()
