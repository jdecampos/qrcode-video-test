"""
Request and Response Models for QR Code API
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class QRSize(str, Enum):
    """QR Code size options"""
    SMALL = "small"      # 150x150 pixels
    MEDIUM = "medium"    # 300x300 pixels
    LARGE = "large"      # 600x600 pixels
    
    @property
    def pixels(self) -> int:
        """Get pixel dimensions"""
        size_map = {
            QRSize.SMALL: 150,
            QRSize.MEDIUM: 300,
            QRSize.LARGE: 600,
        }
        return size_map[self]


class ErrorCorrectionLevel(str, Enum):
    """QR Code error correction levels"""
    L = "L"    # ~7% correction capacity
    M = "M"    # ~15% correction capacity (default)
    Q = "Q"    # ~25% correction capacity
    H = "H"    # ~30% correction capacity


class OutputFormat(str, Enum):
    """QR Code output formats"""
    PNG = "png"
    SVG = "svg"
    JPEG = "jpeg"
    PDF = "pdf"


class OutputEncoding(str, Enum):
    """QR Code output encoding"""
    BINARY = "binary"
    BASE64 = "base64"


class QRCodeRequest(BaseModel):
    """Request model for QR code generation"""
    
    data: str = Field(..., description="Text or URL to encode", min_length=1, max_length=2000)
    size: QRSize = Field(QRSize.MEDIUM, description="Size of the QR code")
    format: OutputFormat = Field(OutputFormat.PNG, description="Output format")
    error_correction: ErrorCorrectionLevel = Field(
        ErrorCorrectionLevel.M, 
        description="Error correction level"
    )
    output_format: OutputEncoding = Field(
        OutputEncoding.BINARY, 
        description="Output encoding format (binary or base64)"
    )
    
    @validator('data')
    def validate_data(cls, v):
        """Validate input data"""
        if not v or not v.strip():
            raise ValueError("Data cannot be empty")
        
        # URL validation for URL-like data
        if v.startswith(('http://', 'https://', 'ftp://')):
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(v):
                raise ValueError("Invalid URL format")
        
        # Test UTF-8 encoding
        try:
            v.encode('utf-8')
        except UnicodeEncodeError:
            raise ValueError("Data contains invalid characters")
        
        return v
    
    @validator('data')
    def validate_capacity(cls, v, values):
        """Validate data fits within QR code capacity"""
        if 'error_correction' in values:
            error_correction = values['error_correction']
            
            # Capacity limits (approximate, binary data)
            capacity_limits = {
                ErrorCorrectionLevel.L: 1663,
                ErrorCorrectionLevel.M: 1273,
                ErrorCorrectionLevel.Q: 927,
                ErrorCorrectionLevel.H: 713
            }
            
            try:
                binary_size = len(v.encode('utf-8'))
                max_capacity = capacity_limits[error_correction]
                
                if binary_size > max_capacity:
                    raise ValueError(
                        f"Data too large for error correction level {error_correction.value}. "
                        f"Maximum: {max_capacity} bytes, got: {binary_size}"
                    )
            except UnicodeEncodeError:
                raise ValueError("Data contains invalid characters")
        
        return v


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(..., description="Error category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class QRCodeBase64Response(BaseModel):
    """Base64 encoded QR code response model"""
    
    data: str = Field(..., description="Base64 encoded QR code data")
    format: str = Field(..., description="Image format (png, svg, jpeg, pdf)")
    encoding: str = Field(..., description="Encoding format (always base64)")
    size: str = Field(..., description="QR code size used")
    error_correction: str = Field(..., description="Error correction level used")
