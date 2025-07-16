"""
Integration tests for Institutions Endpoints
"""
import pytest
import httpx
import random
from ..config import settings
from ..test_metadata import add_test_info

created_institution_id = None
created_institution_dane_code = None

@add_test_info(
    description="Crear una institución exitosamente",
    expected_result="Status Code: 200, datos de la institución creada",
    module="Cobertura",
    test_id="INS-001"
)
@pytest.mark.asyncio
async def test_create_institution_success(auth_token, town):
    """Test successful institution creation"""
    global created_institution_id, created_institution_dane_code
    random_number = random.randint(10000, 99999)
    institution_data = {
        "name": f"Test Institution {random_number}",
        "dane_code": f"DANE{random_number}",
        "town_id": town["id"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/",
            json=institution_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == institution_data["name"]
    created_institution_id = data["id"]
    created_institution_dane_code = data["dane_code"]

@add_test_info(
    description="Fallar al crear una institución con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="Cobertura",
    test_id="INS-002"
)
@pytest.mark.asyncio
async def test_create_institution_missing_data(auth_token, town):
    """Test institution creation with missing required fields"""
    institution_data = {
        "name": "Incomplete Institution",
        "town_id": town["id"]
        # Missing dane_code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/",
            json=institution_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de instituciones exitosamente",
    expected_result="Status Code: 200, lista de instituciones",
    module="Cobertura",
    test_id="INS-003"
)
@pytest.mark.asyncio
async def test_get_institutions_success(auth_token):
    """Test successful retrieval of institutions list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de instituciones sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="INS-004"
)
@pytest.mark.asyncio
async def test_get_institutions_unauthorized():
    """Test retrieving institutions list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener una institución por ID exitosamente",
    expected_result="Status Code: 200, datos de la institución",
    module="Cobertura",
    test_id="INS-005"
)
@pytest.mark.asyncio
async def test_get_institution_by_id_success(auth_token):
    """Test successful retrieval of an institution by ID"""
    assert created_institution_id is not None, "Institution ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{created_institution_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_institution_id

@add_test_info(
    description="Fallar al obtener una institución con un ID inexistente",
    expected_result="Status Code: 404, error no encontrado",
    module="Cobertura",
    test_id="INS-006"
)
@pytest.mark.asyncio
async def test_get_institution_by_id_not_found(auth_token):
    """Test retrieving an institution with a non-existent ID"""
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) una institución exitosamente",
    expected_result="Status Code: 200, datos actualizados de la institución",
    module="Cobertura",
    test_id="INS-007"
)
@pytest.mark.asyncio
async def test_update_institution_put_success(auth_token, town):
    """Test successful full update (PUT) of an institution"""
    assert created_institution_id is not None, "Institution ID is not set"
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Institution {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}",
        "town_id": town["id"]
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{created_institution_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

@add_test_info(
    description="Fallar al actualizar (PUT) una institución con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="INS-008"
)
@pytest.mark.asyncio
async def test_update_institution_put_not_found(auth_token, town):
    """Test full update (PUT) of a non-existent institution"""
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": f"Updated Institution {random_number}",
        "dane_code": f"DANE-UPDATED-{random_number}",
        "town_id": town["id"]
    }
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Actualizar parcialmente (PATCH) una institución exitosamente",
    expected_result="Status Code: 200, datos actualizados de la institución",
    module="Cobertura",
    test_id="INS-009"
)
@pytest.mark.asyncio
async def test_update_institution_patch_success(auth_token):
    """Test successful partial update (PATCH) of an institution"""
    assert created_institution_id is not None, "Institution ID is not set"
    patch_data = {"name": "Patched Institution Name"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{created_institution_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == patch_data["name"]

@add_test_info(
    description="Fallar al actualizar (PATCH) una institución con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="INS-010"
)
@pytest.mark.asyncio
async def test_update_institution_patch_not_found(auth_token):
    """Test partial update (PATCH) of a non-existent institution"""
    patch_data = {"name": "Patched Institution Name"}
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{non_existent_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Fallar al obtener institución por DANE code inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="Cobertura",
    test_id="INS-012"
)
@pytest.mark.asyncio
async def test_get_institution_by_dane_code_not_found(auth_token):
    """Test get institution by non-existent DANE code"""
    non_existent_dane = f"DANE{random.randint(100000, 999999)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/dane/{non_existent_dane}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404


@add_test_info(
    description="Eliminar una institución exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="Cobertura",
    test_id="INS-013"
)
@pytest.mark.asyncio
async def test_delete_institution_success(auth_token):
    """Test successful deletion of an institution"""
    assert created_institution_id is not None, "Institution ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{created_institution_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar una institución con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="INS-014"
)
@pytest.mark.asyncio
async def test_delete_institution_not_found(auth_token):
    """Test deleting a non-existent institution"""
    non_existent_id = random.randint(100000, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400 