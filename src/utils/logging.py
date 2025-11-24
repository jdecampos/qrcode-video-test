"""
Logging configuration for QR Code API
"""

import logging
import time
from typing import Dict, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def setup_logging():
    """Configure application logging"""
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("qr_api.log"),
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger = logging.getLogger(__name__)
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )
        
        # Add timing header
        response.headers["X-Process-Time-Ms"] = str(process_time)
        
        return response


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_qr_generation(self, data_length: int, size: str, format: str, 
                         error_correction: str, generation_time_ms: float):
        """Log QR code generation performance"""
        
        self.logger.info(
            f"QR Generated - Data: {data_length} chars, "
            f"Size: {size}, Format: {format}, "
            f"ErrorCorrection: {error_correction}, "
            f"Time: {generation_time_ms:.2f}ms"
        )
    
    def log_validation_error(self, error_type: str, details: Dict[str, Any]):
        """Log validation errors"""
        
        self.logger.warning(
            f"Validation Error - Type: {error_type}, Details: {details}"
        )
