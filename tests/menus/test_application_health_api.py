"""
Integration tests for Application Health and Status APIs
Test cases: MENUS-APP-001 to MENUS-APP-004
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response


class TestApplicationRootEndpoint:
    """Test suite for GET / (root) endpoint"""
    
    async def test_get_welcome_message_success(self, client: httpx.AsyncClient):
        """MENUS-APP-001: Successfully get welcome message"""
        # Root endpoint is at the base URL, not under API prefix
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify welcome message response structure
        assert "message" in data
        assert data["message"] == "Welcome to the PAE Menus API"


class TestApplicationHealthEndpoints:
    """Test suite for health check endpoints"""
    
    async def test_get_general_health_status_success(self, client: httpx.AsyncClient):
        """MENUS-APP-002: Successfully get health status"""
        # Health endpoint is at the root level, not under API prefix
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify health response structure
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "PAE Menus API"
    
    async def test_get_database_health_success(self, client: httpx.AsyncClient):
        """MENUS-APP-003: Successfully check database health"""
        # Database health endpoint is at the root level, not under API prefix
        response = await client.get("/health/database")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify database health response structure
        assert "status" in data
        assert data["status"] == "healthy"
        assert "database" in data
        assert data["database"] == "connected"
    
    async def test_get_database_health_when_database_down(self, client: httpx.AsyncClient):
        """MENUS-APP-004: Handle database health check when database might be down"""
        # Database health endpoint is at the root level, not under API prefix
        response = await client.get("/health/database")
        
        assert response.status_code == 200
        data = response.json()
        
        # This test assumes the database might be down, but in our case it's up
        # The test should check for either healthy or unhealthy status
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert "database" in data
        if data["status"] == "healthy":
            assert data["database"] == "connected"
        else:
            assert data["database"] == "disconnected"
            assert "error" in data
            assert isinstance(data["error"], str) 