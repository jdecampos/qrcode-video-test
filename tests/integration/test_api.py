"""
Integration tests for QR Code API
"""

import pytest
import time
from fastapi.testclient import TestClient
from PIL import Image
import io

from main import app
from services.auth import auth_service
from models.auth import User


client = TestClient(app)


class TestQRCodeIntegration:
    """Integration tests for QR code API"""
    
    @pytest.fixture
    def auth_token(self):
        """Create valid JWT token for testing"""
        user = User(
            id="integration-user",
            username="integration",
            scopes=["qr:generate"]
        )
        return auth_service.create_access_token(user)
    
    def test_end_to_end_qr_generation(self, auth_token):
        """Test complete QR code generation flow"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test different data types
        test_cases = [
            {"data": "Simple text", "description": "Plain text"},
            {"data": "https://example.com", "description": "URL"},
            {"data": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;", "description": "WiFi config"},
        ]
        
        for case in test_cases:
            data = {
                "data": case["data"],
                "size": "medium",
                "format": "png",
                "error_correction": "M"
            }
            
            response = client.post("/v1/qr-code", json=data, headers=headers)
            
            assert response.status_code == 200, f"Failed for {case['description']}"
            assert response.headers["content-type"] == "image/png"
            
            # Verify it's a valid image
            img = Image.open(io.BytesIO(response.content))
            assert img.size == (300, 300)
    
    def test_performance_under_load(self, auth_token):
        """Test API performance under concurrent load"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {
            "data": "Performance test data",
            "size": "medium",
            "format": "png",
            "error_correction": "M"
        }
        
        # Generate 10 QR codes and measure performance
        start_time = time.time()
        responses = []
        
        for _ in range(10):
            response = client.post("/v1/qr-code", json=data, headers=headers)
            responses.append(response)
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Average time should be reasonable (< 1 second per request)
        avg_time = total_time / 10
        assert avg_time < 1.0, f"Average time {avg_time:.2f}s exceeds limit"
        
        # Check generation time headers
        for response in responses:
            gen_time = float(response.headers["x-generation-time-ms"])
            assert gen_time < 500, f"Generation time {gen_time}ms exceeds 500ms limit"
    
    def test_different_sizes_and_formats(self, auth_token):
        """Test different QR code sizes and formats"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        base_data = {"data": "Size and format test"}
        
        # Test all size combinations
        sizes = ["small", "medium", "large"]
        expected_sizes = {"small": 150, "medium": 300, "large": 600}
        
        for size in sizes:
            data = {**base_data, "size": size, "format": "png"}
            response = client.post("/v1/qr-code", json=data, headers=headers)
            
            assert response.status_code == 200
            assert response.headers["x-qr-size"] == size
            
            img = Image.open(io.BytesIO(response.content))
            expected = expected_sizes[size]
            assert img.size == (expected, expected)
    
    def test_error_correction_levels(self, auth_token):
        """Test all error correction levels"""
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        base_data = {"data": "Error correction test"}
        
        levels = ["L", "M", "Q", "H"]
        
        for level in levels:
            data = {**base_data, "error_correction": level}
            response = client.post("/v1/qr-code", json=data, headers=headers)
            
            assert response.status_code == 200
            assert response.headers["x-error-correction"] == level
    
    def test_authentication_integration(self):
        """Test authentication flow integration"""
        
        # Test without token
        response = client.post("/v1/qr-code", json={"data": "test"})
        assert response.status_code == 401
        
        # Test with expired token (simulate by creating token with short expiry)
        user = User(id="test-user", username="test")
        expired_token = auth_service.create_access_token(
            user, 
            expires_delta=time.timedelta(seconds=-1)  # Already expired
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.post("/v1/qr-code", json={"data": "test"}, headers=headers)
        assert response.status_code == 401
        
        # Test with valid token
        valid_token = auth_service.create_access_token(user)
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.post("/v1/qr-code", json={"data": "test"}, headers=headers)
        assert response.status_code == 200
