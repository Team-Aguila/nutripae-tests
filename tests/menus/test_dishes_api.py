"""
Integration tests for Dishes API
Test cases: DISH-001 to DISH-020
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response, assert_dish_response


class TestDishesAPI:
    """Test suite for Dishes API endpoints"""
    
    # CREATE DISH TESTS
    
    async def test_create_dish_success(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient, test_ingredient_2):
        """DISH-001: Successfully create a new dish with recipe"""
        ingredient_id_1 = test_ingredient.get("id")
        ingredient_id_2 = test_ingredient_2.get("id")
        
        dish_data = {
            "name": "Test Dish DISH-001",
            "description": "Test dish for DISH-001",
            "status": "active",
            "compatible_meal_types": ["almuerzo", "refrigerio"],  # Use Spanish values
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id_1,
                        "quantity": 250.0,
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
        
        response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_dish_response(data, dish_data)
        assert len(data["recipe"]["ingredients"]) == 2
        assert data["dish_type"] == "protein"
        
        # Cleanup
        dish_id = data["id"]
        await client.delete(f"{api_prefix}/dishes/{dish_id}")

    async def test_create_dish_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-002: Fail to create dish with missing required fields"""
        invalid_data = {
            "description": "Missing name, meal types and recipe",
            "status": "active"
        }
        
        response = await client.post(f"{api_prefix}/dishes/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about missing required fields
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("name" in str(error) for error in data["detail"])
        assert any("compatible_meal_types" in str(error) for error in data["detail"])
        assert any("recipe" in str(error) for error in data["detail"])

    async def test_create_dish_with_non_existent_ingredient(self, client: httpx.AsyncClient, api_prefix: str, non_existent_ingredient_id):
        """DISH-003: Fail to create dish with non-existent ingredient in recipe"""
        dish_data = {
            "name": "Non-existent Ingredient Test DISH-003",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": non_existent_ingredient_id,
                        "quantity": 100.0,
                        "unit": "g"
                    }
                ]
            }
        }
        
        response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "not found")

    async def test_create_dish_empty_recipe_ingredients(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-004: Fail to create dish with empty recipe ingredients"""
        dish_data = {
            "name": "Empty Recipe Test DISH-004",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": []
            }
        }
        
        response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data)
        # Should indicate that recipe must have at least one ingredient

    async def test_create_dish_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient):
        """DISH-005: Fail to create dish with duplicate name"""
        ingredient_id = test_ingredient.get("id")
        
        dish_data = {
            "name": "Duplicate Dish Test DISH-005",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 100.0,
                        "unit": "g"
                    }
                ]
            }
        }
        
        # First create a dish
        response1 = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        assert response1.status_code == 201
        dish1_id = assert_response_has_id(response1.json())
        
        # Try to create another with the same name
        response2 = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response2.status_code == 400
        data = response2.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/dishes/{dish1_id}")

    # READ DISH TESTS
    
    async def test_get_dish_by_id_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DISH-006: Successfully get dish by ID"""
        dish_id = test_dish.get("id")
        
        response = await client.get(f"{api_prefix}/dishes/{dish_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == dish_id
        assert data["name"] == test_dish["name"]
        assert "recipe" in data
        assert "ingredients" in data["recipe"]
        assert len(data["recipe"]["ingredients"]) > 0

    async def test_get_dish_by_id_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """DISH-007: Fail to get dish with non-existent ID"""
        response = await client.get(f"{api_prefix}/dishes/{non_existent_dish_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_get_dish_by_id_invalid_format(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-008: Fail to get dish with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = await client.get(f"{api_prefix}/dishes/{invalid_id}")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # LIST DISHES TESTS
    
    async def test_get_dishes_list_default(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-009: Successfully get dishes list with default parameters"""
        response = await client.get(f"{api_prefix}/dishes/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that each item has required fields
        for dish in data:
            assert "id" in dish
            assert "name" in dish
            assert "status" in dish
            assert "compatible_meal_types" in dish
            assert "recipe" in dish

    async def test_get_dishes_list_with_name_filter(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DISH-010: Successfully get dishes list filtered by name"""
        dish_name = test_dish["name"]
        search_term = dish_name.split()[0]  # Use first word of the dish name
        
        params = {"name": search_term}
        response = await client.get(f"{api_prefix}/dishes/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that our test dish is in the results
        found = any(dish["id"] == test_dish["id"] for dish in data)
        assert found

    async def test_get_dishes_list_with_status_filter(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-011: Successfully get dishes list filtered by status"""
        params = {"status": "active"}
        response = await client.get(f"{api_prefix}/dishes/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that all returned dishes have active status
        for dish in data:
            assert dish["status"] == "active"

    async def test_get_dishes_list_with_meal_type_filter(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DISH-012: Successfully get dishes list filtered by meal type"""
        meal_type = test_dish["compatible_meal_types"][0]
        
        params = {"meal_type": meal_type}
        response = await client.get(f"{api_prefix}/dishes/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that all returned dishes are compatible with the meal type
        for dish in data:
            assert meal_type in dish["compatible_meal_types"]

    # UPDATE DISH TESTS
    
    async def test_update_dish_name_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DISH-013: Successfully update dish name"""
        dish_id = test_dish.get("id")
        original_name = test_dish["name"]
        
        update_data = {"name": f"Updated {original_name}"}
        response = await client.put(f"{api_prefix}/dishes/{dish_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == f"Updated {original_name}"
        assert data["id"] == dish_id

    async def test_update_dish_recipe_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient):
        """DISH-014: Successfully update dish recipe"""
        dish_id = test_dish.get("id")
        ingredient_id = test_ingredient.get("id")
        
        update_data = {
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 300.0,
                        "unit": "g"
                    }
                ]
            }
        }
        response = await client.put(f"{api_prefix}/dishes/{dish_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipe"]["ingredients"]) == 1
        assert data["recipe"]["ingredients"][0]["quantity"] == 300.0

    async def test_update_dish_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """DISH-015: Fail to update non-existent dish"""
        update_data = {"name": "Updated Name"}
        response = await client.put(f"{api_prefix}/dishes/{non_existent_dish_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_update_dish_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient):
        """DISH-016: Fail to update dish with duplicate name"""
        ingredient_id = test_ingredient.get("id")
        
        # Create another dish
        dish_data = {
            "name": "Another Dish DISH-016",
            "compatible_meal_types": ["desayuno"],  # Spanish for breakfast
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 50.0,
                        "unit": "g"
                    }
                ]
            }
        }
        
        create_response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        assert create_response.status_code == 201
        another_dish_id = create_response.json()["id"]
        
        # Try to update it with the test dish's name
        update_data = {"name": test_dish["name"]}
        response = await client.put(f"{api_prefix}/dishes/{another_dish_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/dishes/{another_dish_id}")

    # DELETE DISH TESTS
    
    async def test_delete_dish_success(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient):
        """DISH-017: Successfully delete dish"""
        ingredient_id = test_ingredient.get("id")
        
        # Create a dish to delete
        dish_data = {
            "name": "Delete Test Dish DISH-017",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 100.0,
                        "unit": "g"
                    }
                ]
            }
        }
        
        create_response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        assert create_response.status_code == 201
        dish_id = create_response.json()["id"]
        
        # Delete the dish
        response = await client.delete(f"{api_prefix}/dishes/{dish_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        
        # Verify dish is deleted
        get_response = await client.get(f"{api_prefix}/dishes/{dish_id}")
        assert get_response.status_code == 404

    async def test_delete_dish_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """DISH-018: Fail to delete non-existent dish"""
        response = await client.delete(f"{api_prefix}/dishes/{non_existent_dish_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    # COMPLEX RECIPE TESTS
    
    async def test_create_dish_complex_recipe(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient, test_ingredient_2):
        """DISH-019: Successfully create dish with complex recipe containing multiple ingredients"""
        ingredient_id_1 = test_ingredient.get("id")
        ingredient_id_2 = test_ingredient_2.get("id")
        
        dish_data = {
            "name": "Complex Recipe Dish DISH-019",
            "description": "Dish with complex recipe for testing",
            "compatible_meal_types": ["almuerzo", "refrigerio"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id_1,
                        "quantity": 500.0,
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ingredient_id_2,
                        "quantity": 200.0,
                        "unit": "g"
                    }
                ]
            },
            "nutritional_info": {
                "calories": 425.0,
                "protein": 18.0,
                "carbohydrates": 52.0,
                "fat": 12.0,
                "fiber": 4.0,
                "sodium": 150.0,
                "photo_url": "https://example.com/complex-dish.jpg"
            },
            "dish_type": "protein"
        }
        
        response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_dish_response(data, dish_data)
        
        # Verify complex recipe structure
        assert len(data["recipe"]["ingredients"]) == 2
        
        # Verify ingredient details
        for recipe_ingredient in data["recipe"]["ingredients"]:
            assert "ingredient_id" in recipe_ingredient
            assert "quantity" in recipe_ingredient
            assert "unit" in recipe_ingredient
            assert recipe_ingredient["ingredient_id"] in [ingredient_id_1, ingredient_id_2]
        
        # Cleanup
        dish_id = data["id"]
        await client.delete(f"{api_prefix}/dishes/{dish_id}")

    async def test_update_dish_add_ingredient_to_recipe(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient_2):
        """DISH-020: Successfully update dish by adding ingredient to recipe"""
        dish_id = test_dish.get("id")
        ingredient_id_2 = test_ingredient_2.get("id")
        
        # Get current recipe
        get_response = await client.get(f"{api_prefix}/dishes/{dish_id}")
        assert get_response.status_code == 200
        current_dish = get_response.json()
        current_ingredients = current_dish["recipe"]["ingredients"]
        
        # Add new ingredient to recipe
        new_ingredients = current_ingredients + [
            {
                "ingredient_id": ingredient_id_2,
                "quantity": 75.0,
                "unit": "g"
            }
        ]
        
        update_data = {
            "recipe": {
                "ingredients": new_ingredients
            }
        }
        
        response = await client.put(f"{api_prefix}/dishes/{dish_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipe"]["ingredients"]) == len(current_ingredients) + 1
        
        # Verify the new ingredient was added
        ingredient_ids = [ing["ingredient_id"] for ing in data["recipe"]["ingredients"]]
        assert ingredient_id_2 in ingredient_ids 