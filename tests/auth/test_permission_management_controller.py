"""
Integration tests for Permission Management Controller Endpoints
Test cases: AUTH-040 and onwards
"""
import pytest
import httpx

from ..config import settings
from ..test_metadata import add_test_info

# PERMISSION MANAGEMENT TESTS

@add_test_info(
    description="Listar todos los permisos del sistema exitosamente",
    expected_result="Status Code: 200, lista de permisos",
    module="Autenticación",
    test_id="AUTH-040"
)
async def test_list_permissions_success(auth_token: str):
    """Test successful listing of all system permissions"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/permissions/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@add_test_info(
    description="Fallar al listar permisos sin autenticación",
    expected_result="Status Code: 403, error de autenticación",
    module="Autenticación",
    test_id="AUTH-041"
)
async def test_list_permissions_no_auth(auth_token: str):
    """Test listing permissions fails without token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/permissions/")
    
    assert response.status_code == 403


@add_test_info(
    description="Obtener un permiso por su ID exitosamente",
    expected_result="Status Code: 200, datos del permiso",
    module="Autenticación",
    test_id="AUTH-042"
)
async def test_get_permission_by_id_success(auth_token: str):
    """Test successful retrieval of a permission by ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    permission_id = 1 # Assuming a permission with ID 1 exists
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/permissions/{permission_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == permission_id


@add_test_info(
    description="Obtener un permiso por su nombre exitosamente",
    expected_result="Status Code: 200, datos del permiso",
    module="Autenticación",
    test_id="AUTH-043"
)
async def test_get_permission_by_name_success(auth_token: str):
    """Test successful retrieval of a permission by its name"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Assuming a common permission like 'user:list' exists
    permission_name = "user:list"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/permissions/by-name/{permission_name}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == permission_name


@add_test_info(
    description="Fallar al obtener un permiso por nombre que no existe",
    expected_result="Status Code: 404",
    module="Autenticación",
    test_id="AUTH-044"
)
async def test_get_permission_by_name_not_found(auth_token: str):
    """Test getting a non-existent permission by name returns 404"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    permission_name = "non:existent:permission"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/permissions/by-name/{permission_name}", headers=headers)
    
    assert response.status_code == 404 