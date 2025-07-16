import pytest
import httpx
import random
from ..config import settings

@pytest.fixture(scope="module")
async def document_type(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/document-types", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        yield data[0]

@pytest.fixture(scope="module")
async def gender(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/genders", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        yield data[0]

@pytest.fixture(scope="module")
async def operational_role(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/operational-roles", headers={"Authorization": f"Bearer {auth_token}"})
        if response.status_code == 200 and response.json():
            yield response.json()[0]
        else:
            random_number = random.randint(100, 999)
            role_data = {"name": f"Test Role {random_number}"}
            # Assuming a POST endpoint exists for operational roles for testing purposes
            response = await client.post(f"{settings.BASE_RH_BACKEND_URL}/operational-roles/", json=role_data, headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 201
            yield response.json()

@pytest.fixture(scope="module")
async def availability_status(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_RH_BACKEND_URL}/options/availability-statuses", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        yield data[0]

@pytest.fixture(scope="module")
async def employee(auth_token, document_type, gender, operational_role):
    async with httpx.AsyncClient() as client:
        random_doc = f"EMP-FIXTURE-{random.randint(100000, 999999)}"
        employee_data = {
            "document_number": random_doc,
            "full_name": "Fixture Employee",
            "birth_date": "1985-01-01",
            "hire_date": "2023-01-01",
            "document_type_id": document_type["id"],
            "gender_id": gender["id"],
            "operational_role_id": operational_role["id"]
        }
        response = await client.post(
            f"{settings.BASE_RH_BACKEND_URL}/employees/",
            json=employee_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        created_employee = response.json()
        yield created_employee

        # Teardown: delete the employee after tests in the module are done
        await client.delete(
            f"{settings.BASE_RH_BACKEND_URL}/employees/{created_employee['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        ) 