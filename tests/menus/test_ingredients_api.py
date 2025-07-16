"""
Integration tests for Ingredients API
Test cases: ING-001 to ING-030
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response, assert_ingredient_response
from ..test_metadata import add_test_info


class TestIngredientsAPI:
    """Test suite for Ingredients API endpoints"""
    
    # CREATE INGREDIENT TESTS
    
    @add_test_info(
        description="Crear un ingrediente exitosamente",
        expected_result="Status Code: 201, datos del ingrediente creado",
        module="Menús",
        test_id="ING-001"
    )
    async def test_create_ingredient_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-001: Successfully create a new ingredient"""
        ingredient_data = {
            "name": "Test Ingredient ING-001",
            "base_unit_of_measure": "kg",
            "status": "active",
            "description": "Test ingredient for ING-001",
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
        
        response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_ingredient_response(data, ingredient_data)
        
        # Cleanup
        ingredient_id = data.get("_id")
        if ingredient_id:
            await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Fallar al crear ingrediente con campos requeridos faltantes",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="ING-002"
    )
    async def test_create_ingredient_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-002: Fail to create ingredient with missing required fields"""
        invalid_data = {
            "description": "Missing name and unit",
            "category": "test"
        }
        
        response = await client.post(f"{api_prefix}/ingredients/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about missing required fields
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("name" in str(error) for error in data["detail"])
        assert any("base_unit_of_measure" in str(error) for error in data["detail"])

    @add_test_info(
        description="Fallar al crear ingrediente con estado inválido",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="ING-003"
    )
    async def test_create_ingredient_invalid_status(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-003: Fail to create ingredient with invalid status"""
        invalid_data = {
            "name": "Invalid Status Test",
            "base_unit_of_measure": "kg",
            "status": "invalid_status"
        }
        
        response = await client.post(f"{api_prefix}/ingredients/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about invalid status
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("status" in str(error) for error in data["detail"])

    @add_test_info(
        description="Fallar al crear ingrediente con nombre duplicado",
        expected_result="Status Code: 400, error de conflicto",
        module="Menús",
        test_id="ING-004"
    )
    async def test_create_ingredient_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-004: Fail to create ingredient with duplicate name"""
        ingredient_data = {
            "name": "Duplicate Test Ingredient",
            "base_unit_of_measure": "kg",
            "status": "active"
        }
        
        # First create an ingredient
        response1 = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert response1.status_code == 201
        ingredient1_id = assert_response_has_id(response1.json())
        
        # Try to create another with the same name
        response2 = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        
        assert response2.status_code == 400
        data = response2.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient1_id}")

    @add_test_info(
        description="Fallar al crear ingrediente con nombre vacío",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="ING-005"
    )
    async def test_create_ingredient_empty_name(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-005: Fail to create ingredient with empty name"""
        invalid_data = {
            "name": "",
            "base_unit_of_measure": "kg",
            "status": "active"
        }
        
        response = await client.post(f"{api_prefix}/ingredients/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("name" in str(error) for error in data["detail"])

    # READ INGREDIENT TESTS
    
    @add_test_info(
        description="Obtener ingrediente por ID exitosamente",
        expected_result="Status Code: 200, datos completos del ingrediente",
        module="Menús",
        test_id="ING-006"
    )
    async def test_get_ingredient_by_id_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-006: Successfully get ingredient by ID"""
        # First create an ingredient
        ingredient_data = {
            "name": "Get Test Ingredient ING-006",
            "base_unit_of_measure": "g",
            "status": "active",
            "description": "Ingredient for get test"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        created_ingredient = create_response.json()
        ingredient_id = created_ingredient["_id"]
        
        # Get the ingredient
        response = await client.get(f"{api_prefix}/ingredients/{ingredient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert_ingredient_response(data, ingredient_data)
        assert data["_id"] == ingredient_id
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Fallar al obtener ingrediente que no existe",
        expected_result="Status Code: 404, ingrediente no encontrado",
        module="Menús",
        test_id="ING-007"
    )
    async def test_get_ingredient_by_id_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_ingredient_id):
        """ING-007: Fail to get ingredient that doesn't exist"""
        response = await client.get(f"{api_prefix}/ingredients/{non_existent_ingredient_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al obtener ingrediente con ID en formato inválido",
        expected_result="Status Code: 422, error de validación",
        module="Menús",
        test_id="ING-008"
    )
    async def test_get_ingredient_by_id_invalid_format(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-008: Fail to get ingredient with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = await client.get(f"{api_prefix}/ingredients/{invalid_id}")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # LIST INGREDIENTS TESTS
    
    @add_test_info(
        description="Obtener lista de ingredientes con paginación por defecto",
        expected_result="Status Code: 200, lista paginada de ingredientes",
        module="Menús",
        test_id="ING-009"
    )
    async def test_get_ingredients_list_default_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-009: Successfully get ingredients list with default pagination"""
        response = await client.get(f"{api_prefix}/ingredients/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that each item has required fields
        for ingredient in data:
            assert "_id" in ingredient
            assert "name" in ingredient
            assert "base_unit_of_measure" in ingredient
            assert "status" in ingredient

    @add_test_info(
        description="Obtener lista de ingredientes con paginación personalizada",
        expected_result="Status Code: 200, lista con paginación personalizada",
        module="Menús",
        test_id="ING-010"
    )
    async def test_get_ingredients_list_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-010: Successfully get ingredients list with pagination"""
        params = {"skip": 0, "limit": 5}
        response = await client.get(f"{api_prefix}/ingredients/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @add_test_info(
        description="Obtener lista de ingredientes filtrada por estado",
        expected_result="Status Code: 200, lista filtrada por estado",
        module="Menús",
        test_id="ING-011"
    )
    async def test_get_ingredients_list_with_status_filter(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-011: Successfully get ingredients list filtered by status"""
        params = {"status": "active"}
        response = await client.get(f"{api_prefix}/ingredients/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that all returned ingredients have active status
        for ingredient in data:
            assert ingredient["status"] == "active"

    @add_test_info(
        description="Obtener lista de ingredientes filtrada por categoría",
        expected_result="Status Code: 200, lista filtrada por categoría",
        module="Menús",
        test_id="ING-012"
    )
    async def test_get_ingredients_list_with_category_filter(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-012: Successfully get ingredients list filtered by category"""
        # First create an ingredient with specific category
        ingredient_data = {
            "name": "Category Filter Test ING-012",
            "base_unit_of_measure": "kg",
            "category": "test_filter_category"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json().get("_id")
        
        # Test the filter
        params = {"category": "test_filter_category"}
        response = await client.get(f"{api_prefix}/ingredients/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that at least our created ingredient is returned
        found = any(ing["_id"] == ingredient_id for ing in data)
        assert found
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Obtener lista de ingredientes con búsqueda por nombre",
        expected_result="Status Code: 200, lista filtrada por búsqueda",
        module="Menús",
        test_id="ING-013"
    )
    async def test_get_ingredients_list_with_search(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-013: Successfully get ingredients list with search filter"""
        # First create an ingredient with specific name
        ingredient_data = {
            "name": "Unique Search Test Ingredient ING-013",
            "base_unit_of_measure": "kg"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json().get("_id")
        
        # Test the search
        params = {"search": "Unique Search Test"}
        response = await client.get(f"{api_prefix}/ingredients/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that our created ingredient is returned
        found = any(ing["_id"] == ingredient_id for ing in data)
        assert found
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Obtener lista de ingredientes activos excluyendo inactivos",
        expected_result="Status Code: 200, solo ingredientes activos",
        module="Menús",
        test_id="ING-014"
    )
    async def test_get_active_ingredients_excludes_inactive(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-014: Successfully get active ingredients excluding inactive ones"""
        # Create an active ingredient
        active_data = {
            "name": "Active Ingredient ING-014",
            "base_unit_of_measure": "kg",
            "status": "active"
        }
        
        active_response = await client.post(f"{api_prefix}/ingredients/", json=active_data)
        assert active_response.status_code == 201
        active_id = active_response.json().get("_id")
        
        # Create an inactive ingredient
        inactive_data = {
            "name": "Inactive Ingredient ING-014",
            "base_unit_of_measure": "kg",
            "status": "inactive"
        }
        
        inactive_response = await client.post(f"{api_prefix}/ingredients/", json=inactive_data)
        assert inactive_response.status_code == 201
        inactive_id = inactive_response.json().get("_id")
        
        # Get active ingredients
        response = await client.get(f"{api_prefix}/ingredients/active")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that active ingredient is included and inactive is excluded
        active_found = any(ing["_id"] == active_id for ing in data)
        inactive_found = any(ing["_id"] == inactive_id for ing in data)
        
        assert active_found
        assert not inactive_found
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{active_id}")
        await client.delete(f"{api_prefix}/ingredients/{inactive_id}")

    # UPDATE INGREDIENT TESTS
    
    @add_test_info(
        description="Actualizar nombre de ingrediente exitosamente",
        expected_result="Status Code: 200, datos del ingrediente actualizado",
        module="Menús",
        test_id="ING-015"
    )
    async def test_update_ingredient_name_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-015: Successfully update ingredient name"""
        # Create ingredient
        ingredient_data = {
            "name": "Original Name ING-015",
            "base_unit_of_measure": "kg"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Update name
        update_data = {"name": "Updated Name ING-015"}
        response = await client.put(f"{api_prefix}/ingredients/{ingredient_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name ING-015"
        assert data["base_unit_of_measure"] == "kg"  # Should remain unchanged
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Actualizar múltiples campos de ingrediente exitosamente",
        expected_result="Status Code: 200, ingrediente con múltiples campos actualizados",
        module="Menús",
        test_id="ING-016"
    )
    async def test_update_ingredient_multiple_fields_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-016: Successfully update multiple ingredient fields"""
        # Create ingredient
        ingredient_data = {
            "name": "Multi Update Test ING-016",
            "base_unit_of_measure": "kg",
            "description": "Original description",
            "category": "original_category"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Update multiple fields
        update_data = {
            "description": "Updated description",
            "category": "updated_category",
            "status": "inactive"
        }
        response = await client.put(f"{api_prefix}/ingredients/{ingredient_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["category"] == "updated_category"
        assert data["status"] == "inactive"
        assert data["name"] == "Multi Update Test ING-016"  # Should remain unchanged
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Fallar al actualizar ingrediente que no existe",
        expected_result="Status Code: 404, ingrediente no encontrado",
        module="Menús",
        test_id="ING-017"
    )
    async def test_update_ingredient_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_ingredient_id):
        """ING-017: Fail to update ingredient that doesn't exist"""
        update_data = {"name": "Updated Name"}
        response = await client.put(f"{api_prefix}/ingredients/{non_existent_ingredient_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al actualizar ingrediente con nombre duplicado",
        expected_result="Status Code: 400, error de conflicto",
        module="Menús",
        test_id="ING-018"
    )
    async def test_update_ingredient_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-018: Fail to update ingredient with duplicate name"""
        # Create first ingredient
        ingredient1_data = {
            "name": "First Ingredient ING-018",
            "base_unit_of_measure": "kg"
        }
        
        response1 = await client.post(f"{api_prefix}/ingredients/", json=ingredient1_data)
        assert response1.status_code == 201
        ingredient1_id = response1.json()["id"]
        
        # Create second ingredient
        ingredient2_data = {
            "name": "Second Ingredient ING-018",
            "base_unit_of_measure": "g"
        }
        
        response2 = await client.post(f"{api_prefix}/ingredients/", json=ingredient2_data)
        assert response2.status_code == 201
        ingredient2_id = response2.json()["id"]
        
        # Try to update second ingredient with first ingredient's name
        update_data = {"name": "First Ingredient ING-018"}
        response = await client.put(f"{api_prefix}/ingredients/{ingredient2_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient1_id}")
        await client.delete(f"{api_prefix}/ingredients/{ingredient2_id}")

    # SOFT DELETE TESTS
    
    @add_test_info(
        description="Inactivar ingrediente exitosamente",
        expected_result="Status Code: 200, ingrediente inactivado",
        module="Menús",
        test_id="ING-019"
    )
    async def test_inactivate_ingredient_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-019: Successfully inactivate ingredient"""
        # Create ingredient
        ingredient_data = {
            "name": "Inactivate Test ING-019",
            "base_unit_of_measure": "kg",
            "status": "active"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Inactivate ingredient
        response = await client.patch(f"{api_prefix}/ingredients/{ingredient_id}/inactivate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
        assert data["id"] == ingredient_id
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Activar ingrediente exitosamente",
        expected_result="Status Code: 200, ingrediente activado",
        module="Menús",
        test_id="ING-020"
    )
    async def test_activate_ingredient_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-020: Successfully activate ingredient"""
        # Create inactive ingredient
        ingredient_data = {
            "name": "Activate Test ING-020",
            "base_unit_of_measure": "kg",
            "status": "inactive"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Activate ingredient
        response = await client.patch(f"{api_prefix}/ingredients/{ingredient_id}/activate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["id"] == ingredient_id
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    # DELETE INGREDIENT TESTS
    
    @add_test_info(
        description="Eliminar ingrediente exitosamente",
        expected_result="Status Code: 200, confirmación de eliminación",
        module="Menús",
        test_id="ING-021"
    )
    async def test_delete_ingredient_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-021: Successfully delete ingredient"""
        # Create ingredient
        ingredient_data = {
            "name": "Delete Test ING-021",
            "base_unit_of_measure": "kg"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Delete ingredient
        response = await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        
        # Verify ingredient is deleted
        get_response = await client.get(f"{api_prefix}/ingredients/{ingredient_id}")
        assert get_response.status_code == 404

    @add_test_info(
        description="Fallar al eliminar ingrediente que no existe",
        expected_result="Status Code: 404, ingrediente no encontrado",
        module="Menús",
        test_id="ING-022"
    )
    async def test_delete_ingredient_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_ingredient_id):
        """ING-022: Fail to delete ingredient that doesn't exist"""
        response = await client.delete(f"{api_prefix}/ingredients/{non_existent_ingredient_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    # UTILITY ENDPOINTS TESTS
    
    @add_test_info(
        description="Obtener categorías de ingredientes exitosamente",
        expected_result="Status Code: 200, lista de categorías",
        module="Menús",
        test_id="ING-023"
    )
    async def test_get_ingredient_categories_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-023: Successfully get ingredient categories"""
        response = await client.get(f"{api_prefix}/ingredients/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All items should be strings
        for category in data:
            assert isinstance(category, str)

    @add_test_info(
        description="Obtener estadísticas de ingredientes exitosamente",
        expected_result="Status Code: 200, estadísticas de ingredientes",
        module="Menús",
        test_id="ING-024"
    )
    async def test_get_ingredient_statistics_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-024: Successfully get ingredient statistics"""
        response = await client.get(f"{api_prefix}/ingredients/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain statistical information
        assert "total_ingredients" in data
        assert "active_ingredients" in data
        assert "inactive_ingredients" in data
        assert isinstance(data["total_ingredients"], int)
        assert isinstance(data["active_ingredients"], int)
        assert isinstance(data["inactive_ingredients"], int)

    @add_test_info(
        description="Verificar disponibilidad de nombre de ingrediente",
        expected_result="Status Code: 200, nombre disponible",
        module="Menús",
        test_id="ING-025"
    )
    async def test_check_name_uniqueness_available(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-025: Successfully check name uniqueness - available"""
        params = {"name": "Unique Name Check ING-025"}
        response = await client.head(f"{api_prefix}/ingredients/validate/name-uniqueness", params=params)
        
        assert response.status_code == 200

    @add_test_info(
        description="Verificar que nombre de ingrediente está ocupado",
        expected_result="Status Code: 200, nombre no disponible",
        module="Menús",
        test_id="ING-026"
    )
    async def test_check_name_uniqueness_taken(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-026: Successfully check name uniqueness - taken"""
        # Create ingredient
        ingredient_data = {
            "name": "Taken Name Check ING-026",
            "base_unit_of_measure": "kg"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Check if name is taken
        params = {"name": "Taken Name Check ING-026"}
        response = await client.head(f"{api_prefix}/ingredients/validate/name-uniqueness", params=params)
        
        assert response.status_code == 409
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Obtener ingrediente detallado exitosamente",
        expected_result="Status Code: 200, información detallada del ingrediente",
        module="Menús",
        test_id="ING-027"
    )
    async def test_get_detailed_ingredient_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-027: Successfully get detailed ingredient information"""
        # Create ingredient
        ingredient_data = {
            "name": "Detailed Test ING-027",
            "base_unit_of_measure": "kg",
            "description": "Detailed test ingredient"
        }
        
        create_response = await client.post(f"{api_prefix}/ingredients/", json=ingredient_data)
        assert create_response.status_code == 201
        ingredient_id = create_response.json()["id"]
        
        # Get detailed ingredient
        response = await client.get(f"{api_prefix}/ingredients/{ingredient_id}/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ingredient_id
        assert data["name"] == "Detailed Test ING-027"
        # Should contain additional fields for detailed view
        assert "menu_usage" in data or "usage_count" in data
        
        # Cleanup
        await client.delete(f"{api_prefix}/ingredients/{ingredient_id}")

    @add_test_info(
        description="Obtener lista detallada de ingredientes exitosamente",
        expected_result="Status Code: 200, lista detallada de ingredientes",
        module="Menús",
        test_id="ING-028"
    )
    async def test_get_detailed_ingredients_list_success(self, client: httpx.AsyncClient, api_prefix: str):
        """ING-028: Successfully get detailed ingredients list"""
        response = await client.get(f"{api_prefix}/ingredients/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check detailed response structure for each ingredient
        for ingredient in data:
            assert "id" in ingredient
            assert "name" in ingredient
            assert "base_unit_of_measure" in ingredient
            # Should contain additional fields for detailed view
            assert "menu_usage" in ingredient or "usage_count" in ingredient 