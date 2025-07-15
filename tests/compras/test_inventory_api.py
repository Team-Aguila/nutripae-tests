"""
Integration tests for Inventory API
Test cases: INV-001 to INV-017
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response
from ..test_metadata import add_test_info


class TestInventoryAPI:
    """Test suite for Inventory API endpoints"""
    
    # INVENTORY QUERY TESTS
    
    @add_test_info(
        description="Obtener inventario sin filtros exitosamente",
        expected_result="Status Code: 200, lista completa de inventario",
        module="Compras",
        test_id="INV-001"
    )
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

    @add_test_info(
        description="Obtener inventario filtrado por institución",
        expected_result="Status Code: 200, inventario filtrado por institución",
        module="Compras",
        test_id="INV-002"
    )
    async def test_get_inventory_filtered_by_institution(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-002: Successfully retrieve inventory filtered by institution"""
        response = await client.get(f"{api_prefix}/inventory", params={"institution_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario filtrado por producto",
        expected_result="Status Code: 200, inventario filtrado por producto",
        module="Compras",
        test_id="INV-003"
    )
    async def test_get_inventory_filtered_by_product(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-003: Successfully retrieve inventory filtered by product"""
        response = await client.get(f"{api_prefix}/inventory", params={"product_id": "648f8f8f8f8f8f8f8f8f8f8f"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario con paginación",
        expected_result="Status Code: 200, inventario paginado",
        module="Compras",
        test_id="INV-004"
    )
    async def test_get_inventory_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-004: Successfully retrieve inventory with pagination"""
        response = await client.get(f"{api_prefix}/inventory", params={"limit": 10, "offset": 5})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario excluyendo productos expirados",
        expected_result="Status Code: 200, inventario sin productos expirados",
        module="Compras",
        test_id="INV-005"
    )
    async def test_get_inventory_exclude_expired(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-005: Successfully retrieve inventory excluding expired products"""
        response = await client.get(f"{api_prefix}/inventory", params={"show_expired": False})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario con productos bajo el umbral mínimo",
        expected_result="Status Code: 200, productos bajo umbral",
        module="Compras",
        test_id="INV-006"
    )
    async def test_get_inventory_below_threshold(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-006: Successfully retrieve inventory below minimum threshold"""
        response = await client.get(f"{api_prefix}/inventory", params={"show_below_threshold": True})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario filtrado por categoría",
        expected_result="Status Code: 200, inventario filtrado por categoría",
        module="Compras",
        test_id="INV-007"
    )
    async def test_get_inventory_by_category(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-007: Successfully retrieve inventory filtered by category"""
        response = await client.get(f"{api_prefix}/inventory", params={"category": "cereales"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    @add_test_info(
        description="Obtener inventario filtrado por proveedor",
        expected_result="Status Code: 200, inventario filtrado por proveedor",
        module="Compras",
        test_id="INV-008"
    )
    async def test_get_inventory_by_provider(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-008: Successfully retrieve inventory filtered by provider"""
        response = await client.get(f"{api_prefix}/inventory", params={"provider_id": "648f8f8f8f8f8f8f8f8f8f8f"})
        
        assert response.status_code == 200
        data = response.json()
        items_key = "inventory_items" if "inventory_items" in data else "items"
        assert items_key in data

    # INVENTORY VALIDATION TESTS
    
    @add_test_info(
        description="Fallar al obtener inventario con ID de producto inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-009"
    )
    async def test_get_inventory_invalid_product_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-009: Fail to retrieve inventory with invalid product ID"""
        response = await client.get(f"{api_prefix}/inventory", params={"product_id": "invalid_id"})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al obtener inventario con ID de proveedor inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-010"
    )
    async def test_get_inventory_invalid_provider_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-010: Fail to retrieve inventory with invalid provider ID"""
        response = await client.get(f"{api_prefix}/inventory", params={"provider_id": "invalid_id"})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al obtener inventario con límite inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-011"
    )
    async def test_get_inventory_invalid_limit(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-011: Fail to retrieve inventory with invalid limit"""
        response = await client.get(f"{api_prefix}/inventory", params={"limit": 1001})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al obtener inventario con offset inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-012"
    )
    async def test_get_inventory_invalid_offset(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-012: Fail to retrieve inventory with invalid offset"""
        response = await client.get(f"{api_prefix}/inventory", params={"offset": -1})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # INVENTORY THRESHOLD TESTS
    
    @add_test_info(
        description="Actualizar umbral de inventario exitosamente",
        expected_result="Status Code: 200, umbral actualizado",
        module="Compras",
        test_id="INV-013"
    )
    async def test_update_inventory_threshold_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-013: Successfully update inventory threshold"""
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

    @add_test_info(
        description="Actualizar umbral de inventario a cero",
        expected_result="Status Code: 200, umbral actualizado a cero",
        module="Compras",
        test_id="INV-014"
    )
    async def test_update_inventory_threshold_zero(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-014: Successfully update inventory threshold to zero"""
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

    @add_test_info(
        description="Fallar al actualizar umbral de inventario con valor negativo",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-015"
    )
    async def test_update_inventory_threshold_negative(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-015: Fail to update inventory threshold with negative value"""
        response = await client.put(
            f"{api_prefix}/inventory/648f8f8f8f8f8f8f8f8f8f8f/threshold",
            params={"new_threshold": -5.0}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al actualizar umbral de inventario que no existe",
        expected_result="Status Code: 404, inventario no encontrado",
        module="Compras",
        test_id="INV-016"
    )
    async def test_update_inventory_threshold_not_found(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-016: Fail to update threshold for non-existent inventory"""
        response = await client.put(
            f"{api_prefix}/inventory/648f8f8f8f8f8f8f8f8f8f8a/threshold",
            params={"new_threshold": 10.0}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "Inventory item not found")

    @add_test_info(
        description="Fallar al actualizar umbral con ID de inventario inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="INV-017"
    )
    async def test_update_inventory_threshold_invalid_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-017: Fail to update threshold with invalid inventory ID"""
        response = await client.put(
            f"{api_prefix}/inventory/invalid_id/threshold",
            params={"new_threshold": 10.0}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data) 