"""
Shared pytest fixtures for PAE Menus API integration tests
"""
import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from bson import ObjectId

from .config import TestConfig


@pytest.fixture
async def client():
    """HTTP client fixture for making API requests"""
    async with httpx.AsyncClient(
        base_url=TestConfig.BASE_URL,
        timeout=TestConfig.TIMEOUT,
        follow_redirects=TestConfig.FOLLOW_REDIRECTS
    ) as client:
        yield client


@pytest.fixture
def api_prefix():
    """API prefix fixture"""
    return TestConfig.API_PREFIX


@pytest.fixture
async def test_ingredient(client: httpx.AsyncClient, api_prefix: str):
    """Create a test ingredient and clean up after test"""
    ingredient_data = {
        "name": "Test Ingredient Integration",
        "base_unit_of_measure": "kg",
        "status": "active",
        "description": "Test ingredient for integration tests",
        "category": "test_category",
        "nutritional_info": {
            "per_100g": {
                "calories": 300.0,
                "protein": 8.0,
                "carbohydrates": 60.0,
                "fat": 2.0,
                "fiber": 3.0,
                "sodium": 10.0
            }
        }
    }
    
    # Create ingredient
    response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
    assert response.status_code == 201
    ingredient = response.json()
    
    yield ingredient
    
    # Cleanup: Delete ingredient
    try:
        ingredient_id = ingredient.get("id")
        if ingredient_id:
            await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_ingredient_2(client: httpx.AsyncClient, api_prefix: str):
    """Create a second test ingredient for complex recipes"""
    ingredient_data = {
        "name": "Test Ingredient 2 Integration",
        "base_unit_of_measure": "g",
        "status": "active",
        "description": "Second test ingredient for integration tests",
        "category": "test_category_2",
        "nutritional_info": {
            "per_100g": {
                "calories": 150.0,
                "protein": 20.0,
                "carbohydrates": 5.0,
                "fat": 8.0,
                "fiber": 1.0,
                "sodium": 200.0
            }
        }
    }
    
    # Create ingredient
    response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
    assert response.status_code == 201
    ingredient = response.json()
    
    yield ingredient
    
    # Cleanup: Delete ingredient
    try:
        ingredient_id = ingredient.get("id")
        if ingredient_id:
            await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_dish(client: httpx.AsyncClient, api_prefix: str, test_ingredient, test_ingredient_2):
    """Create a test dish and clean up after test"""
    ingredient_id_1 = test_ingredient.get("id")
    ingredient_id_2 = test_ingredient_2.get("id")
    
    dish_data = {
        "name": "Test Dish Integration",
        "description": "Test dish for integration tests",
        "status": "active",
        "compatible_meal_types": ["almuerzo"],  # Use Spanish values
        "recipe": {
            "ingredients": [
                {
                    "ingredient_id": ingredient_id_1,
                    "quantity": 200.0,
                    "unit": "g"
                },
                {
                    "ingredient_id": ingredient_id_2,
                    "quantity": 100.0,
                    "unit": "g"
                }
            ]
        },
        "nutritional_info": {
            "calories": 350.0,
            "protein": 15.0,
            "carbohydrates": 45.0,
            "fat": 8.0,
            "fiber": 2.0,
            "sodium": 120.0,
            "photo_url": "https://example.com/test-dish.jpg"
        },
        "dish_type": "protein"
    }
    
    # Create dish
    response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
    assert response.status_code == 201
    dish = response.json()
    
    yield dish
    
    # Cleanup: Delete dish
    try:
        dish_id = dish.get("id")
        if dish_id:
            await client.delete(f"{api_prefix}/dishes/{dish_id}")
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_menu_cycle(client: httpx.AsyncClient, api_prefix: str, test_dish):
    """Create a test menu cycle and clean up after test"""
    dish_id = test_dish.get("id")
    
    cycle_data = {
        "name": "Test Menu Cycle Integration",
        "description": "Test menu cycle for integration tests",
        "status": "active",
        "duration_days": 7,
        "daily_menus": [
            {
                "day": 1,
                "breakfast_dish_ids": [],
                "lunch_dish_ids": [dish_id],
                "snack_dish_ids": []
            },
            {
                "day": 2,
                "breakfast_dish_ids": [],
                "lunch_dish_ids": [dish_id],
                "snack_dish_ids": []
            }
        ]
    }
    
    # Create menu cycle
    response = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
    if response.status_code == 201:
        cycle = response.json()
        yield cycle
        
        # Cleanup: Delete menu cycle
        try:
            cycle_id = cycle.get("id")
            if cycle_id:
                await client.delete(f"{api_prefix}/menu-cycles/{cycle_id}")
        except Exception:
            pass  # Ignore cleanup errors
    else:
        # If we can't create the cycle, yield None and let tests handle it
        yield None


@pytest.fixture
async def test_menu_schedule(client: httpx.AsyncClient, api_prefix: str, test_menu_cycle):
    """Create a test menu schedule via assignment and clean up after test"""
    if not test_menu_cycle:
        yield None
        return
        
    cycle_id = test_menu_cycle.get("id")  # This is already a string from the API response
    
    assignment_data = {
        "menu_cycle_id": cycle_id,  # String ID as expected by MenuScheduleAssignmentRequest
        "campus_ids": ["test_campus_1"],
        "town_ids": ["test_town_1"],
        "start_date": "2024-02-01",
        "end_date": "2024-02-28"
    }
    
    # Create menu schedule via assignment
    response = await client.post(f"{api_prefix}/menu-schedules/assign", json=assignment_data)
    if response.status_code == 201:
        assignment_result = response.json()
        schedule_id = assignment_result.get("schedule_id")
        if schedule_id:
            # Get the created schedule
            get_response = await client.get(f"{api_prefix}/menu-schedules/{schedule_id}")
            if get_response.status_code == 200:
                schedule = get_response.json()
                yield schedule
                
                # Cleanup: Delete menu schedule
                try:
                    await client.delete(f"{api_prefix}/menu-schedules/{schedule_id}")
                except Exception:
                    pass  # Ignore cleanup errors
            else:
                yield None
        else:
            yield None
    else:
        # If we can't create the schedule, yield None and let tests handle it
        yield None


@pytest.fixture
def sample_ingredient_data():
    """Sample ingredient data for testing"""
    return {
        "name": "Sample Ingredient Legacy",
        "base_unit_of_measure": "kg",
        "status": "active",
        "description": "Sample ingredient for testing",
        "category": "sample_category",
        "nutritional_info": {
            "per_100g": {
                "calories": 250.0,
                "protein": 5.0,
                "carbohydrates": 50.0,
                "fat": 1.0,
                "fiber": 2.0,
                "sodium": 5.0
            }
        }
    }


@pytest.fixture
def sample_dish_data(test_ingredient):
    """Sample dish data with valid ingredient ID"""
    ingredient_id = test_ingredient.get("id") if test_ingredient else str(ObjectId())
    
    return {
        "name": "Sample Dish Legacy",
        "description": "Sample dish for testing",
        "status": "active",
        "compatible_meal_types": ["almuerzo"],  # Use Spanish values
        "recipe": {
            "ingredients": [
                {
                    "ingredient_id": ingredient_id,
                    "quantity": 150.0,
                    "unit": "g"
                }
            ]
        },
        "nutritional_info": {
            "calories": 300.0,
            "protein": 12.0,
            "carbohydrates": 40.0,
            "fat": 6.0,
            "fiber": 3.0,
            "sodium": 100.0
        },
        "dish_type": "cereal"
    }


@pytest.fixture
def sample_menu_cycle_data(test_dish):
    """Sample menu cycle data with valid dish ID"""
    dish_id = test_dish.get("id") if test_dish else str(ObjectId())
    
    return {
        "name": "Sample Menu Cycle Legacy",
        "description": "Sample menu cycle for testing",
        "status": "active",
        "duration_days": 5,
        "daily_menus": [
            {
                "day": 1,
                "breakfast_dish_ids": [],
                "lunch_dish_ids": [dish_id],
                "snack_dish_ids": []
            },
            {
                "day": 2,
                "breakfast_dish_ids": [],
                "lunch_dish_ids": [dish_id],
                "snack_dish_ids": []
            }
        ]
    }


@pytest.fixture
def sample_nutritional_analysis_data(test_menu_cycle):
    """Sample nutritional analysis data with valid menu cycle ID"""
    cycle_id = test_menu_cycle.get("id") if test_menu_cycle else str(ObjectId())
    
    return {
        "analysis_type": "menu_cycle",
        "target_id": cycle_id,
        "period_start": "2024-02-01",
        "period_end": "2024-02-07",
        "institution_id": 1,
        "analysis_parameters": {
            "age_group": "school_age",
            "target_population": 100,
            "dietary_restrictions": []
        }
    }


@pytest.fixture
def non_existent_ingredient_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


@pytest.fixture
def non_existent_dish_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


@pytest.fixture
def non_existent_menu_cycle_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


@pytest.fixture
def non_existent_menu_schedule_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return TestConfig


# Helper functions for assertions
def assert_response_has_id(data: Dict[str, Any]) -> str:
    """Assert that response has an ID field and return it"""
    assert "id" in data, "Response should contain an 'id' field"
    assert data["id"] is not None, "ID should not be None"
    assert isinstance(data["id"], str), "ID should be a string"
    return data["id"]


def assert_pagination_response(data: Dict[str, Any], expected_items_key: str = "items"):
    """Assert that response has pagination structure"""
    assert isinstance(data, list) or expected_items_key in data, f"Response should be a list or contain '{expected_items_key}'"
    if expected_items_key in data:
        assert isinstance(data[expected_items_key], list), f"'{expected_items_key}' should be a list"


def assert_error_response(data: Dict[str, Any], expected_message: Optional[str] = None):
    """Assert that response has error structure"""
    assert "detail" in data or "message" in data, "Error response should contain 'detail' or 'message'"
    if expected_message:
        error_text = str(data.get("detail", data.get("message", "")))
        assert expected_message.lower() in error_text.lower(), f"Expected '{expected_message}' in error message: {error_text}"


def assert_ingredient_response(data: Dict[str, Any], expected_data: Dict[str, Any]):
    """Assert that ingredient response matches expected data"""
    assert_response_has_id(data)
    assert data["name"] == expected_data["name"]
    assert data["base_unit_of_measure"] == expected_data["base_unit_of_measure"]
    assert data["status"] == expected_data.get("status", "active")
    if "description" in expected_data:
        assert data["description"] == expected_data["description"]
    if "category" in expected_data:
        assert data["category"] == expected_data["category"]
    assert "created_at" in data
    assert "updated_at" in data


def assert_dish_response(data: Dict[str, Any], expected_data: Dict[str, Any]):
    """Assert that dish response matches expected data"""
    assert_response_has_id(data)
    assert data["name"] == expected_data["name"]
    assert data["status"] == expected_data.get("status", "active")
    assert data["compatible_meal_types"] == expected_data["compatible_meal_types"]
    if "description" in expected_data:
        assert data["description"] == expected_data["description"]
    assert "recipe" in data
    assert "created_at" in data
    assert "updated_at" in data 