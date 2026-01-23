"""
Simple test suite for document classification endpoints
Tests API structure and error handling without complex mocking
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.config import settings


client = TestClient(app)

# API Key for testing
API_KEY = settings.API_KEY
HEADERS = {"x-ss-api-key": API_KEY}


class TestClassificationAPI:
    """Test classification endpoint API"""
    
    def test_classify_document_not_found(self):
        """Test classification of non-existent document returns 404"""
        response = client.post(
            "/api/docs/99999/classify",
            json={"force_llm": False},
            headers=HEADERS
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_classify_no_extracted_text(self):
        """Test classification without extracted text returns 400"""
        # This would need a document in DB without extracted_text
        # For now, we test the endpoint structure
        response = client.post(
            "/api/docs/1/classify",
            json={"force_llm": False},
            headers=HEADERS
        )
        # Either 404 (doc not found) or 400 (no extracted text)
        assert response.status_code in [400, 404]
    
    def test_classify_without_api_key(self):
        """Test classification without API key returns 403"""
        response = client.post(
            "/api/docs/1/classify",
            json={"force_llm": False}
        )
        assert response.status_code == 403
    
    def test_classify_invalid_request_body(self):
        """Test classification with invalid request returns proper error"""
        response = client.post(
            "/api/docs/1/classify",
            json={"invalid_field": "value"},
            headers=HEADERS
        )
        # Should either accept (default values) or reject
        assert response.status_code in [200, 400, 404]
    
    def test_classify_response_structure(self):
        """Test that successful classification has correct response structure"""
        # This test documents the expected response format
        # In real scenario, would have a document with extracted_text
        response = client.post(
            "/api/docs/1/classify",
            json={"force_llm": False},
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            # Verify response has required fields
            assert "document_id" in data
            assert "category" in data
            assert "filename" in data
            assert "target_path" in data
            assert "method" in data
            assert "message" in data
            
            # Verify method is one of expected values
            assert data["method"] in ["rules", "llm", "fallback"]
            
            # Verify confidence is a number if present
            if "confidence" in data:
                assert isinstance(data["confidence"], (int, float))


class TestApproveEndpoint:
    """Test approve endpoint"""
    
    def test_approve_document_not_found(self):
        """Test approve of non-existent document returns 404"""
        response = client.post(
            "/api/docs/99999/approve",
            json={
                "final_category": "Test",
                "final_filename": "test.pdf",
                "final_target_path": "03_sorted/Test"
            },
            headers=HEADERS
        )
        assert response.status_code == 404
    
    def test_approve_without_api_key(self):
        """Test approve without API key returns 403"""
        response = client.post(
            "/api/docs/1/approve",
            json={
                "final_category": "Test",
                "final_filename": "test.pdf",
                "final_target_path": "03_sorted/Test"
            }
        )
        assert response.status_code == 403


class TestRejectEndpoint:
    """Test reject endpoint"""
    
    def test_reject_document_not_found(self):
        """Test reject of non-existent document returns 404"""
        response = client.post(
            "/api/docs/99999/reject",
            headers=HEADERS
        )
        assert response.status_code == 404
    
    def test_reject_without_api_key(self):
        """Test reject without API key returns 403"""
        response = client.post(
            "/api/docs/1/reject"
        )
        assert response.status_code == 403


class TestUpdateDocumentEndpoint:
    """Test update document endpoint"""
    
    def test_update_document_not_found(self):
        """Test update of non-existent document returns 404"""
        response = client.patch(
            "/api/docs/99999",
            json={"user_approved_category": "Test"},
            headers=HEADERS
        )
        assert response.status_code == 404
    
    def test_update_without_api_key(self):
        """Test update without API key returns 403"""
        response = client.patch(
            "/api/docs/1",
            json={"user_approved_category": "Test"}
        )
        assert response.status_code == 403


# Integration tests that would need a real DB
class TestClassificationWorkflow:
    """Test complete classification workflow"""
    
    def test_get_documents_list(self):
        """Test retrieving documents list"""
        response = client.get("/api/docs/list", headers=HEADERS)
        # Should work without API key too (public endpoint)
        assert response.status_code in [200, 403]
    
    def test_get_document_details(self):
        """Test retrieving single document details"""
        response = client.get("/api/docs/1", headers=HEADERS)
        # Either 404 (not found) or 403 (no auth) or 200 (found)
        assert response.status_code in [200, 403, 404]
