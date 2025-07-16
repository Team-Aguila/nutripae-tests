"""
Integration tests for Daily Availabilities Endpoints
"""
import pytest
import httpx
import random
from datetime import date, timedelta
from ..config import settings
from ..test_metadata import add_test_info

created_availability_id = None

@add_test_info(
    description="Crear un registro de disponibilidad diaria exitosamente",
    expected_result="Status Code: 201, datos de la disponibilidad creada",
    module="RH",
    test_id="AVA-001"
)
@pytest.mark.asyncio
async def test_create_availability_success(auth_token, employee, availability_status):
    """Test successful daily availability creation"""
    global created_availability_id
    availability_data = {
        "employee_id": employee["id"],
        "date": str(date.today()),
        "status_id": availability_status["id"],
        "notes": "Test note"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/",
            json=availability_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == availability_data["employee_id"]
    created_availability_id = data["id"]

@add_test_info(
    description="Fallar al crear un registro de disponibilidad con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="RH",
    test_id="AVA-002"
)
@pytest.mark.asyncio
async def test_create_availability_missing_data(auth_token, employee):
    """Test daily availability creation with missing required fields"""
    availability_data = {
        "employee_id": employee["id"],
        "date": str(date.today())
        # status_id is missing
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/",
            json=availability_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de disponibilidades exitosamente",
    expected_result="Status Code: 200, lista de disponibilidades",
    module="RH",
    test_id="AVA-003"
)
@pytest.mark.asyncio
async def test_get_availabilities_success(auth_token):
    """Test successful retrieval of availabilities list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Obtener una disponibilidad por ID exitosamente",
    expected_result="Status Code: 200, datos de la disponibilidad",
    module="RH",
    test_id="AVA-004"
)
@pytest.mark.asyncio
async def test_get_availability_by_id_success(auth_token):
    """Test successful retrieval of an availability by ID"""
    assert created_availability_id is not None, "Availability ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/{created_availability_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_availability_id

@add_test_info(
    description="Fallar al obtener una disponibilidad con un ID inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="AVA-005"
)
@pytest.mark.asyncio
async def test_get_availability_by_id_not_found(auth_token):
    """Test retrieving an availability with a non-existent ID"""
    non_existent_id = random.randint(99999, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Actualizar (PUT) una disponibilidad exitosamente",
    expected_result="Status Code: 200, datos actualizados de la disponibilidad",
    module="RH",
    test_id="AVA-006"
)
@pytest.mark.asyncio
async def test_update_availability_put_success(auth_token, employee, availability_status):
    """Test successful full update (PUT) of an availability"""
    assert created_availability_id is not None, "Availability ID is not set"
    update_data = {
        "employee_id": employee["id"],
        "date": str(date.today()),
        "status_id": availability_status["id"],
        "notes": "Updated note"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/{created_availability_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["notes"] == "Updated note"

@add_test_info(
    description="Obtener disponibilidades por ID de empleado exitosamente",
    expected_result="Status Code: 200, lista de disponibilidades para el empleado",
    module="RH",
    test_id="AVA-007"
)
@pytest.mark.asyncio
async def test_get_availabilities_by_employee_id_success(auth_token, employee):
    """Test successful retrieval of availabilities for a specific employee"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/employee/{employee['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Crear disponibilidades en lote exitosamente",
    expected_result="Status Code: 201, lista de disponibilidades creadas",
    module="RH",
    test_id="AVA-008"
)
@pytest.mark.asyncio
async def test_create_bulk_availabilities_success(auth_token, employee, availability_status):
    """Test successful bulk creation of availabilities"""
    availabilities_data = [
        {
            "employee_id": employee["id"],
            "date": str(date.today() + timedelta(days=1)),
            "status_id": availability_status["id"]
        },
        {
            "employee_id": employee["id"],
            "date": str(date.today() + timedelta(days=2)),
            "status_id": availability_status["id"]
        }
    ]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/bulk",
            json=availabilities_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 201
    assert len(response.json()) == 2

@add_test_info(
    description="Eliminar una disponibilidad exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="RH",
    test_id="AVA-009"
)
@pytest.mark.asyncio
async def test_delete_availability_success(auth_token):
    """Test successful deletion of an availability"""
    assert created_availability_id is not None, "Availability ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/{created_availability_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar una disponibilidad con un ID inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="AVA-010"
)
@pytest.mark.asyncio
async def test_delete_availability_not_found(auth_token):
    """Test deleting a non-existent availability"""
    non_existent_id = random.randint(99999, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_RH_BACKEND_URL}/availabilities/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404 