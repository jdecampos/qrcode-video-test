"""
Unit tests for QR Code Generator Service
"""

import pytest
import time
from PIL import Image
import io

from models.requests import QRCodeRequest, QRSize, OutputFormat, ErrorCorrectionLevel
from services.qr_generator import QRCodeGenerator


class TestQRCodeGenerator:
    """Unit tests for QR code generation service"""
    
    def test_generate_basic_qr_code(self):
        """Test basic QR code generation"""
        
        generator = QRCodeGenerator()
        request = QRCodeRequest(data="Hello, World!")
        
        image_data, generation_time = generator.generate_qr_code(request)
        
        assert isinstance(image_data, bytes)
        assert len(image_data) > 0
        assert isinstance(generation_time, float)
        assert generation_time >= 0
        
        # Verify it's a valid PNG image
        img = Image.open(io.BytesIO(image_data))
        assert img.size == (300, 300)  # Default medium size
        assert img.format == "PNG"
    
    def test_generate_qr_code_different_sizes(self):
        """Test QR code generation with different sizes"""
        
        generator = QRCodeGenerator()
        
        sizes = [
            (QRSize.SMALL, 150),
            (QRSize.MEDIUM, 300),
            (QRSize.LARGE, 600),
        ]
        
        for qr_size, expected_pixels in sizes:
            request = QRCodeRequest(
                data="Test data",
                size=qr_size
            )
            
            image_data, _ = generator.generate_qr_code(request)
            img = Image.open(io.BytesIO(image_data))
            
            assert img.size == (expected_pixels, expected_pixels)
    
    def test_generate_qr_code_different_formats(self):
        """Test QR code generation with different output formats"""
        
        generator = QRCodeGenerator()
        
        formats = [
            OutputFormat.PNG,
            OutputFormat.SVG,
            OutputFormat.JPEG,
            OutputFormat.PDF,
        ]
        
        for format_type in formats:
            request = QRCodeRequest(
                data="Test data",
                format=format_type
            )
            
            image_data, _ = generator.generate_qr_code(request)
            
            assert isinstance(image_data, bytes)
            assert len(image_data) > 0
            
            if format_type == OutputFormat.PNG:
                img = Image.open(io.BytesIO(image_data))
                assert img.format == "PNG"
            elif format_type == OutputFormat.SVG:
                # SVG should be XML text
                svg_text = image_data.decode('utf-8')
                assert svg_text.startswith('<?xml')
                assert '<svg' in svg_text
            elif format_type == OutputFormat.JPEG:
                img = Image.open(io.BytesIO(image_data))
                assert img.format == "JPEG"
            elif format_type == OutputFormat.PDF:
                # PDF should start with PDF header
                assert image_data.startswith(b'%PDF')
    
    def test_generate_qr_code_error_correction_levels(self):
        """Test QR code generation with different error correction levels"""
        
        generator = QRCodeGenerator()
        
        levels = [
            ErrorCorrectionLevel.L,
            ErrorCorrectionLevel.M,
            ErrorCorrectionLevel.Q,
            ErrorCorrectionLevel.H,
        ]
        
        for level in levels:
            request = QRCodeRequest(
                data="Test data",
                error_correction=level
            )
            
            image_data, generation_time = generator.generate_qr_code(request)
            
            assert isinstance(image_data, bytes)
            assert len(image_data) > 0
            
            # Higher error correction should generally produce larger images
            img = Image.open(io.BytesIO(image_data))
            assert img.size == (300, 300)  # Size should be consistent
    
    def test_generate_qr_code_url_data(self):
        """Test QR code generation with URL data"""
        
        generator = QRCodeGenerator()
        
        urls = [
            "https://example.com",
            "https://www.google.com/search?q=test",
            "ftp://files.example.com/data.txt",
        ]
        
        for url in urls:
            request = QRCodeRequest(data=url)
            image_data, _ = generator.generate_qr_code(request)
            
            assert isinstance(image_data, bytes)
            assert len(image_data) > 0
            
            # Verify it's a valid image
            img = Image.open(io.BytesIO(image_data))
            assert img.size == (300, 300)
    
    def test_generate_qr_code_unicode_data(self):
        """Test QR code generation with Unicode characters"""
        
        generator = QRCodeGenerator()
        
        unicode_data = [
            "Hello 世界",
            "Café résumé naïve",
            "🚀 🌟 💫",
            "Тест на русском",
        ]
        
        for data in unicode_data:
            request = QRCodeRequest(data=data)
            image_data, generation_time = generator.generate_qr_code(request)
            
            assert isinstance(image_data, bytes)
            assert len(image_data) > 0
            assert generation_time >= 0
    
    def test_generate_qr_code_performance(self):
        """Test QR code generation performance"""
        
        generator = QRCodeGenerator()
        request = QRCodeRequest(data="Performance test data")
        
        # Generate multiple QR codes and measure time
        start_time = time.time()
        
        for _ in range(10):
            image_data, generation_time = generator.generate_qr_code(request)
            assert isinstance(image_data, bytes)
            assert generation_time < 500  # Should be under 500ms per generation
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        # Average should be reasonable
        assert avg_time < 0.1  # Should be under 100ms average
    
    def test_generate_qr_code_empty_data_raises_error(self):
        """Test that empty data raises ValueError"""
        
        generator = QRCodeGenerator()
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            request = QRCodeRequest(data="")
            generator.generate_qr_code(request)
    
    def test_generate_qr_code_invalid_data_raises_error(self):
        """Test that invalid data raises appropriate errors"""
        
        generator = QRCodeGenerator()
        
        # Test data that's too long for high error correction
        long_data = "x" * 2000
        
        with pytest.raises(ValueError, match="Data too large"):
            request = QRCodeRequest(
                data=long_data,
                error_correction=ErrorCorrectionLevel.H
            )
            generator.generate_qr_code(request)
