import pytest
import httpx
import uuid
import random
from ..config import settings

# Fixture to create a department and clean up afterwards
@pytest.fixture(scope="module")
async def department(auth_token):
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        # Create department
        department_data = {"name": f"Test Department-{random_number}", "dane_code": f"{random_number}"}
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/",
            json=department_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_department = response.json()
        yield created_department

        # Teardown: delete department
        await client.delete(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/departments/{created_department['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

# Fixture to create a town and clean up afterwards
@pytest.fixture(scope="module")
async def town(auth_token, department):
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        town_data = {"name": f"Test Town-{random_number}", "dane_code": f"{random_number}", "department_id": department["id"]}
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/towns/",
            json=town_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_town = response.json()
        yield created_town

# Fixture to create an institution
@pytest.fixture(scope="module")
async def institution(auth_token, town):
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        institution_data = {
            "name": f"Test Institution-{random_number}",
            "dane_code": f"{random_number}",
            "town_id": town["id"]
        }
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/institutions/",
            json=institution_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_institution = response.json()
        yield created_institution


# Fixture to create a campus
@pytest.fixture(scope="module")
async def campus(auth_token, institution):
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        campus_data = {
            "name": f"Test Campus-{random_number}",
            "dane_code": f"{random_number}",
            "institution_id": institution["id"],
            "address": "123 Test St",
            "latitude": 4.60971,
            "longitude": -74.08175
        }
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/campuses/",
            json=campus_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_campus = response.json()
        yield created_campus

# Parametric data fixtures
@pytest.fixture(scope="module")
async def benefit_type(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/benefit-types",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200 and response.json():
            yield response.json()[0]
        else:
            benefit_data = {"name": f"Test Benefit Type-{random_number}"}
            response = await client.post(
                f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/benefit-types",
                json=benefit_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code == 200
            yield response.json()


@pytest.fixture(scope="module")
async def document_type(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/document-types", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        yield response.json()[0]

@pytest.fixture(scope="module")
async def gender(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/genders", headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        yield response.json()[0]

@pytest.fixture(scope="module")
async def grade(auth_token):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/grades", headers={"Authorization": f"Bearer {auth_token}"})
        if response.status_code == 200 and response.json():
            yield response.json()[0]
        else:
            grade_data = {"name": f"Test Grade-{random_number}"}
            response = await client.post(f"{settings.BASE_COVERAGE_BACKEND_URL}/parametrics/grades", json=grade_data, headers={"Authorization": f"Bearer {auth_token}"})
            assert response.status_code == 200
            yield response.json()


# Fixture to create a beneficiary
@pytest.fixture(scope="module")
async def beneficiary(auth_token, document_type, gender, grade):
    async with httpx.AsyncClient() as client:
        random_number = random.randint(10000, 99999)
        beneficiary_data = {
            "document_type_id": document_type["id"],
            "number_document": f"{random_number}",
            "first_name": f"Test-{random_number}",
            "first_surname": f"Beneficiary-{random_number}",
            "birth_date": "2010-01-01",
            "gender_id": gender["id"],
            "grade_id": grade["id"],
            "second_name": f"Fixture-{random_number}        ",
            "second_surname": f"Beneficiary-{random_number}",
            "etnic_group_id": 1
        }
        response = await client.post(
            f"{settings.BASE_COVERAGE_BACKEND_URL}/beneficiaries/",
            json=beneficiary_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        created_beneficiary = response.json()
        yield created_beneficiary 