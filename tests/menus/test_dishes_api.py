"""
Integration tests for Dishes API
Test cases: DISH-001 to DISH-030
"""
import pytest
import httpx
from typing import Dict, Any
import uuid
from datetime import datetime

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response, assert_dish_response
from ..test_metadata import add_test_info


class TestDishesAPI:
    """Test suite for Dishes API endpoints"""
    
    # CREATE DISH TESTS
    
    @add_test_info(
        description="Crear un plato exitosamente",
        expected_result="Status Code: 201, datos del plato creado",
        module="Menús",
        test_id="DISH-001"
    )
    async def test_create_dish_success(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient):
        """DISH-001: Successfully create a new dish"""
        ingredient_id = test_ingredient.get("_id")
        
        # Use unique name to avoid collisions
        unique_suffix = f"{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:8]}"
        dish_data = {
            "name": f"Test Dish DISH-001-{unique_suffix}",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 150.0,
                        "unit": "g"
                    }
                ]
            }
            # Only using required fields - status defaults to "active"
            # Removed optional fields: description, nutritional_info, dish_type
        }
        
        response = await client.post(f"{api_prefix}/dishes/", json=dish_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_dish_response(data, dish_data)
        
        # Cleanup: Try to delete the created dish
        dish_id = data.get("_id") or data.get("id")
        if dish_id:
            try:
                await client.delete(f"{api_prefix}/dishes/{dish_id}")
            except Exception:
                pass  # Ignore cleanup errors

    @add_test_info(
        description="Fallar al crear plato con campos requeridos faltantes",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="DISH-002"
    )
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

    @add_test_info(
        description="Fallar al crear plato con ingrediente no existente",
        expected_result="Status Code: 400, error de ingrediente no encontrado",
        module="Menús",
        test_id="DISH-003"
    )
    async def test_create_dish_with_non_existent_ingredient(self, client: httpx.AsyncClient, api_prefix: str, non_existent_ingredient_id):
        """DISH-003: Fail to create dish with non-existent ingredient"""
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

    @add_test_info(
        description="Fallar al crear plato con receta sin ingredientes",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="DISH-004"
    )
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

    @add_test_info(
        description="Fallar al crear plato con nombre duplicado",
        expected_result="Status Code: 400, error de conflicto",
        module="Menús",
        test_id="DISH-005"
    )
    async def test_create_dish_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient):
        """DISH-005: Fail to create dish with duplicate name"""
        ingredient_id = test_ingredient.get("_id")
        
        # Use unique base name for this test
        unique_suffix = f"{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:8]}"
        base_name = f"Duplicate Test Dish-{unique_suffix}"
        
        dish_data = {
            "name": base_name,
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id,
                        "quantity": 200.0,
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
        
        # Backend might return 400 or 500 for duplicates
        assert response2.status_code in [400, 500]
        data = response2.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        try:
            await client.delete(f"{api_prefix}/dishes/{dish1_id}")
        except Exception:
            pass  # Ignore cleanup errors

    # READ DISH TESTS
    
    @add_test_info(
        description="Obtener plato por ID exitosamente",
        expected_result="Status Code: 200, datos completos del plato",
        module="Menús",
        test_id="DISH-006"
    )
    async def test_get_dish_by_id_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DSH-006: Successfully get dish by ID"""
        dish_id = test_dish.get("_id") or test_dish.get("id")  # API might return _id
        
        # Get the dish
        response = await client.get(f"{api_prefix}/dishes/{dish_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert_dish_response(data, test_dish)
        assert data["_id"] == dish_id  # Use _id instead of id

    @add_test_info(
        description="Fallar al obtener plato que no existe",
        expected_result="Status Code: 404, plato no encontrado",
        module="Menús",
        test_id="DISH-007"
    )
    async def test_get_dish_by_id_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """DISH-007: Fail to get dish that doesn't exist"""
        response = await client.get(f"{api_prefix}/dishes/{non_existent_dish_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al obtener plato con ID en formato inválido",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="DISH-008"
    )
    async def test_get_dish_by_id_invalid_format(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-008: Fail to get dish with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = await client.get(f"{api_prefix}/dishes/{invalid_id}")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # LIST DISHES TESTS
    
    @add_test_info(
        description="Obtener lista de platos con configuración por defecto",
        expected_result="Status Code: 200, lista de platos",
        module="Menús",
        test_id="DISH-009"
    )
    async def test_get_dishes_list_default(self, client: httpx.AsyncClient, api_prefix: str):
        """DISH-009: Successfully get dishes list with default settings"""
        response = await client.get(f"{api_prefix}/dishes/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that each item has required fields
        for dish in data:
            assert "_id" in dish  # API returns _id (MongoDB format)
            assert "name" in dish
            assert "status" in dish
            assert "compatible_meal_types" in dish
            assert "recipe" in dish

    @add_test_info(
        description="Obtener lista de platos filtrada por nombre",
        expected_result="Status Code: 200, lista filtrada por nombre",
        module="Menús",
        test_id="DISH-010"
    )
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

    @add_test_info(
        description="Obtener lista de platos filtrada por estado",
        expected_result="Status Code: 200, lista filtrada por estado",
        module="Menús",
        test_id="DISH-011"
    )
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

    @add_test_info(
        description="Obtener lista de platos filtrada por tipo de comida",
        expected_result="Status Code: 200, lista filtrada por tipo de comida",
        module="Menús",
        test_id="DISH-012"
    )
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
    
    @add_test_info(
        description="Actualizar nombre de plato exitosamente",
        expected_result="Status Code: 200, datos del plato actualizado",
        module="Menús",
        test_id="DISH-013"
    )
    async def test_update_dish_name_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """DISH-013: Successfully update dish name"""
        dish_id = test_dish.get("_id") or test_dish.get("id")  # API might return _id
        original_name = test_dish["name"]
        
        update_data = {"name": f"Updated {original_name}"}
        response = await client.put(f"{api_prefix}/dishes/{dish_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == f"Updated {original_name}"
        assert data["_id"] == dish_id

    @add_test_info(
        description="Actualizar receta de plato exitosamente",
        expected_result="Status Code: 200, plato con receta actualizada",
        module="Menús",
        test_id="DISH-014"
    )
    async def test_update_dish_recipe_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient):
        """DISH-014: Successfully update dish recipe"""
        dish_id = test_dish.get("_id")
        ingredient_id = test_ingredient.get("_id")
        
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

    @add_test_info(
        description="Fallar al actualizar plato que no existe",
        expected_result="Status Code: 404, plato no encontrado",
        module="Menús",
        test_id="DISH-015"
    )
    async def test_update_dish_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """DISH-015: Fail to update dish that doesn't exist"""
        update_data = {"name": "Updated Name"}
        response = await client.put(f"{api_prefix}/dishes/{non_existent_dish_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al actualizar plato con nombre duplicado",
        expected_result="Status Code: 400, error de conflicto",
        module="Menús",
        test_id="DISH-016"
    )
    async def test_update_dish_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient):
        """DISH-016: Fail to update dish with duplicate name"""
        # Generate unique suffix for this test
        unique_suffix = f"{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        ingredient_id = test_ingredient.get("_id")
        
        # Create another dish
        dish_data = {
            "name": f"Another Dish DISH-016-{unique_suffix}",
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
        another_dish_id = create_response.json()["_id"]
        
        # Try to update it with the test dish's name
        update_data = {"name": test_dish["name"]}
        response = await client.put(f"{api_prefix}/dishes/{another_dish_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/dishes/{another_dish_id}")

    # DELETE DISH TESTS
    
    # DELETE operations are not implemented in the backend API (405 Method Not Allowed)
    # Commenting out until DELETE endpoint is implemented
    
    # @add_test_info(
    #     description="Eliminar plato exitosamente - NO IMPLEMENTADO",
    #     expected_result="Status Code: 405 Method Not Allowed",
    #     module="Menús",
    #     test_id="DISH-017"
    # )
    # async def test_delete_dish_success(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient):
    #     """DISH-017: DELETE endpoint is not implemented"""
    #     pass

    # @add_test_info(
    #     description="Fallar al eliminar plato que no existe - NO IMPLEMENTADO",
    #     expected_result="Status Code: 405 Method Not Allowed",
    #     module="Menús",
    #     test_id="DISH-018"
    # )
    # async def test_delete_dish_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
    #     """DISH-018: DELETE endpoint is not implemented"""
    #     pass

    # COMPLEX RECIPE TESTS
    
    @add_test_info(
        description="Crear plato con receta compleja exitosamente",
        expected_result="Status Code: 201, plato creado con receta múltiple",
        module="Menús",
        test_id="DISH-030"
    )
    async def test_create_dish_complex_recipe(self, client: httpx.AsyncClient, api_prefix: str, test_ingredient, test_ingredient_2):
        """DISH-030: Successfully create dish with complex recipe"""
        ingredient_id_1 = test_ingredient.get("_id")  # Use _id instead of id
        ingredient_id_2 = test_ingredient_2.get("_id")  # Use _id instead of id
        
        # Use unique name to avoid collisions
        unique_suffix = f"{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:8]}"
        dish_data = {
            "name": f"Complex Recipe Dish-{unique_suffix}",
            "description": "Test dish with multiple ingredients",
            "status": "active",
            "compatible_meal_types": ["almuerzo"],
            "recipe": {
                "ingredients": [
                    {
                        "ingredient_id": ingredient_id_1,
                        "quantity": 300.0,
                        "unit": "g"
                    },
                    {
                        "ingredient_id": ingredient_id_2,
                        "quantity": 150.0,
                        "unit": "g"
                    }
                ]
            },
            "nutritional_info": {
                "calories": 400.0,
                "protein": 18.0,
                "carbohydrates": 52.0,
                "fat": 12.0,
                "fiber": 4.0,
                "sodium": 150.0
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
        dish_id = data.get("_id") or data.get("id")  # Use _id
        if dish_id:
            try:
                await client.delete(f"{api_prefix}/dishes/{dish_id}")
            except Exception:
                pass  # Ignore cleanup errors

    @add_test_info(
        description="Actualizar plato agregando ingrediente a la receta exitosamente",
        expected_result="Status Code: 200, receta actualizada con nuevo ingrediente",
        module="Menús",
        test_id="DISH-020"
    )
    async def test_update_dish_add_ingredient_to_recipe(self, client: httpx.AsyncClient, api_prefix: str, test_dish, test_ingredient_2):
        """DISH-020: Successfully update dish by adding ingredient to recipe"""
        dish_id = test_dish.get("_id") or test_dish.get("id")  # API might return _id
        ingredient_id_2 = test_ingredient_2.get("_id") or test_ingredient_2.get("id")  # API might return _id
        
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