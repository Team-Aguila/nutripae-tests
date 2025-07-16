"""
Integration tests for Employees Endpoints
"""
import pytest
import httpx
import random
from datetime import date
from ..config import settings
from ..test_metadata import add_test_info

created_employee_id = None
created_employee_document = None

@add_test_info(
    description="Crear un empleado exitosamente",
    expected_result="Status Code: 201, datos del empleado creado",
    module="RH",
    test_id="EMP-001"
)
@pytest.mark.asyncio
async def test_create_employee_success(auth_token, document_type, gender, operational_role):
    """Test successful employee creation"""
    global created_employee_id, created_employee_document
    random_doc = f"DOC-{random.randint(100000, 999999)}"
    employee_data = {
        "document_number": random_doc,
        "full_name": "Test Employee",
        "birth_date": "1990-01-01",
        "hire_date": str(date.today()),
        "document_type_id": document_type["id"],
        "gender_id": gender["id"],
        "operational_role_id": operational_role["id"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/employees/",
            json=employee_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["document_number"] == employee_data["document_number"]
    created_employee_id = data["id"]
    created_employee_document = data["document_number"]

@add_test_info(
    description="Fallar al crear un empleado con datos faltantes",
    expected_result="Status Code: 422, error de validación",
    module="RH",
    test_id="EMP-002"
)
@pytest.mark.asyncio
async def test_create_employee_missing_data(auth_token, document_type, gender):
    """Test employee creation with missing required fields"""
    employee_data = {
        "document_number": f"DOC-{random.randint(100000, 999999)}",
        "full_name": "Test Employee",
        "birth_date": "1990-01-01",
        "hire_date": str(date.today()),
        "document_type_id": document_type["id"],
        "gender_id": gender["id"]
        # operational_role_id is missing
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/employees/",
            json=employee_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 422

@add_test_info(
    description="Obtener la lista de empleados exitosamente",
    expected_result="Status Code: 200, lista de empleados",
    module="RH",
    test_id="EMP-003"
)
@pytest.mark.asyncio
async def test_get_employees_success(auth_token):
    """Test successful retrieval of employees list"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/employees/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@add_test_info(
    description="Fallar al obtener la lista de empleados sin autorización",
    expected_result="Status Code: 403, error de autenticación",
    module="RH",
    test_id="EMP-004"
)
@pytest.mark.asyncio
async def test_get_employees_unauthorized():
    """Test retrieving employees list without auth token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/employees/")
    assert response.status_code == 403

@add_test_info(
    description="Obtener un empleado por ID exitosamente",
    expected_result="Status Code: 200, datos del empleado",
    module="RH",
    test_id="EMP-005"
)
@pytest.mark.asyncio
async def test_get_employee_by_id_success(auth_token):
    """Test successful retrieval of an employee by ID"""
    assert created_employee_id is not None, "Employee ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{created_employee_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["id"] == created_employee_id

@add_test_info(
    description="Fallar al obtener un empleado con un ID inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="EMP-006"
)
@pytest.mark.asyncio
async def test_get_employee_by_id_not_found(auth_token):
    """Test retrieving an employee with a non-existent ID"""
    non_existent_id = random.randint(99999, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Fallar al obtener un empleado con un documento inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="EMP-008"
)
@pytest.mark.asyncio
async def test_get_employee_by_document_not_found(auth_token):
    """Test retrieving an employee with a non-existent document number"""
    non_existent_doc = f"DOC-{random.randint(99999, 999999)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_RH_BACKEND_URL}/employees/document/{non_existent_doc}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404


@add_test_info(
    description="Actualizar (PUT) un empleado exitosamente",
    expected_result="Status Code: 200, datos actualizados del empleado",
    module="RH",
    test_id="EMP-009"
)
@pytest.mark.asyncio
async def test_update_employee_put_success(auth_token, document_type, gender, operational_role):
    """Test successful full update (PUT) of an employee"""
    assert created_employee_id is not None, "Employee ID is not set"
    update_data = {
        "document_number": f"DOC-UPDATED-{random.randint(100,999)}",
        "full_name": "Updated Employee",
        "birth_date": "1991-02-02",
        "hire_date": str(date.today()),
        "document_type_id": document_type["id"],
        "gender_id": gender["id"],
        "operational_role_id": operational_role["id"],
        "is_active": False
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{created_employee_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Employee"
    assert response.json()["is_active"] is False

@add_test_info(
    description="Fallar al actualizar (PUT) un empleado con un ID inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="EMP-010"
)
@pytest.mark.asyncio
async def test_update_employee_put_not_found(auth_token, document_type, gender, operational_role):
    """Test full update (PUT) of a non-existent employee"""
    non_existent_id = random.randint(99999, 999999)
    update_data = {
        "document_number": f"DOC-UPDATED-{random.randint(100,999)}",
        "full_name": "Updated Employee",
        "birth_date": "1991-02-02",
        "hire_date": str(date.today()),
        "document_type_id": document_type["id"],
        "gender_id": gender["id"],
        "operational_role_id": operational_role["id"],
        "is_active": False
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{non_existent_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404

@add_test_info(
    description="Eliminar un empleado exitosamente",
    expected_result="Status Code: 200, objeto vacío",
    module="RH",
    test_id="EMP-013"
)
@pytest.mark.asyncio
async def test_delete_employee_success(auth_token):
    """Test successful deletion of an employee"""
    assert created_employee_id is not None, "Employee ID is not set"
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{created_employee_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 200

@add_test_info(
    description="Fallar al eliminar un empleado con un ID inexistente",
    expected_result="Status Code: 404, no encontrado",
    module="RH",
    test_id="EMP-014"
)
@pytest.mark.asyncio
async def test_delete_employee_not_found(auth_token):
    """Test deleting a non-existent employee"""
    non_existent_id = random.randint(99999, 999999)
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 404 