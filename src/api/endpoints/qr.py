"""
QR Code Generation Endpoint
"""

import base64
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from src.models.requests import QRCodeRequest, ErrorResponse, QRCodeBase64Response
from src.services.qr_generator import QRCodeGenerator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/qr-code")
async def generate_qr_code(request: QRCodeRequest) -> Response:
    """
    Generate QR code from provided data
    
    - **data**: Text or URL to encode (required)
    - **size**: Size of QR code (small/medium/large, default: medium)
    - **format**: Output format (png/svg/jpeg/pdf, default: png)
    - **error_correction**: Error correction level (L/M/Q/H, default: M)
    - **output_format**: Output encoding (binary/base64, default: binary)
    """
    
    try:
        # Generate QR code
        generator = QRCodeGenerator()
        image_data, generation_time_ms = generator.generate_qr_code(request)
        
        # Handle base64 output
        if request.output_format == "base64":
            # Encode the image data as base64
            if isinstance(image_data, str):
                # SVG is already text, encode as UTF-8 then base64
                base64_data = base64.b64encode(image_data.encode('utf-8')).decode('utf-8')
            else:
                # Binary data (PNG, JPEG, PDF)
                base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Return JSON response with base64 data
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=QRCodeBase64Response(
                    data=base64_data,
                    format=request.format,
                    encoding="base64",
                    size=request.size,
                    error_correction=request.error_correction
                ).model_dump(),
                headers={
                    "X-Generation-Time-Ms": str(generation_time_ms),
                    "X-QR-Size": request.size,
                    "X-Error-Correction": request.error_correction,
                    "X-Output-Format": "base64",
                }
            )
        
        # Binary output (default)
        media_type = f"image/{request.format}"
        if request.format == "svg":
            media_type = "image/svg+xml"
        elif request.format == "pdf":
            media_type = "application/pdf"
        
        return Response(
            content=image_data,
            media_type=media_type,
            headers={
                "X-Generation-Time-Ms": str(generation_time_ms),
                "X-QR-Size": request.size,
                "X-Error-Correction": request.error_correction,
                "X-Output-Format": "binary",
            }
        )
    
    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": str(e)
            }
        )
    except RuntimeError as e:
        # Generation errors (capacity, format issues)
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "generation_error",
                "message": str(e)
            }
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred while processing your request"
            }
        )
