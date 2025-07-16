"""
Integration tests for Towns Endpoints
"""
import pytest
import httpx
import random
from ..config import settings
from ..test_metadata import add_test_info

created_town_id = None
created_town_dane_code = None

@add_test_info(
    description="Crear un municipio exitosamente",
    expected_result="Status Code: 200, datos del municipio creado",
    module="Cobertura",
    test_id="TOW-001"
)
@pytest.mark.asyncio
async def test_create_town_success(auth_token, department):
    """Test successful town creation"""
    global created_town_id, created_town_dane_code
    random_number = random.randint(10000, 99999)
    town_data = {
        "name": f"Test Town {random_number}",
        "dane_code": f"DANE{random_number}",
        "department_id": department["id"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/",
            json=town_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == town_data["name"]
    created_town_id = data["id"]
    created_town_dane_code = data["dane_code"]

@add_test_info(
    description="Fallar al crear un municipio con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="Cobertura",
    test_id="TOW-002"
)
@pytest.mark.asyncio
async def test_create_town_missing_data(auth_token, department):
    """Test town creation with missing required fields"""
    town_data = {
        "name": "Incomplete Town",
        "department_id": department["id"]
        # Missing dane_code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/",
            json=town_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de municipios exitosamente",
    expected_result="Status Code: 200, lista de municipios",
    module="Cobertura",
    test_id="TOW-003"
)
@pytest.mark.asyncio
async def test_get_towns_success(auth_token):
    """Test successful retrieval of towns list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de municipios sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="TOW-004"
)
@pytest.mark.asyncio
async def test_get_towns_unauthorized():
    """Test retrieving towns list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener un municipio por ID exitosamente",
    expected_result="Status Code: 200, datos del municipio",
    module="Cobertura",
    test_id="TOW-005"
)
@pytest.mark.asyncio
async def test_get_town_by_id_success(auth_token):
    """Test successful retrieval of a town by ID"""
    assert created_town_id is not None, "Town ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{created_town_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_town_id

@add_test_info(
    description="Fallar al obtener un municipio con un ID inexistente",
    expected_result="Status Code: 404, error no encontrado",
    module="Cobertura",
    test_id="TOW-006"
)
@pytest.mark.asyncio
async def test_get_town_by_id_not_found(auth_token):
    """Test retrieving a town with a non-existent ID"""
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) un municipio exitosamente",
    expected_result="Status Code: 200, datos actualizados del municipio",
    module="Cobertura",
    test_id="TOW-007"
)
@pytest.mark.asyncio
async def test_update_town_put_success(auth_token, department):
    """Test successful full update (PUT) of a town"""
    assert created_town_id is not None, "Town ID is not set"
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Town {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}",
        "department_id": department["id"]
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{created_town_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

@add_test_info(
    description="Fallar al actualizar (PUT) un municipio con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="TOW-008"
)
@pytest.mark.asyncio
async def test_update_town_put_not_found(auth_token, department):
    """Test full update (PUT) of a non-existent town"""
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Town {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}",
        "department_id": department["id"]
    }
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Actualizar parcialmente (PATCH) un municipio exitosamente",
    expected_result="Status Code: 200, datos actualizados del municipio",
    module="Cobertura",
    test_id="TOW-009"
)
@pytest.mark.asyncio
async def test_update_town_patch_success(auth_token):
    """Test successful partial update (PATCH) of a town"""
    assert created_town_id is not None, "Town ID is not set"
    patch_data = {"name": "Patched Town Name"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{created_town_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == patch_data["name"]

@add_test_info(
    description="Fallar al actualizar (PATCH) un municipio con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="TOW-010"
)
@pytest.mark.asyncio
async def test_update_town_patch_not_found(auth_token):
    """Test partial update (PATCH) of a non-existent town"""
    patch_data = {"name": "Patched Town Name"}
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{non_existent_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Fallar al obtener municipio por DANE code inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="Cobertura",
    test_id="TOW-012"
)
@pytest.mark.asyncio
async def test_get_town_by_dane_code_not_found(auth_token):
    """Test get town by non-existent DANE code"""
    non_existent_dane = f"DANE{random.randint(100000, 999999)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/dane/{non_existent_dane}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Eliminar un municipio exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="Cobertura",
    test_id="TOW-013"
)
@pytest.mark.asyncio
async def test_delete_town_success(auth_token):
    """Test successful deletion of a town"""
    assert created_town_id is not None, "Town ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{created_town_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar un municipio con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="TOW-014"
)
@pytest.mark.asyncio
async def test_delete_town_not_found(auth_token):
    """Test deleting a non-existent town"""
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400 