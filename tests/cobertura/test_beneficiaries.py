"""
Integration tests for Beneficiaries Endpoints
"""
import pytest
import httpx
import uuid
import random
from ..config import settings
from ..test_metadata import add_test_info

created_beneficiary_id = None

@add_test_info(
    description="Crear un beneficiario exitosamente",
    expected_result="Status Code: 200, datos del beneficiario creado",
    module="Cobertura",
    test_id="BEN-001"
)
@pytest.mark.asyncio
async def test_create_beneficiary_success(auth_token, document_type, gender, grade):
    """Test successful beneficiary creation"""
    global created_beneficiary_id
    random_number = random.randint(10000, 99999)
    beneficiary_data = {
        "document_type_id": document_type["id"],
        "number_document": f"{random_number}",
        "first_name": "Test",
        "first_surname": "User",
        "birth_date": "2010-05-20",
        "gender_id": gender["id"],
        "grade_id": grade["id"],
        "second_name": "Second",
        "second_surname": "Surname",
        "etnic_group_id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/",
            json=beneficiary_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["number_document"] == beneficiary_data["number_document"]
    created_beneficiary_id = data["id"] # Save for subsequent tests

@add_test_info(
    description="Fallar al crear un beneficiario con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="Cobertura",
    test_id="BEN-002"
)
@pytest.mark.asyncio
async def test_create_beneficiary_missing_data(auth_token, document_type, gender, grade):
    """Test beneficiary creation with missing required fields"""
    random_number = random.randint(10000, 99999)
    beneficiary_data = {
        "document_type_id": document_type["id"],
        "number_document": f"{random_number}",
        # "first_name": "Test",  <- Missing first_name
        "first_surname": "User",
        "birth_date": "2010-05-20",
        "gender_id": gender["id"],
        "grade_id": grade["id"],
        "etnic_group_id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/",
            json=beneficiary_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de beneficiarios exitosamente",
    expected_result="Status Code: 200, lista de beneficiarios",
    module="Cobertura",
    test_id="BEN-003"
)
@pytest.mark.asyncio
async def test_get_beneficiaries_success(auth_token):
    """Test successful retrieval of beneficiaries list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de beneficiarios sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="BEN-004"
)
@pytest.mark.asyncio
async def test_get_beneficiaries_unauthorized():
    """Test retrieving beneficiaries list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener un beneficiario por ID exitosamente",
    expected_result="Status Code: 200, datos del beneficiario",
    module="Cobertura",
    test_id="BEN-005"
)
@pytest.mark.asyncio
async def test_get_beneficiary_by_id_success(auth_token):
    """Test successful retrieval of a beneficiary by ID"""
    assert created_beneficiary_id is not None, "Beneficiary ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{created_beneficiary_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_beneficiary_id

@add_test_info(
    description="Fallar al obtener un beneficiario con un ID inexistente",
    expected_result="Status Code: 404, error de no encontrado",
    module="Cobertura",
    test_id="BEN-006"
)
@pytest.mark.asyncio
async def test_get_beneficiary_by_id_not_found(auth_token):
    """Test retrieving a beneficiary with a non-existent ID"""
    non_existent_id = uuid.uuid4()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) un beneficiario exitosamente",
    expected_result="Status Code: 200, datos actualizados del beneficiario",
    module="Cobertura",
    test_id="BEN-007"
)
@pytest.mark.asyncio
async def test_update_beneficiary_put_success(auth_token, document_type, gender, grade):
    """Test successful full update (PUT) of a beneficiary"""
    assert created_beneficiary_id is not None, "Beneficiary ID is not set"
    random_number = random.randint(10000, 99999)
    update_data = {
        "document_type_id": document_type["id"],
        "number_document": f"{random_number}",
        "first_name": "Updated",
        "first_surname": "User",
        "birth_date": "2011-01-01",
        "gender_id": gender["id"],
        "grade_id": grade["id"],
        "second_name": "Second Updated",
        "second_surname": "Surname Updated",
        "etnic_group_id": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{created_beneficiary_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"

@add_test_info(
    description="Fallar al actualizar (PUT) un beneficiario con un ID inexistente",
    expected_result="Status Code: 404, error de no encontrado",
    module="Cobertura",
    test_id="BEN-008"
)
@pytest.mark.asyncio
async def test_update_beneficiary_put_not_found(auth_token, document_type, gender, grade):
    """Test full update (PUT) of a non-existent beneficiary"""
    random_number = random.randint(10000, 99999)
    update_data = {
        "document_type_id": document_type["id"],
        "number_document": f"{random_number}",
        "first_name": "Updated",
        "first_surname": "User",
        "birth_date": "2011-01-01",
        "gender_id": gender["id"],
        "grade_id": grade["id"],
        "second_name": "Second Updated",
        "second_surname": "Surname Updated",
        "etnic_group_id": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{uuid.uuid4()}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Actualizar parcialmente (PATCH) un beneficiario exitosamente",
    expected_result="Status Code: 200, datos actualizados del beneficiario",
    module="Cobertura",
    test_id="BEN-009"
)
@pytest.mark.asyncio
async def test_update_beneficiary_patch_success(auth_token):
    """Test successful partial update (PATCH) of a beneficiary"""
    assert created_beneficiary_id is not None, "Beneficiary ID is not set"
    patch_data = {"first_name": "Patched"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{created_beneficiary_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Patched"

@add_test_info(
    description="Fallar al actualizar (PATCH) un beneficiario con un ID inexistente",
    expected_result="Status Code: 404, error de no encontrado",
    module="Cobertura",
    test_id="BEN-010"
)
@pytest.mark.asyncio
async def test_update_beneficiary_patch_not_found(auth_token):
    """Test partial update (PATCH) of a non-existent beneficiary"""
    non_existent_id = uuid.uuid4()
    patch_data = {"first_name": "Patched"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{non_existent_id}",
            json=patch_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

@add_test_info(
    description="Eliminar un beneficiario exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="Cobertura",
    test_id="BEN-011"
)
@pytest.mark.asyncio
async def test_delete_beneficiary_success(auth_token):
    """Test successful deletion of a beneficiary"""
    assert created_beneficiary_id is not None, "Beneficiary ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{created_beneficiary_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar un beneficiario con un ID inexistente",
    expected_result="Status Code: 404, error de no encontrado",
    module="Cobertura",
    test_id="BEN-012"
)
@pytest.mark.asyncio
async def test_delete_beneficiary_not_found(auth_token):
    """Test deleting a non-existent beneficiary"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400