"""
Integration tests for Application Health and Status APIs
Test cases: MENUS-APP-001 to MENUS-APP-004
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response
from ..test_metadata import add_test_info


class TestApplicationRootEndpoint:
    """Test suite for GET / (root) endpoint"""
    
    @add_test_info(
        description="Verificar que el endpoint raíz responda correctamente en el servicio de menús",
        expected_result="Status Code: 200, mensaje de bienvenida",
        module="Menús",
        test_id="MENUS-APP-001"
    )
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
    
    @add_test_info(
        description="Verificar que el endpoint de salud general responda correctamente",
        expected_result="Status Code: 200, status healthy",
        module="Menús",
        test_id="MENUS-APP-002"
    )
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
    
    @add_test_info(
        description="Verificar que el endpoint de salud de la base de datos responda correctamente",
        expected_result="Status Code: 200, database connected",
        module="Menús",
        test_id="MENUS-APP-003"
    )
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
    
    @add_test_info(
        description="Manejar verificación de salud de base de datos cuando podría estar desconectada",
        expected_result="Status Code: 200, status healthy o unhealthy según estado",
        module="Menús",
        test_id="MENUS-APP-004"
    )
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