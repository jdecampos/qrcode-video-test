"""
Contract tests for QR Code API
"""

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from main import app
from services.auth import auth_service
from models.auth import User


client = TestClient(app)


class TestQRCodeContract:
    """Contract tests for QR code generation endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Create valid JWT token for testing"""
        user = User(
            id="test-user",
            username="testuser",
            scopes=["qr:generate"]
        )
        return auth_service.create_access_token(user)
    
    def test_generate_qr_code_valid_request(self, auth_token):
        """Test QR code generation with valid request"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {
            "data": "Hello, World!",
            "size": "medium",
            "format": "png",
            "error_correction": "M"
        }
        
        response = client.post("/v1/qr-code", json=data, headers=headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "x-generation-time-ms" in response.headers
        assert "x-qr-size" in response.headers
        assert "x-error-correction" in response.headers
        
        # Verify it's a valid PNG image
        img = Image.open(io.BytesIO(response.content))
        assert img.size == (300, 300)  # medium size
        assert img.format == "PNG"
    
    def test_generate_qr_code_missing_auth(self):
        """Test that missing authentication returns 401"""
        
        data = {"data": "Hello, World!"}
        response = client.post("/v1/qr-code", json=data)
        
        assert response.status_code == 401
        assert response.json()["error"] == "authentication_error"
    
    def test_generate_qr_code_invalid_token(self):
        """Test that invalid token returns 401"""
        
        headers = {"Authorization": "Bearer invalid-token"}
        data = {"data": "Hello, World!"}
        
        response = client.post("/v1/qr-code", json=data, headers=headers)
        
        assert response.status_code == 401
        assert response.json()["error"] == "authentication_error"
    
    def test_generate_qr_code_empty_data(self, auth_token):
        """Test that empty data returns validation error"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {"data": ""}
        
        response = client.post("/v1/qr-code", json=data, headers=headers)
        
        assert response.status_code == 400
        assert "validation_error" in response.json()["error"]
    
    def test_generate_qr_code_invalid_url(self, auth_token):
        """Test that invalid URL returns validation error"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {"data": "https://invalid-url-without-tld"}
        
        response = client.post("/v1/qr-code", json=data, headers=headers)
        
        assert response.status_code == 400
        assert "validation_error" in response.json()["error"]
    
    def test_generate_qr_code_data_too_long(self, auth_token):
        """Test that data exceeding capacity returns error"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Create data that exceeds QR code capacity for high error correction
        long_data = "x" * 2000  # This should exceed capacity for level H
        
        data = {
            "data": long_data,
            "error_correction": "H"
        }
        
        response = client.post("/v1/qr-code", json=data, headers=headers)
        
        assert response.status_code == 400
        assert "validation_error" in response.json()["error"]
    
    def test_health_check_no_auth(self):
        """Test that health check works without authentication"""
        
        response = client.get("/v1/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()
        assert "timestamp" in response.json()
