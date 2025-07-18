"""
Integration tests for User Management Controller Endpoints
Test cases: AUTH-024 and onwards
"""
import pytest
import httpx
import time

from ..config import settings
from ..test_metadata import add_test_info

# Helper to create unique user data for each test run
def unique_user_data(suffix: str):
    timestamp = int(time.time())
    return {
        "email": f"testuser_{timestamp}_{suffix}@example.com",
        "full_name": f"Test User {suffix}",
        "username": f"testuser_{timestamp}_{suffix}",
        "password": "SecurePassword123!",
        "role_ids": [2] # Assuming 'basic_user' role has ID 2
    }

# USER MANAGEMENT TESTS

@add_test_info(
    description="Crear un usuario exitosamente con permisos de administrador",
    expected_result="Status Code: 201, datos del usuario creado",
    module="Autenticación",
    test_id="AUTH-024"
)
async def test_create_user_success(auth_token: str):
    """Test successful user creation by an admin"""
    user_data = unique_user_data("create_success")
    headers = {"Authorization": f"Bearer {auth_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # Cleanup
    user_id = data["id"]
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)


@add_test_info(
    description="Fallar al crear un usuario sin permisos suficientes",
    expected_result="Status Code: 403, error de permisos",
    module="Autenticación",
    test_id="AUTH-025"
)
async def test_create_user_insufficient_permissions(basic_user_token: str):
    """Test user creation failure with basic user token"""
    user_data = unique_user_data("create_fail")
    headers = {"Authorization": f"Bearer {basic_user_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=headers)
        
    assert response.status_code == 403 # Forbidden


@add_test_info(
    description="Listar usuarios exitosamente",
    expected_result="Status Code: 200, lista de usuarios",
    module="Autenticación",
    test_id="AUTH-026"
)
async def test_list_users_success(auth_token: str):
    """Test successful listing of users"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/users/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@add_test_info(
    description="Obtener detalles de un usuario específico por ID",
    expected_result="Status Code: 200, datos del usuario",
    module="Autenticación",
    test_id="AUTH-027"
)
async def test_get_user_by_id_success(auth_token: str):
    """Test successful retrieval of a specific user by ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # First, create a user to fetch
    user_data = unique_user_data("get_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=headers)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Fetch the user
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]

    # Cleanup
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)


@add_test_info(
    description="Fallar al obtener usuario con ID no existente",
    expected_result="Status Code: 404, usuario no encontrado",
    module="Autenticación",
    test_id="AUTH-028"
)
async def test_get_user_by_id_not_found(auth_token: str):
    """Test retrieval of a non-existent user should return 404"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    non_existent_id = 999999
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/users/{non_existent_id}", headers=headers)
        
    assert response.status_code == 404


@add_test_info(
    description="Actualizar datos de un usuario exitosamente",
    expected_result="Status Code: 200, datos del usuario actualizados",
    module="Autenticación",
    test_id="AUTH-029"
)
async def test_update_user_success(auth_token: str):
    """Test successful update of user data"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a user to update
    user_data = unique_user_data("update_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=headers)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Update the user's full name
    update_data = {"full_name": "Updated Full Name"}
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Full Name"
    assert data["id"] == user_id

    # Cleanup
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)


@add_test_info(
    description="Eliminar lógicamente un usuario exitosamente",
    expected_result="Status Code: 200, datos del usuario con estado cambiado",
    module="Autenticación",
    test_id="AUTH-030"
)
async def test_delete_user_success(auth_token: str):
    """Test successful logical deletion of a user"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a user to delete
    user_data = unique_user_data("delete_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=headers)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Delete the user
    async with httpx.AsyncClient() as client:
        delete_response = await client.delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)

    assert delete_response.status_code == 200
    
    # Verify the user is marked as deleted (e.g., status changed or not found on list)
    get_response = await httpx.AsyncClient().get(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=headers)
    assert get_response.status_code == 200
    # Assuming status 2 corresponds to 'deleted' or 'inactive'
    assert get_response.json()["status_id"] != 1 


@add_test_info(
    description="Fallar al eliminar un usuario sin permisos",
    expected_result="Status Code: 403",
    module="Autenticación",
    test_id="AUTH-031"
)
async def test_delete_user_insufficient_permissions(auth_token: str, basic_user_token: str):
    """Test user deletion failure with insufficient permissions"""
    admin_headers = {"Authorization": f"Bearer {auth_token}"}
    basic_headers = {"Authorization": f"Bearer {basic_user_token}"}

    # Admin creates a user
    user_data = unique_user_data("delete_fail")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/users/", json=user_data, headers=admin_headers)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Basic user tries to delete it
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=basic_headers)

    assert response.status_code == 403

    # Cleanup by admin
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/users/{user_id}", headers=admin_headers) 