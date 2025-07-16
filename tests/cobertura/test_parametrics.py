"""
Integration tests for Parametrics Endpoints
"""
import pytest
import httpx
from ..config import settings
from ..test_metadata import add_test_info

# Test Benefit Types
@add_test_info(
    description="Obtener la lista de tipos de beneficio exitosamente",
    expected_result="Status Code: 200, lista de tipos de beneficio",
    module="Cobertura",
    test_id="PAR-001"
)
@pytest.mark.asyncio
async def test_get_benefit_types_success(auth_token):
    """Test successful retrieval of benefit types list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/benefit-types",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de tipos de beneficio sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="PAR-002"
)
@pytest.mark.asyncio
async def test_get_benefit_types_unauthorized():
    """Test retrieving benefit types list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/benefit-types")
    assert response.status_code == 403

# Test Document Types
@add_test_info(
    description="Obtener la lista de tipos de documento exitosamente",
    expected_result="Status Code: 200, lista de tipos de documento",
    module="Cobertura",
    test_id="PAR-003"
)
@pytest.mark.asyncio
async def test_get_document_types_success(auth_token):
    """Test successful retrieval of document types list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/document-types",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@add_test_info(
    description="Fallar al obtener la lista de tipos de documento sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="PAR-004"
)
@pytest.mark.asyncio
async def test_get_document_types_unauthorized():
    """Test retrieving document types list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/document-types")
    assert response.status_code == 403

# Test Genders
@add_test_info(
    description="Obtener la lista de géneros exitosamente",
    expected_result="Status Code: 200, lista de géneros",
    module="Cobertura",
    test_id="PAR-005"
)
@pytest.mark.asyncio
async def test_get_genders_success(auth_token):
    """Test successful retrieval of genders list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/genders",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@add_test_info(
    description="Fallar al obtener la lista de géneros sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="PAR-006"
)
@pytest.mark.asyncio
async def test_get_genders_unauthorized():
    """Test retrieving genders list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/genders")
    assert response.status_code == 403

# Test Grades
@add_test_info(
    description="Obtener la lista de grados exitosamente",
    expected_result="Status Code: 200, lista de grados",
    module="Cobertura",
    test_id="PAR-007"
)
@pytest.mark.asyncio
async def test_get_grades_success(auth_token):
    """Test successful retrieval of grades list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/grades",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de grados sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="PAR-008"
)
@pytest.mark.asyncio
async def test_get_grades_unauthorized():
    """Test retrieving grades list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/grades")
    assert response.status_code == 403

# Test Ethnic Groups
@add_test_info(
    description="Obtener la lista de grupos étnicos exitosamente",
    expected_result="Status Code: 200, lista de grupos étnicos",
    module="Cobertura",
    test_id="PAR-009"
)
@pytest.mark.asyncio
async def test_get_ethnic_groups_success(auth_token):
    """Test successful retrieval of ethnic groups list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/etnic-groups",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@add_test_info(
    description="Fallar al obtener la lista de grupos étnicos sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="Cobertura",
    test_id="PAR-010"
)
@pytest.mark.asyncio
async def test_get_ethnic_groups_unauthorized():
    """Test retrieving ethnic groups list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/etnic-groups")
    assert response.status_code == 403 