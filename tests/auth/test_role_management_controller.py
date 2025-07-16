"""
Integration tests for Role Management Controller Endpoints
Test cases: AUTH-032 and onwards
"""
import pytest
import httpx
import time

from ..config import settings
from ..test_metadata import add_test_info

# Helper to create unique role data
def unique_role_data(suffix: str):
    timestamp = int(time.time())
    return {
        "name": f"Test Role {timestamp}_{suffix}",
        "description": "A role created for integration testing",
        "permission_ids": [] # Start with no permissions
    }

# ROLE MANAGEMENT TESTS

@add_test_info(
    description="Crear un rol exitosamente",
    expected_result="Status Code: 201, datos del rol creado",
    module="Autenticación",
    test_id="AUTH-032"
)
async def test_create_role_success(auth_token: str):
    """Test successful role creation"""
    role_data = unique_role_data("create_success")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == role_data["name"]
    assert "id" in data

    # Cleanup
    role_id = data["id"]
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)


@add_test_info(
    description="Fallar al crear un rol con nombre duplicado",
    expected_result="Status Code: 400, error de nombre duplicado",
    module="Autenticación",
    test_id="AUTH-033"
)
async def test_create_role_duplicate_name(auth_token: str):
    """Test role creation failure with a duplicate name"""
    role_data = unique_role_data("duplicate")
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create the role first
    async with httpx.AsyncClient() as client:
        response1 = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    assert response1.status_code == 201
    role_id = response1.json()["id"]

    # Try to create it again
    async with httpx.AsyncClient() as client:
        response2 = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    
    assert response2.status_code == 400

    # Cleanup
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)


@add_test_info(
    description="Listar roles exitosamente",
    expected_result="Status Code: 200, lista de roles",
    module="Autenticación",
    test_id="AUTH-034"
)
async def test_list_roles_success(auth_token: str):
    """Test successful listing of roles"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@add_test_info(
    description="Obtener un rol por ID exitosamente",
    expected_result="Status Code: 200, datos del rol",
    module="Autenticación",
    test_id="AUTH-035"
)
async def test_get_role_by_id_success(auth_token: str):
    """Test successful retrieval of a role by ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a role to fetch
    role_data = unique_role_data("get_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    assert create_response.status_code == 201
    role_id = create_response.json()["id"]
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == role_data["name"]

    # Cleanup
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)


@add_test_info(
    description="Actualizar un rol exitosamente",
    expected_result="Status Code: 200, datos del rol actualizados",
    module="Autenticación",
    test_id="AUTH-036"
)
async def test_update_role_success(auth_token: str):
    """Test successful update of a role"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a role to update
    role_data = unique_role_data("update_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    assert create_response.status_code == 201
    role_id = create_response.json()["id"]

    # Update data
    update_data = {"description": "Updated Description"}
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", json=update_data, headers=headers)
        
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Description"

    # Cleanup
    await httpx.AsyncClient().delete(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)


@add_test_info(
    description="Eliminar un rol exitosamente",
    expected_result="Status Code: 200",
    module="Autenticación",
    test_id="AUTH-037"
)
async def test_delete_role_success(auth_token: str):
    """Test successful deletion of a role"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create a role to delete
    role_data = unique_role_data("delete_success")
    create_response = await httpx.AsyncClient().post(f"{settings.BASE_AUTH_BACKEND_URL}/roles/", json=role_data, headers=headers)
    assert create_response.status_code == 201
    role_id = create_response.json()["id"]

    # Delete it
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)
    assert response.status_code == 200

    # Verify it's gone
    async with httpx.AsyncClient() as client:
        verify_response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{role_id}", headers=headers)
    assert verify_response.status_code == 404


@add_test_info(
    description="Listar usuarios asignados a un rol",
    expected_result="Status Code: 200, lista de usuarios",
    module="Autenticación",
    test_id="AUTH-038"
)
async def test_get_role_users_success(auth_token: str):
    """Test successful retrieval of users assigned to a role"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    admin_role_id = 1 # Assuming admin role is ID 1
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{admin_role_id}/users", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Admin user should be in this list
    assert any(user['email'] == settings.ADMIN_USER_EMAIL for user in data)


@add_test_info(
    description="Fallar al listar usuarios de un rol que no existe",
    expected_result="Status Code: 404",
    module="Autenticación",
    test_id="AUTH-039"
)
async def test_get_role_users_not_found(auth_token: str):
    """Test getting users for a non-existent role"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    non_existent_role_id = 999999
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_AUTH_BACKEND_URL}/roles/{non_existent_role_id}/users", headers=headers)

    assert response.status_code == 404 