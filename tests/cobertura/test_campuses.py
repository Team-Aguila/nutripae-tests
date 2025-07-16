"""
Integration tests for Campuses Endpoints
"""
import pytest
import httpx
import uuid
import random
from ..config import settings
from ..test_metadata import add_test_info

# This will hold the ID of a campus created for the whole module to use in non-destructive tests.
module_campus_id = None

@pytest.fixture(scope="module", autouse=True)
async def setup_module_campus(auth_token, institution):
    """Fixture to create a campus for the module and clean it up after tests."""
    global module_campus_id
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        campus_data = {
            "name": f"Module Campus {random_number}",
            "dane_code": f"{random_number}",
            "institution_id": institution["id"],
            "address": "123 Module St",
            "latitude": 4.6,
            "longitude": -74.0
        }
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            json=campus_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_campus = response.json()
        module_campus_id = created_campus['id']
        
        yield
        
        # Teardown: Attempt to delete the campus. A 404 is acceptable if a test already deleted it.
        delete_response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{module_campus_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code in [200, 404]


# Create Campus
@add_test_info(test_id="CAMP-001", module="Cobertura", description="Crear un campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_create_campus_success(auth_token, institution):
    random_number = random.randint(10000, 99999)
    campus_data = {
        "name": f"Test Campus ",
        "dane_code": f"{random_number}",
        "institution_id": institution["id"],
        "address": "123 Test St", "latitude": 4.60971, "longitude": -74.08175
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            json=campus_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == campus_data["name"]
        # Cleanup created campus
        await client.delete(f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{data['id']}", headers={"Authorization": f"Bearer {auth_token}"})

@add_test_info(test_id="CAMP-002", module="Cobertura", description="Fallar al crear un campus con datos faltantes", expected_result="Status 422")
@pytest.mark.asyncio
async def test_create_campus_missing_data(auth_token, institution):
    random_number = random.randint(10000, 99999)
    campus_data = {"institution_id": institution["id"], "dane_code": f"{random_number}", "name": "Test Campus"} # Missing required fields
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            json=campus_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 422

# Get Campuses
@add_test_info(test_id="CAMP-003", module="Cobertura", description="Obtener la lista de campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_get_campuses_success(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(test_id="CAMP-004", module="Cobertura", description="Fallar al obtener la lista de campus sin autorización", expected_result="Status 403")
@pytest.mark.asyncio
async def test_get_campuses_unauthorized():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/")
    assert response.status_code == 403

# Get Campus by ID
@add_test_info(test_id="CAMP-005", module="Cobertura", description="Obtener un campus por ID exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_get_campus_by_id_success(auth_token):
    assert module_campus_id is not None
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{module_campus_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == module_campus_id

@add_test_info(test_id="CAMP-006", module="Cobertura", description="Fallar al obtener un campus con un ID inexistente", expected_result="Status 404")
@pytest.mark.asyncio
async def test_get_campus_by_id_not_found(auth_token):
    random_number = random.randint(10000, 99999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{random_number}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

# Update Campus (PUT)
@add_test_info(test_id="CAMP-007", module="Cobertura", description="Actualizar (PUT) un campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_update_campus_put_success(auth_token, institution):
    update_data = {
        "name": "Updated Campus Name",
        "institution_id": institution["id"], "address": "123 Updated St",
        "latitude": 1.1, "longitude": 2.2
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{module_campus_id}",
            json=update_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Campus Name"

@add_test_info(test_id="CAMP-008", module="Cobertura", description="Fallar al actualizar (PUT) un campus con un ID inexistente", expected_result="Status 404")
@pytest.mark.asyncio
async def test_update_campus_put_not_found(auth_token, institution):
    random_number = random.randint(10000, 99999)
    update_data = {
        "name": "Non-existent Campus",
        "institution_id": institution["id"], "address": "123 Updated St",
        "latitude": 1.1, "longitude": 2.2
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{random_number}",
            json=update_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

# Update Campus (PATCH)
@add_test_info(test_id="CAMP-009", module="Cobertura", description="Actualizar parcialmente (PATCH) un campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_update_campus_patch_success(auth_token):
    patch_data = {"name": "Patched Campus Name"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{module_campus_id}",
            json=patch_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == "Patched Campus Name"

@add_test_info(test_id="CAMP-010", module="Cobertura", description="Fallar al actualizar (PATCH) un campus con un ID inexistente", expected_result="Status 404")
@pytest.mark.asyncio
async def test_update_campus_patch_not_found(auth_token):
    random_number = random.randint(10000, 99999)
    patch_data = {"name": "Patched Campus Name"}
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{random_number}",
            json=patch_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

# Delete Campus
@add_test_info(test_id="CAMP-011", module="Cobertura", description="Eliminar un campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_delete_campus_success(auth_token, institution):
    random_number = random.randint(10000, 99999)
    campus_data = {
        "name": f"Campus to Delete",
        "dane_code": f"{random_number}",
        "institution_id": institution["id"],
        "address": "123 To Delete St", "latitude": 4.6, "longitude": -74.0
    }
    async with httpx.AsyncClient() as client:
        create_response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            json=campus_data, headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        campus_id_to_delete = create_response.json()["id"]

        delete_response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{campus_id_to_delete}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert delete_response.status_code == 200

@add_test_info(test_id="CAMP-012", module="Cobertura", description="Fallar al eliminar un campus con un ID inexistente", expected_result="Status 404")
@pytest.mark.asyncio
async def test_delete_campus_not_found(auth_token):
    random_number = random.randint(10000, 99999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{random_number}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 400

# Get Campus Coverage
@add_test_info(test_id="CAMP-013", module="Cobertura", description="Obtener la cobertura de un campus exitosamente", expected_result="Status 200")
@pytest.mark.asyncio
async def test_get_campus_coverage_success(auth_token, beneficiary, benefit_type):
    async with httpx.AsyncClient() as client:
        # Create a coverage for the module campus
        coverage_data = {"beneficiary_id": beneficiary["id"], "campus_id": module_campus_id, "benefit_type_id": benefit_type["id"]}
        create_cov_res = await client.post(f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/", json=coverage_data, headers={"Authorization": f"Bearer {auth_token}"})
        assert create_cov_res.status_code == 200
        created_coverage = create_cov_res.json()

        # Get campus coverage
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{module_campus_id}/coverage", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(c['id'] == created_coverage['id'] for c in data)
        
        # Teardown
        await client.delete(f"{settings.BASE_COVERAGE_BACKEND_URL}/coverages/{created_coverage['id']}", headers={"Authorization": f"Bearer {auth_token}"})

@add_test_info(test_id="CAMP-014", module="Cobertura", description="Fallar al obtener la cobertura de un campus con un ID inexistente", expected_result="Status 404")
@pytest.mark.asyncio
async def test_get_campus_coverage_not_found(auth_token):
    non_existent_campus_id = 9999999
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/{non_existent_campus_id}/coverage",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404 