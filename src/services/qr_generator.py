"""
QR Code Generation Service
"""

import io
import time
from typing import Tuple

import qrcode
from PIL import Image
import svgwrite
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from src.models.requests import QRCodeRequest, QRSize, OutputFormat, ErrorCorrectionLevel
from src.utils.validators import validate_qr_data, validate_capacity
from src.utils.logging import PerformanceLogger


class QRCodeGenerator:
    """
    Stateless QR code generator service
    
    All operations are in-memory:
    1. Validate input
    2. Generate QR code in memory
    3. Convert to requested format
    4. Stream response
    5. Clean up resources
    """
    
    def __init__(self):
        self.performance_logger = PerformanceLogger()
        
        # Map error correction levels to qrcode constants
        self.error_correction_map = {
            ErrorCorrectionLevel.L: qrcode.constants.ERROR_CORRECT_L,
            ErrorCorrectionLevel.M: qrcode.constants.ERROR_CORRECT_M,
            ErrorCorrectionLevel.Q: qrcode.constants.ERROR_CORRECT_Q,
            ErrorCorrectionLevel.H: qrcode.constants.ERROR_CORRECT_H,
        }
    
    def generate_qr_code(self, request: QRCodeRequest) -> Tuple[bytes, float]:
        """
        Generate QR code and return as bytes with generation time
        
        Args:
            request: QR code generation request
            
        Returns:
            Tuple of (image_data_bytes, generation_time_ms)
            
        Raises:
            ValueError: If input validation fails
        """
        
        start_time = time.time()
        
        # Validate input
        data_validation = validate_qr_data(request.data)
        if not data_validation:
            raise ValueError(data_validation.message)
        
        capacity_validation = validate_capacity(request.data, request.error_correction)
        if not capacity_validation:
            raise ValueError(capacity_validation.message)
        
        try:
            # Generate QR code based on format
            if request.format == OutputFormat.SVG:
                image_data = self._generate_svg_qr(request)
            elif request.format == OutputFormat.PDF:
                image_data = self._generate_pdf_qr(request)
            else:
                image_data = self._generate_raster_qr(request)
            
            generation_time = (time.time() - start_time) * 1000
            
            # Log performance
            self.performance_logger.log_qr_generation(
                data_length=len(request.data),
                size=request.size,
                format=request.format,
                error_correction=request.error_correction,
                generation_time_ms=generation_time
            )
            
            return image_data, generation_time
            
        except Exception as e:
            raise ValueError(f"Failed to generate QR code: {str(e)}")
    
    def _generate_raster_qr(self, request: QRCodeRequest) -> bytes:
        """Generate PNG or JPEG QR code"""
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,  # Auto-detect version
            error_correction=self.error_correction_map[request.error_correction],
            box_size=10,  # Size of each box in pixels
            border=4,     # Border size in boxes
        )
        
        # Add data and optimize
        qr.add_data(request.data)
        qr.make(fit=True)
        
        # Create image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to requested dimensions
        target_size = request.size.pixels
        qr_img = qr_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        
        if request.format == OutputFormat.JPEG:
            # Convert to RGB for JPEG (no transparency)
            rgb_img = Image.new('RGB', qr_img.size, 'white')
            rgb_img.paste(qr_img, mask=qr_img.split()[-1] if qr_img.mode == 'RGBA' else None)
            rgb_img.save(img_buffer, format='JPEG', quality=85)
        else:
            # PNG
            qr_img.save(img_buffer, format='PNG')
        
        return img_buffer.getvalue()
    
    def _generate_svg_qr(self, request: QRCodeRequest) -> bytes:
        """Generate SVG QR code"""
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,
            error_correction=self.error_correction_map[request.error_correction],
            box_size=10,
            border=4,
        )
        
        qr.add_data(request.data)
        qr.make(fit=True)
        
        # Get QR code matrix
        qr_matrix = qr.get_matrix()
        box_size = 10
        border = 4
        
        # Calculate SVG dimensions
        matrix_size = len(qr_matrix)
        svg_size = (matrix_size + 2 * border) * box_size
        
        # Create SVG manually
        svg_lines = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{svg_size}" height="{svg_size}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="100%" height="100%" fill="white"/>',
        ]
        
        # Add QR code modules
        for row, matrix_row in enumerate(qr_matrix):
            for col, module in enumerate(matrix_row):
                if module:  # Black module
                    x = (col + border) * box_size
                    y = (row + border) * box_size
                    
                    svg_lines.append(
                        f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="black"/>'
                    )
        
        svg_lines.append('</svg>')
        
        return '\n'.join(svg_lines).encode('utf-8')
    
    def _generate_pdf_qr(self, request: QRCodeRequest) -> bytes:
        """Generate PDF QR code"""
        
        try:
            # First generate as PNG
            png_request = QRCodeRequest(
                data=request.data,
                size=request.size,
                format=OutputFormat.PNG,
                error_correction=request.error_correction
            )
            
            png_data = self._generate_raster_qr(png_request)
            
            # Create PDF
            pdf_buffer = io.BytesIO()
            pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
            
            # Calculate position to center QR code
            target_size = request.size.pixels
            page_width, page_height = letter
            
            x = (page_width - target_size) / 2
            y = (page_height - target_size) / 2
            
            # Create ImageReader for reportlab
            from reportlab.lib.utils import ImageReader
            
            img_reader = ImageReader(io.BytesIO(png_data))
            
            # Draw QR code on PDF
            pdf_canvas.drawImage(
                img_reader,
                x, y,
                width=target_size,
                height=target_size,
                preserveAspectRatio=True
            )
            
            pdf_canvas.save()
            return pdf_buffer.getvalue()
            
        except Exception as e:
            # If PDF generation fails, create a simple text-based PDF
            pdf_buffer = io.BytesIO()
            pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
            
            page_width, page_height = letter
            
            # Add title
            pdf_canvas.setFont("Helvetica-Bold", 16)
            pdf_canvas.drawString(
                page_width / 2 - 100,
                page_height / 2 + 50,
                "QR Code Generator API"
            )
            
            # Add QR code info
            pdf_canvas.setFont("Helvetica", 12)
            pdf_canvas.drawString(
                page_width / 2 - 150,
                page_height / 2,
                f"Data: {request.data[:60]}{'...' if len(request.data) > 60 else ''}"
            )
            pdf_canvas.drawString(
                page_width / 2 - 150,
                page_height / 2 - 30,
                f"Size: {request.size} ({target_size}x{target_size}px)"
            )
            pdf_canvas.drawString(
                page_width / 2 - 150,
                page_height / 2 - 50,
                f"Error Correction: {request.error_correction}"
            )
            
            # Add note about image generation
            pdf_canvas.setFont("Helvetica-Oblique", 10)
            pdf_canvas.drawString(
                page_width / 2 - 150,
                page_height / 2 - 80,
                "Note: QR code image generation failed - showing text representation"
            )
            
            pdf_canvas.save()
            return pdf_buffer.getvalue()
