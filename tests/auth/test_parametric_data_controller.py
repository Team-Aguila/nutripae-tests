"""
Integration tests for Parametric Data Controller Endpoints
Test cases: AUTH-051 and onwards
"""
import pytest
import httpx

from ..config import settings
from ..test_metadata import add_test_info

# PARAMETRIC DATA TESTS

@add_test_info(
    description="Listar estados de usuario exitosamente",
    expected_result="Status Code: 200, lista de estados",
    module="Autenticación",
    test_id="AUTH-051"
)
async def test_list_user_statuses_success(auth_token: str):
    """Test successful listing of user statuses"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/parametric/user-statuses/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]

@add_test_info(
    description="Fallar al listar estados de usuario sin autenticación",
    expected_result="Status Code: 403",
    module="Autenticación",
    test_id="AUTH-052"
)
async def test_list_user_statuses_no_auth(auth_token: str):
    """Test listing user statuses fails without a token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/parametric/user-statuses/")
    
    assert response.status_code == 403

@add_test_info(
    description="Listar estados de invitación exitosamente",
    expected_result="Status Code: 200, lista de estados",
    module="Autenticación",
    test_id="AUTH-053"
)
async def test_list_invitation_statuses_success(auth_token: str):
    """Test successful listing of invitation statuses"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/parametric/invitation-statuses/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@add_test_info(
    description="Listar versiones de API exitosamente",
    expected_result="Status Code: 200, lista de versiones",
    module="Autenticación",
    test_id="AUTH-054"
)
async def test_list_api_versions_success(auth_token: str):
    """Test successful listing of API versions"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/parametric/api-versions/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@add_test_info(
    description="Listar métodos HTTP exitosamente",
    expected_result="Status Code: 200, lista de métodos",
    module="Autenticación",
    test_id="AUTH-055"
)
async def test_list_http_methods_success(auth_token: str):
    """Test successful listing of HTTP methods"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/parametric/http-methods/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0 