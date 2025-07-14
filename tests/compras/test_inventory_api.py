"""
Integration tests for Inventory API
Test cases: INV-001 to INV-017
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response


class TestInventoryAPI:
    """Test suite for Inventory API endpoints"""
    
    # INVENTORY QUERY TESTS
    
    async def test_get_inventory_no_filters(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-001: Successfully retrieve inventory without filters"""
        response = await client.get(f"{api_prefix}/inventory")
        
        assert response.status_code == 200
        data = response.json()
        # Handle both response formats
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data
        assert "summary" in data or "page_info" in data
        
        if "summary" in data:
            summary = data["summary"]
            assert "total_items" in summary
            assert "below_threshold_count" in summary
            assert "expired_count" in summary

    async def test_get_inventory_filtered_by_institution(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-002: Successfully retrieve inventory filtered by institution"""
        response = await client.get(f"{api_prefix}/inventory", params={"institution_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_filtered_by_product(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-003: Successfully retrieve inventory filtered by product"""
        response = await client.get(f"{api_prefix}/inventory", params={"product_id": "648f8f8f8f8f8f8f8f8f8f8f"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-004: Successfully retrieve inventory with pagination"""
        response = await client.get(f"{api_prefix}/inventory", params={"limit": 10, "offset": 5})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_exclude_expired(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-005: Successfully retrieve inventory excluding expired items"""
        response = await client.get(f"{api_prefix}/inventory", params={"show_expired": False})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_below_threshold(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-006: Successfully retrieve items below threshold"""
        response = await client.get(f"{api_prefix}/inventory", params={"show_below_threshold": True})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_by_category(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-007: Successfully retrieve inventory by category"""
        response = await client.get(f"{api_prefix}/inventory", params={"category": "cereales"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    async def test_get_inventory_by_provider(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-008: Successfully retrieve inventory by provider"""
        response = await client.get(f"{api_prefix}/inventory", params={"provider_id": "648f8f8f8f8f8f8f8f8f8f8f"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    # INVENTORY VALIDATION TESTS
    
    async def test_get_inventory_invalid_product_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-009: Fail with invalid product_id format"""
        response = await client.get(f"{api_prefix}/inventory", params={"product_id": "invalid_id"})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_get_inventory_invalid_provider_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-010: Fail with invalid provider_id format"""
        response = await client.get(f"{api_prefix}/inventory", params={"provider_id": "invalid_id"})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_get_inventory_invalid_limit(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-011: Fail with invalid limit value"""
        response = await client.get(f"{api_prefix}/inventory", params={"limit": 1001})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_get_inventory_invalid_offset(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-012: Fail with invalid offset value"""
        response = await client.get(f"{api_prefix}/inventory", params={"offset": -1})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # INVENTORY THRESHOLD TESTS
    
    async def test_update_inventory_threshold_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-013: Successfully update minimum threshold"""
        response = await client.put(
            f"{api_prefix}/inventory/686c6e059d212a3310b869be/threshold",
            params={"new_threshold": 10.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "inventory_id" in data
        assert "new_threshold" in data
        assert data["new_threshold"] == 10.0

    async def test_update_inventory_threshold_zero(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-014: Successfully update threshold to zero"""
        response = await client.put(
            f"{api_prefix}/inventory/686c6e059d212a3310b869be/threshold",
            params={"new_threshold": 0.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "inventory_id" in data
        assert "new_threshold" in data
        assert data["new_threshold"] == 0.0

    async def test_update_inventory_threshold_negative(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-015: Fail to update with negative threshold"""
        response = await client.put(
            f"{api_prefix}/inventory/648f8f8f8f8f8f8f8f8f8f8f/threshold",
            params={"new_threshold": -5.0}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_update_inventory_threshold_not_found(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-016: Fail to update non-existent inventory item"""
        response = await client.put(
            f"{api_prefix}/inventory/648f8f8f8f8f8f8f8f8f8f8a/threshold",
            params={"new_threshold": 10.0}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "Inventory item not found")

    async def test_update_inventory_threshold_invalid_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-017: Fail to update with invalid inventory_id format"""
        response = await client.put(
            f"{api_prefix}/inventory/invalid_id/threshold",
            params={"new_threshold": 10.0}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data) 