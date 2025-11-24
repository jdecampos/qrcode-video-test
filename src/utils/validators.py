"""
Input validation utilities for QR Code API
"""

import re
from typing import Tuple

from src.models.requests import ErrorCorrectionLevel


class ValidationResult:
    """Validation result with success status and message"""
    
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message
    
    def __bool__(self):
        return self.is_valid


def validate_qr_data(data: str) -> ValidationResult:
    """
    Validates the data to be encoded in QR code
    
    Rules:
    - Must not be empty
    - Maximum length: 2000 characters
    - If appears to be URL: must be valid URL format
    - Must be UTF-8 encodable
    """
    
    if not data or not data.strip():
        return ValidationResult(False, "Data cannot be empty")
    
    if len(data) > 2000:
        return ValidationResult(False, "Data exceeds maximum length of 2000 characters")
    
    # URL validation if data looks like URL
    if data.startswith(('http://', 'https://', 'ftp://')):
        if not is_valid_url(data):
            return ValidationResult(False, "Invalid URL format")
    
    # Test UTF-8 encoding
    try:
        data.encode('utf-8')
    except UnicodeEncodeError:
        return ValidationResult(False, "Data contains invalid characters")
    
    return ValidationResult(True, "Valid")


def validate_capacity(data: str, error_correction: ErrorCorrectionLevel) -> ValidationResult:
    """
    Validates if data fits within QR code capacity
    
    Capacity limits (approximate, for version 40 QR codes):
    - L: 2953 numeric, 2331 alphanumeric, 1663 binary
    - M: 2331 numeric, 1852 alphanumeric, 1273 binary
    - Q: 1663 numeric, 1361 alphanumeric, 927 binary
    - H: 1273 numeric, 1085 alphanumeric, 713 binary
    """
    
    # Simplified capacity check - use binary limits as worst case
    capacity_limits = {
        ErrorCorrectionLevel.L: 1663,
        ErrorCorrectionLevel.M: 1273,
        ErrorCorrectionLevel.Q: 927,
        ErrorCorrectionLevel.H: 713
    }
    
    # Estimate binary size (UTF-8)
    try:
        binary_size = len(data.encode('utf-8'))
    except UnicodeEncodeError:
        return ValidationResult(False, "Data contains invalid characters")
    
    max_capacity = capacity_limits[error_correction]
    
    if binary_size > max_capacity:
        return ValidationResult(
            False, 
            f"Data too large for error correction level {error_correction.value}. "
            f"Maximum: {max_capacity} bytes, got: {binary_size}"
        )
    
    return ValidationResult(True, "Valid")


def is_valid_url(url: str) -> bool:
    """
    Validate URL format using regex
    """
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', 
        re.IGNORECASE
    )
    
    return url_pattern.match(url) is not None


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages for API responses
    """
    
    # Remove potentially sensitive information
    sanitized = re.sub(r'[<>]', '', message)
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:197] + "..."
    
    return sanitized


def validate_generation_parameters(
    size: str, 
    format: str, 
    error_correction: str
) -> ValidationResult:
    """
    Validate QR code generation parameters
    """
    
    valid_sizes = ["small", "medium", "large"]
    if size not in valid_sizes:
        return ValidationResult(
            False, 
            f"Invalid size '{size}'. Valid sizes: {', '.join(valid_sizes)}"
        )
    
    valid_formats = ["png", "svg", "jpeg", "pdf"]
    if format not in valid_formats:
        return ValidationResult(
            False, 
            f"Invalid format '{format}'. Valid formats: {', '.join(valid_formats)}"
        )
    
    valid_error_levels = ["L", "M", "Q", "H"]
    if error_correction not in valid_error_levels:
        return ValidationResult(
            False, 
            f"Invalid error correction '{error_correction}'. Valid levels: {', '.join(valid_error_levels)}"
        )
    
    return ValidationResult(True, "Valid")
