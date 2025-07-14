"""
Integration tests for Menu Cycles API
Test cases: CYCLE-001 to CYCLE-015
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response


class TestMenuCyclesAPI:
    """Test suite for Menu Cycles API endpoints"""
    
    # CREATE MENU CYCLE TESTS
    
    async def test_create_menu_cycle_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """CYCLE-001: Successfully create a new menu cycle"""
        dish_id = test_dish.get("id")
        
        cycle_data = {
            "name": "Test Menu Cycle CYCLE-001",
            "description": "Test menu cycle for CYCLE-001",
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
                },
                {
                    "day": 3,
                    "breakfast_dish_ids": [],
                    "lunch_dish_ids": [dish_id],
                    "snack_dish_ids": []
                }
            ]
        }
        
        response = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_response_has_id(data)
        assert data["name"] == cycle_data["name"]
        assert data["description"] == cycle_data["description"]
        assert data["status"] == cycle_data["status"]
        assert data["duration_days"] == cycle_data["duration_days"]
        assert len(data["daily_menus"]) == 3
        assert data["daily_menus"][0]["day"] == 1
        assert len(data["daily_menus"][0]["lunch_dish_ids"]) == 1
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup
        cycle_id = data["id"]
        await client.delete(f"{api_prefix}/menu-cycles/{cycle_id}")

    async def test_create_menu_cycle_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-002: Fail to create menu cycle with missing required fields"""
        invalid_data = {
            "description": "Missing name, duration_days, and daily_menus",
            "status": "active"
        }
        
        response = await client.post(f"{api_prefix}/menu-cycles/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about missing required fields
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("name" in str(error) for error in data["detail"])
        assert any("duration_days" in str(error) for error in data["detail"])
        assert any("daily_menus" in str(error) for error in data["detail"])

    async def test_create_menu_cycle_invalid_duration(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-003: Fail to create menu cycle with invalid duration (0 or negative)"""
        invalid_data = {
            "name": "Invalid Duration CYCLE-003",
            "duration_days": 0,  # Invalid duration
            "daily_menus": []
        }
        
        response = await client.post(f"{api_prefix}/menu-cycles/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_create_menu_cycle_with_non_existent_dish(self, client: httpx.AsyncClient, api_prefix: str, non_existent_dish_id):
        """CYCLE-004: Fail to create menu cycle with non-existent dish"""
        cycle_data = {
            "name": "Non-existent Dish Test CYCLE-004",
            "duration_days": 3,
            "daily_menus": [
                {
                    "day": 1,
                    "breakfast_dish_ids": [],
                    "lunch_dish_ids": [non_existent_dish_id],
                    "snack_dish_ids": []
                }
            ]
        }
        
        response = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "not found")

    async def test_create_menu_cycle_duplicate_name(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """CYCLE-005: Fail to create menu cycle with duplicate name"""
        dish_id = test_dish.get("id")
        
        cycle_data = {
            "name": "Duplicate Cycle Test CYCLE-005",
            "duration_days": 3,
            "daily_menus": [
                {
                    "day": 1,
                    "breakfast_dish_ids": [],
                    "lunch_dish_ids": [dish_id],
                    "snack_dish_ids": []
                }
            ]
        }
        
        # First create a menu cycle
        response1 = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
        assert response1.status_code == 201
        cycle1_id = assert_response_has_id(response1.json())
        
        # Try to create another with the same name
        response2 = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
        
        assert response2.status_code == 400
        data = response2.json()
        assert_error_response(data, "already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/menu-cycles/{cycle1_id}")

    # READ MENU CYCLE TESTS
    
    async def test_get_menu_cycle_by_id_success(self, client: httpx.AsyncClient, api_prefix: str, test_menu_cycle):
        """CYCLE-006: Successfully get menu cycle by ID"""
        if not test_menu_cycle:
            pytest.skip("Test menu cycle not available")
        
        cycle_id = test_menu_cycle.get("id")
        
        response = await client.get(f"{api_prefix}/menu-cycles/{cycle_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cycle_id
        assert data["name"] == test_menu_cycle["name"]
        assert "daily_menus" in data
        assert isinstance(data["daily_menus"], list)
        assert "duration_days" in data

    async def test_get_menu_cycle_by_id_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_menu_cycle_id):
        """CYCLE-007: Fail to get menu cycle with non-existent ID"""
        response = await client.get(f"{api_prefix}/menu-cycles/{non_existent_menu_cycle_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_get_menu_cycle_by_id_invalid_format(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-008: Fail to get menu cycle with invalid ID format"""
        invalid_id = "invalid-id-format"
        response = await client.get(f"{api_prefix}/menu-cycles/{invalid_id}")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # LIST MENU CYCLES TESTS
    
    async def test_get_menu_cycles_list_default(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-009: Successfully get menu cycles list with default parameters"""
        response = await client.get(f"{api_prefix}/menu-cycles/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that each item has required fields
        for cycle in data:
            assert "id" in cycle
            assert "name" in cycle
            assert "status" in cycle
            assert "duration_days" in cycle
            assert "daily_menus" in cycle

    async def test_get_menu_cycles_list_with_status_filter(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-010: Successfully get menu cycles list filtered by status"""
        params = {"status": "active"}
        response = await client.get(f"{api_prefix}/menu-cycles/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that all returned cycles have active status
        for cycle in data:
            assert cycle["status"] == "active"

    async def test_get_menu_cycles_list_with_search(self, client: httpx.AsyncClient, api_prefix: str):
        """CYCLE-011: Successfully get menu cycles list with search term"""
        params = {"search": "Test"}
        response = await client.get(f"{api_prefix}/menu-cycles/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned cycles should contain the search term in their name
        for cycle in data:
            assert "test" in cycle["name"].lower()

    # UPDATE MENU CYCLE TESTS
    
    async def test_update_menu_cycle_name_success(self, client: httpx.AsyncClient, api_prefix: str, test_menu_cycle):
        """CYCLE-012: Successfully update menu cycle name"""
        if not test_menu_cycle:
            pytest.skip("Test menu cycle not available")
        
        cycle_id = test_menu_cycle.get("id")
        original_name = test_menu_cycle["name"]
        
        update_data = {"name": f"Updated {original_name}"}
        response = await client.patch(f"{api_prefix}/menu-cycles/{cycle_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == f"Updated {original_name}"
        assert data["id"] == cycle_id

    async def test_update_menu_cycle_add_daily_menu(self, client: httpx.AsyncClient, api_prefix: str, test_menu_cycle, test_dish):
        """CYCLE-013: Successfully update menu cycle by adding a daily menu"""
        if not test_menu_cycle:
            pytest.skip("Test menu cycle not available")
        
        cycle_id = test_menu_cycle.get("id")
        dish_id = test_dish.get("id")
        
        # Get current cycle
        get_response = await client.get(f"{api_prefix}/menu-cycles/{cycle_id}")
        assert get_response.status_code == 200
        current_cycle = get_response.json()
        
        # Add new daily menu
        new_daily_menus = current_cycle["daily_menus"] + [
            {
                "day": len(current_cycle["daily_menus"]) + 1,
                "breakfast_dish_ids": [dish_id],
                "lunch_dish_ids": [],
                "snack_dish_ids": []
            }
        ]
        
        update_data = {
            "daily_menus": new_daily_menus,
            "duration_days": len(new_daily_menus)
        }
        response = await client.patch(f"{api_prefix}/menu-cycles/{cycle_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["daily_menus"]) == len(current_cycle["daily_menus"]) + 1
        assert data["duration_days"] == len(new_daily_menus)

    async def test_update_menu_cycle_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_menu_cycle_id):
        """CYCLE-014: Fail to update non-existent menu cycle"""
        update_data = {"name": "Updated Name"}
        response = await client.patch(f"{api_prefix}/menu-cycles/{non_existent_menu_cycle_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    # DELETE MENU CYCLE TESTS
    
    async def test_delete_menu_cycle_success(self, client: httpx.AsyncClient, api_prefix: str, test_dish):
        """CYCLE-015: Successfully delete menu cycle"""
        dish_id = test_dish.get("id")
        
        # Create a menu cycle to delete
        cycle_data = {
            "name": "Delete Test Cycle CYCLE-015",
            "duration_days": 2,
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
        
        create_response = await client.post(f"{api_prefix}/menu-cycles/", json=cycle_data)
        assert create_response.status_code == 201
        cycle_id = create_response.json()["id"]
        
        # Delete the menu cycle
        response = await client.delete(f"{api_prefix}/menu-cycles/{cycle_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()
        
        # Verify cycle is deleted
        get_response = await client.get(f"{api_prefix}/menu-cycles/{cycle_id}")
        assert get_response.status_code == 404 