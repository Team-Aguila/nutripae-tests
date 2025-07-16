"""
Integration tests for Coverages Endpoints
"""
import pytest
import httpx
import uuid
from datetime import datetime
from ..config import settings
from ..test_metadata import add_test_info

created_coverage_id = None

@add_test_info(
    description="Crear una cobertura exitosamente",
    expected_result="Status Code: 200, datos de la cobertura creada",
    module="Cobertura",
    test_id="COV-001"
)
@pytest.mark.asyncio
async def test_create_coverage_success(auth_token, beneficiary, campus, benefit_type):
    """Test successful coverage creation"""
    global created_coverage_id
    coverage_data = {
        "beneficiary_id": beneficiary["id"],
        "campus_id": campus["id"],
        "benefit_type_id": benefit_type["id"],
        "year": datetime.now().year
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/",
            json=coverage_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["beneficiary_id"] == coverage_data["beneficiary_id"]
    created_coverage_id = data["id"]

@add_test_info(
    description="Fallar al crear una cobertura con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="Cobertura",
    test_id="COV-002"
)
@pytest.mark.asyncio
async def test_create_coverage_missing_data(auth_token, beneficiary, campus):
    """Test coverage creation with missing required fields"""
    coverage_data = {
        "beneficiary_id": beneficiary["id"],
        "campus_id": campus["id"],
        # "benefit_type_id": benefit_type["id"], <- Missing
        "year": datetime.now().year
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/",
            json=coverage_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de coberturas exitosamente",
    expected_result="Status Code: 200, lista de coberturas",
    module="Cobertura",
    test_id="COV-003"
)
@pytest.mark.asyncio
async def test_get_coverages_success(auth_token):
    """Test successful retrieval of coverages list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de coberturas sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="COV-004"
)
@pytest.mark.asyncio
async def test_get_coverages_unauthorized():
    """Test retrieving coverages list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener una cobertura por ID exitosamente",
    expected_result="Status Code: 200, datos de la cobertura",
    module="Cobertura",
    test_id="COV-005"
)
@pytest.mark.asyncio
async def test_get_coverage_by_id_success(auth_token):
    """Test successful retrieval of a coverage by ID"""
    assert created_coverage_id is not None, "Coverage ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{created_coverage_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_coverage_id

@add_test_info(
    description="Fallar al obtener una cobertura con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="COV-006"
)
@pytest.mark.asyncio
async def test_get_coverage_by_id_not_found(auth_token):
    """Test retrieving a coverage with a non-existent ID"""
    non_existent_id = uuid.uuid4()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) una cobertura exitosamente",
    expected_result="Status Code: 200, datos actualizados de la cobertura",
    module="Cobertura",
    test_id="COV-007"
)
@pytest.mark.asyncio
async def test_update_coverage_put_success(auth_token, beneficiary, campus, benefit_type):
    """Test successful full update (PUT) of a coverage"""
    assert created_coverage_id is not None, "Coverage ID is not set"
    update_data = {
        "beneficiary_id": beneficiary["id"],
        "campus_id": campus["id"],
        "benefit_type_id": benefit_type["id"],
        "active": True,
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{created_coverage_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["active"] == update_data["active"]

@add_test_info(
    description="Fallar al actualizar (PUT) una cobertura con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="COV-008"
)
@pytest.mark.asyncio
async def test_update_coverage_put_not_found(auth_token, beneficiary, campus, benefit_type):
    """Test full update (PUT) of a non-existent coverage"""
    update_data = {
        "beneficiary_id": beneficiary["id"],
        "campus_id": campus["id"],
        "benefit_type_id": benefit_type["id"],
        "active": True,
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{uuid.uuid4()}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Actualizar parcialmente (PATCH) una cobertura exitosamente",
    expected_result="Status Code: 200, datos actualizados de la cobertura",
    module="Cobertura",
    test_id="COV-009"
)
@pytest.mark.asyncio
async def test_update_coverage_patch_success(auth_token):
    """Test successful partial update (PATCH) of a coverage"""
    assert created_coverage_id is not None, "Coverage ID is not set"
    patch_data = {"active": False}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{created_coverage_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["active"] == patch_data["active"]

@add_test_info(
    description="Fallar al actualizar (PATCH) una cobertura con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="COV-010"
)
@pytest.mark.asyncio
async def test_update_coverage_patch_not_found(auth_token):
    """Test partial update (PATCH) of a non-existent coverage"""
    patch_data = {"year": datetime.now().year + 2}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{uuid.uuid4()}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Eliminar una cobertura exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="Cobertura",
    test_id="COV-011"
)
@pytest.mark.asyncio
async def test_delete_coverage_success(auth_token):
    """Test successful deletion of a coverage"""
    assert created_coverage_id is not None, "Coverage ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{created_coverage_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar una cobertura con un ID inexistente",
    expected_result="Status Code: 400, error de solicitud incorrecta",
    module="Cobertura",
    test_id="COV-012"
)
@pytest.mark.asyncio
async def test_delete_coverage_not_found(auth_token):
    """Test deleting a non-existent coverage"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400 