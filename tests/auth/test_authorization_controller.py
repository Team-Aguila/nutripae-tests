"""
Integration tests for Authorization Controller Endpoints
Test cases: AUTH-010 to AUTH-023
"""
import pytest
import httpx

from ..config import settings
from ..test_metadata import add_test_info


@add_test_info(
    description="Verificar autorización exitosa con token y permisos válidos",
    expected_result="Status Code: 200, autorizado es True",
    module="Autenticación",
    test_id="AUTH-010"
)
async def test_check_authorization_success(auth_token: str):
    """Test successful authorization check with valid token and permissions"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    auth_request = {
        "endpoint": "/users/",
        "method": "GET",
        "required_permissions": ["user:list"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/check-authorization", json=auth_request, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["authorized"] is True


@add_test_info(
    description="Verificar autorización con permisos insuficientes",
    expected_result="Status Code: 200, autorizado es False y muestra permisos faltantes",
    module="Autenticación",
    test_id="AUTH-011"
)
async def test_check_authorization_insufficient_permissions(basic_user_token: str):
    """Test authorization check with insufficient permissions - returns 200 with authorized=false"""
    headers = {"Authorization": f"Bearer {basic_user_token}"}
    auth_request = {
        "endpoint": "/users/",
        "method": "POST",
        "required_permissions": ["user:create"]  # Basic user doesn't have this permission
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/check-authorization", json=auth_request, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["authorized"] is False
    assert "user:create" in data["missing_permissions"]


@add_test_info(
    description="Verificar fallo de autorización sin token",
    expected_result="Status Code: 403",
    module="Autenticación",
    test_id="AUTH-012"
)
async def test_check_authorization_no_token():
    """Test authorization check without token should return 403"""
    auth_request = {
        "endpoint": "/users/",
        "method": "GET",
        "required_permissions": ["user:list"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/check-authorization", json=auth_request)
    
    assert response.status_code == 403


@add_test_info(
    description="Verificar fallo de autorización con token inválido",
    expected_result="Status Code: 401",
    module="Autenticación",
    test_id="AUTH-013"
)
async def test_check_authorization_invalid_token():
    """Test authorization check with invalid token should return 401"""
    headers = {"Authorization": "Bearer invalid_token_123"}
    auth_request = {
        "endpoint": "/users/",
        "method": "GET",
        "required_permissions": ["user:list"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/check-authorization", json=auth_request, headers=headers)
    
    assert response.status_code == 401


@add_test_info(
    description="Obtener permisos de usuario exitosamente",
    expected_result="Status Code: 200, lista de permisos del usuario",
    module="Autenticación",
    test_id="AUTH-014"
)
async def test_get_user_permissions_success(auth_token: str):
    """Test successful retrieval of user permissions with valid token"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/user-permissions", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
    assert len(data["permissions"]) > 0  # Admin should have permissions


@add_test_info(
    description="Fallar al obtener permisos de usuario sin token",
    expected_result="Status Code: 403",
    module="Autenticación",
    test_id="AUTH-015"
)
async def test_get_user_permissions_no_token():
    """Test user permissions retrieval without token should return 403"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/user-permissions")
    
    assert response.status_code == 403


@add_test_info(
    description="Fallar al obtener permisos de usuario con token inválido",
    expected_result="Status Code: 401",
    module="Autenticación",
    test_id="AUTH-016"
)
async def test_get_user_permissions_invalid_token():
    """Test user permissions retrieval with invalid token should return 401"""
    headers = {"Authorization": "Bearer invalid_token_123"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/authorization/user-permissions", headers=headers)
    
    assert response.status_code == 401


@add_test_info(
    description="Obtener información del usuario exitosamente",
    expected_result="Status Code: 200, datos del usuario",
    module="Autenticación",
    test_id="AUTH-017"
)
async def test_get_user_info_success(auth_token: str):
    """Test successful retrieval of user info with valid token"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == settings.ADMIN_USER_EMAIL


@add_test_info(
    description="Fallar al obtener información de usuario sin token",
    expected_result="Status Code: 403",
    module="Autenticación",
    test_id="AUTH-018"
)
async def test_get_user_info_no_token():
    """Test user info retrieval without token should return 403"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/auth/me")
    
    assert response.status_code == 403


@add_test_info(
    description="Fallar al obtener información de usuario con token inválido",
    expected_result="Status Code: 401",
    module="Autenticación",
    test_id="AUTH-019"
)
async def test_get_user_info_invalid_token():
    """Test user info retrieval with invalid token should return 401"""
    headers = {"Authorization": "Bearer invalid_token_123"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/auth/me", headers=headers)
    
    assert response.status_code == 401