"""
Integration tests for Parametrics/Options Endpoints
"""
import pytest
import httpx
from ..config import settings
from ..test_metadata import add_test_info

# Test Document Types
@add_test_info(
    description="Obtener la lista de tipos de documento exitosamente",
    expected_result="Status Code: 200, lista de tipos de documento",
    module="RH",
    test_id="PAR-RH-001"
)
@pytest.mark.asyncio
async def test_get_document_types_success(auth_token):
    """Test successful retrieval of document types list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/options/document-types",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@add_test_info(
    description="Fallar al obtener la lista de tipos de documento sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="RH",
    test_id="PAR-RH-002"
)
@pytest.mark.asyncio
async def test_get_document_types_unauthorized():
    """Test retrieving document types list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/document-types")
    assert response.status_code == 403

# Test Genders
@add_test_info(
    description="Obtener la lista de géneros exitosamente",
    expected_result="Status Code: 200, lista de géneros",
    module="RH",
    test_id="PAR-RH-003"
)
@pytest.mark.asyncio
async def test_get_genders_success(auth_token):
    """Test successful retrieval of genders list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/options/genders",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@add_test_info(
    description="Fallar al obtener la lista de géneros sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="RH",
    test_id="PAR-RH-004"
)
@pytest.mark.asyncio
async def test_get_genders_unauthorized():
    """Test retrieving genders list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/genders")
    assert response.status_code == 403

# Test Operational Roles
@add_test_info(
    description="Obtener la lista de roles operacionales exitosamente",
    expected_result="Status Code: 200, lista de roles operacionales",
    module="RH",
    test_id="PAR-RH-005"
)
@pytest.mark.asyncio
async def test_get_operational_roles_success(auth_token):
    """Test successful retrieval of operational roles list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/options/operational-roles",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de roles operacionales sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="RH",
    test_id="PAR-RH-006"
)
@pytest.mark.asyncio
async def test_get_operational_roles_unauthorized():
    """Test retrieving operational roles list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/operational-roles")
    assert response.status_code == 403

# Test Availability Statuses
@add_test_info(
    description="Obtener la lista de estados de disponibilidad exitosamente",
    expected_result="Status Code: 200, lista de estados de disponibilidad",
    module="RH",
    test_id="PAR-RH-007"
)
@pytest.mark.asyncio
async def test_get_availability_statuses_success(auth_token):
    """Test successful retrieval of availability statuses list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/options/availability-statuses",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

@add_test_info(
    description="Fallar al obtener la lista de estados de disponibilidad sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="RH",
    test_id="PAR-RH-008"
)
@pytest.mark.asyncio
async def test_get_availability_statuses_unauthorized():
    """Test retrieving availability statuses list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/availability-statuses")
    assert response.status_code == 403 