"""
Integration tests for Departments Endpoints
"""
import pytest
import httpx
import uuid
import random
from ..config import settings
from ..test_metadata import add_test_info

created_department_id = None

@add_test_info(
    description="Crear un departamento exitosamente",
    expected_result="Status Code: 200, datos del departamento creado",
    module="Cobertura",
    test_id="DEP-001"
)
@pytest.mark.asyncio
async def test_create_department_success(auth_token):
    """Test successful department creation"""
    global created_department_id
    random_number = random.randint(10000, 99999)
    department_data = {
        "name": f"Test Department {random_number}",
        "dane_code": f"DANE{random_number}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/",
            json=department_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == department_data["name"]
    created_department_id = data["id"]

@add_test_info(
    description="Fallar al crear un departamento con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="Cobertura",
    test_id="DEP-002"
)
@pytest.mark.asyncio
async def test_create_department_missing_data(auth_token):
    """Test department creation with missing required fields"""
    random_number = random.randint(10000, 99999)
    department_data = {
        "dane_code": f"DANE{random_number}"
        # "name": "Test Department" <- Missing
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/",
            json=department_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de departamentos exitosamente",
    expected_result="Status Code: 200, lista de departamentos",
    module="Cobertura",
    test_id="DEP-003"
)
@pytest.mark.asyncio
async def test_get_departments_success(auth_token):
    """Test successful retrieval of departments list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de departamentos sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="DEP-004"
)
@pytest.mark.asyncio
async def test_get_departments_unauthorized():
    """Test retrieving departments list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener un departamento por ID exitosamente",
    expected_result="Status Code: 200, datos del departamento",
    module="Cobertura",
    test_id="DEP-005"
)
@pytest.mark.asyncio
async def test_get_department_by_id_success(auth_token):
    """Test successful retrieval of a department by ID"""
    assert created_department_id is not None, "Department ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{created_department_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_department_id

@add_test_info(
    description="Fallar al obtener un departamento con un ID inexistente",
    expected_result="Status Code: 404, error no encontrado",
    module="Cobertura",
    test_id="DEP-006"
)
@pytest.mark.asyncio
async def test_get_department_by_id_not_found(auth_token):
    """Test retrieving a department with a non-existent ID"""
    random_number = random.randint(10000, 99999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{random_number}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) un departamento exitosamente",
    expected_result="Status Code: 200, datos actualizados del departamento",
    module="Cobertura",
    test_id="DEP-007"
)
@pytest.mark.asyncio
async def test_update_department_put_success(auth_token):
    """Test successful full update (PUT) of a department"""
    assert created_department_id is not None, "Department ID is not set"
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Department {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{created_department_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

@add_test_info(
    description="Fallar al actualizar (PUT) un departamento con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="DEP-008"
)
@pytest.mark.asyncio
async def test_update_department_put_not_found(auth_token):
    """Test full update (PUT) of a non-existent department"""
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Department {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{random_number}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Actualizar parcialmente (PATCH) un departamento exitosamente",
    expected_result="Status Code: 200, datos actualizados del departamento",
    module="Cobertura",
    test_id="DEP-009"
)
@pytest.mark.asyncio
async def test_update_department_patch_success(auth_token):
    """Test successful partial update (PATCH) of a department"""
    assert created_department_id is not None, "Department ID is not set"
    patch_data = {"name": "Patched Department Name"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{created_department_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == patch_data["name"]

@add_test_info(
    description="Fallar al actualizar (PATCH) un departamento con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="DEP-010"
)
@pytest.mark.asyncio
async def test_update_department_patch_not_found(auth_token):
    """Test partial update (PATCH) of a non-existent department"""
    patch_data = {"name": "Patched Department Name"}
    random_number = random.randint(10000, 99999)
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{random_number}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Eliminar un departamento exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="Cobertura",
    test_id="DEP-011"
)
@pytest.mark.asyncio
async def test_delete_department_success(auth_token):
    """Test successful deletion of a department"""
    assert created_department_id is not None, "Department ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{created_department_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar un departamento con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="DEP-012"
)
@pytest.mark.asyncio
async def test_delete_department_not_found(auth_token):
    """Test deleting a non-existent department"""
    random_number = random.randint(10000, 99999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{random_number}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400 