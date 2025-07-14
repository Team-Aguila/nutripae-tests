"""
Integration tests for Inventory Movements API
Test cases: INV-MOV-001 to INV-MOV-037
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response


class TestInventoryMovementsAPI:
    """Test suite for Inventory Movements API endpoints"""
    
    # RECEIVE INVENTORY TESTS
    
    async def test_receive_inventory_with_purchase_order_success(self, client: httpx.AsyncClient, api_prefix: str, sample_inventory_receipt_data: Dict[str, Any]):
        """INV-MOV-001: Successfully receive inventory with purchase order"""
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=sample_inventory_receipt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["product_id"] == sample_inventory_receipt_data["product_id"]
        assert data["institution_id"] == sample_inventory_receipt_data["institution_id"]
        assert data["quantity_received"] == sample_inventory_receipt_data["quantity_received"]
        assert data["unit_of_measure"] == sample_inventory_receipt_data["unit_of_measure"]
        assert data["batch_number"] == sample_inventory_receipt_data["batch_number"]
        assert data["expiration_date"] == sample_inventory_receipt_data["expiration_date"]
        # Note: API doesn't return inventory_batch_id field, only inventory_id
        assert "inventory_id" in data or "inventory_batch_id" in data
        assert "movement_id" in data
        assert "created_at" in data

    async def test_receive_inventory_without_purchase_order_success(self, client: httpx.AsyncClient, api_prefix: str, test_product):
        """INV-MOV-002: Successfully receive inventory without purchase order"""
        product_id = test_product.get("_id") or test_product.get("id")
        
        receipt_data = {
            "product_id": product_id,
            "institution_id": 1,
            "storage_location": "test-warehouse",
            "quantity_received": 10.0,
            "unit_of_measure": "kg",
            "expiration_date": "2024-06-15",
            "batch_number": f"TEST-BATCH-{product_id[-8:]}",
            "received_by": "test_manager",
            "reception_date": "2024-01-15T08:30:00Z",
            "notes": "Test manual reception"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["product_id"] == receipt_data["product_id"]
        assert data["institution_id"] == receipt_data["institution_id"]
        assert data["quantity_received"] == receipt_data["quantity_received"]

    async def test_receive_inventory_non_existent_product(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-003: Fail to receive with non-existent product"""
        receipt_data = {
            "product_id": non_existent_product_id,
            "institution_id": 1,
            "storage_location": "test-warehouse",
            "quantity_received": 25.5,
            "unit_of_measure": "kg",
            "expiration_date": "2024-06-15",
            "batch_number": f"TEST-BATCH-{non_existent_product_id[-8:]}",
            "received_by": "test_manager"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_receive_inventory_duplicate_batch_number(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-004: Fail to receive with duplicate batch number"""
        receipt_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "storage_location": "warehouse-01",
            "quantity_received": 25.5,
            "unit_of_measure": "kg",
            "expiration_date": "2024-06-15",
            "batch_number": "BATCH-2024-001",
            "received_by": "warehouse_manager"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        
        assert response.status_code == 409
        data = response.json()
        assert_error_response(data, "already exists")

    async def test_receive_inventory_invalid_quantity(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-005: Fail to receive with invalid quantity"""
        receipt_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "storage_location": "warehouse-01",
            "quantity_received": -5.0,
            "unit_of_measure": "kg",
            "expiration_date": "2024-06-15",
            "batch_number": "BATCH-2024-001",
            "received_by": "warehouse_manager"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_receive_inventory_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-006: Fail to receive with missing required fields"""
        receipt_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "quantity_received": 25.5
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # CONSUME INVENTORY TESTS
    
    async def test_consume_inventory_fifo_success(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """INV-MOV-007: Successfully consume inventory with FIFO"""
        # First ensure we have inventory to consume
        if not test_inventory_batch:
            pytest.skip("No inventory batch available for consumption test")
        
        product_id = test_inventory_batch["product_id"]
        
        consumption_data = {
            "product_id": product_id,
            "institution_id": 1,
            "storage_location": "test-warehouse",
            "quantity": 5.5,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "test consumption",
            "notes": "Test consumption",
            "consumed_by": "test_chef"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["product_id"] == consumption_data["product_id"]
        assert data["institution_id"] == consumption_data["institution_id"]
        assert data["total_quantity_consumed"] == consumption_data["quantity"]
        assert data["unit"] == consumption_data["unit"]
        assert "batch_details" in data
        assert "movement_ids" in data
        assert "created_at" in data

    async def test_consume_inventory_single_batch_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-008: Successfully consume inventory from single batch"""
        consumption_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "storage_location": "warehouse-01",
            "quantity": 2.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Used for breakfast",
            "consumed_by": "chef_juan"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["product_id"] == consumption_data["product_id"]
        assert data["total_quantity_consumed"] == consumption_data["quantity"]

    async def test_consume_inventory_insufficient_stock(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-009: Fail to consume with insufficient stock"""
        consumption_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "storage_location": "warehouse-01",
            "quantity": 100.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Large quantity",
            "consumed_by": "chef_maria"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 400
        data = response.json()
        assert_error_response(data, "Insufficient stock")

    async def test_consume_inventory_non_existent_product(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-010: Fail to consume with non-existent product"""
        consumption_data = {
            "product_id": non_existent_product_id,
            "institution_id": 1,
            "storage_location": "test-warehouse",
            "quantity": 5.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "test consumption",
            "notes": "Test consumption with non-existent product",
            "consumed_by": "test_chef"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_consume_inventory_invalid_quantity(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-011: Fail to consume with invalid quantity"""
        consumption_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "storage_location": "warehouse-01",
            "quantity": -5.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Test",
            "consumed_by": "chef_maria"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    async def test_consume_inventory_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-012: Fail to consume with missing required fields"""
        consumption_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "institution_id": 1,
            "quantity": 5.0
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # MANUAL ADJUSTMENT TESTS
    
    async def test_manual_adjustment_positive_success(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """INV-MOV-013: Successfully create positive adjustment"""
        if not test_inventory_batch:
            pytest.skip("No inventory batch available for adjustment test")
        
        product_id = test_inventory_batch["product_id"]
        inventory_id = test_inventory_batch.get("inventory_batch_id")
        
        if not inventory_id:
            pytest.skip("No inventory_batch_id available for adjustment test")
        
        adjustment_data = {
            "product_id": product_id,
            "inventory_id": inventory_id,
            "quantity": 5.0,
            "unit": "kg",
            "reason": "Test adjustment",
            "notes": "Test inventory adjustment",
            "adjusted_by": "test_auditor"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/manual-adjustment", json=adjustment_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["product_id"] == adjustment_data["product_id"]
        assert data["inventory_id"] == adjustment_data["inventory_id"]
        # API returns adjustment_quantity instead of quantity
        assert data["adjustment_quantity"] == adjustment_data["quantity"]
        assert data["unit"] == adjustment_data["unit"]
        assert data["reason"] == adjustment_data["reason"]
        assert "movement_id" in data
        # API returns new_stock instead of new_inventory_level
        assert "new_stock" in data
        assert "previous_stock" in data
        assert "created_at" in data

    async def test_manual_adjustment_negative_success(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """INV-MOV-014: Successfully create negative adjustment"""
        if not test_inventory_batch:
            pytest.skip("No inventory batch available for adjustment test")
        
        product_id = test_inventory_batch["product_id"]
        inventory_id = test_inventory_batch.get("inventory_batch_id")
        
        if not inventory_id:
            pytest.skip("No inventory_batch_id available for adjustment test")
        
        adjustment_data = {
            "product_id": product_id,
            "inventory_id": inventory_id,
            "quantity": -3.0,
            "unit": "kg",
            "reason": "Physical count found less stock",
            "notes": "Discrepancy correction",
            "adjusted_by": "auditor_maria"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/manual-adjustment", json=adjustment_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        # API returns adjustment_quantity instead of quantity
        assert data["adjustment_quantity"] == adjustment_data["quantity"]

    async def test_manual_adjustment_negative_stock_fail(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """INV-MOV-015: Fail to create adjustment that would cause negative stock"""
        if not test_inventory_batch:
            pytest.skip("No inventory batch available for adjustment test")
        
        product_id = test_inventory_batch["product_id"]
        inventory_id = test_inventory_batch.get("inventory_batch_id")
        
        if not inventory_id:
            pytest.skip("No inventory_batch_id available for adjustment test")
        
        adjustment_data = {
            "product_id": product_id,
            "inventory_id": inventory_id,
            "quantity": -1000.0,  # Large negative to cause negative stock
            "unit": "kg",
            "reason": "Test negative stock",
            "notes": "Should fail",
            "adjusted_by": "test_auditor"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/manual-adjustment", json=adjustment_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data

    async def test_manual_adjustment_non_existent_inventory(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-016: Fail to create adjustment with non-existent inventory"""
        adjustment_data = {
            "product_id": "6873372e4a1672992ce8b353",
            "inventory_id": "648f8f8f8f8f8f8f8f8f8f8b",
            "quantity": 5.0,
            "unit": "kg",
            "reason": "Physical count",
            "notes": "Test",
            "adjusted_by": "auditor_maria"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/manual-adjustment", json=adjustment_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    async def test_manual_adjustment_zero_quantity(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """INV-MOV-017: Test adjustment with zero quantity"""
        if not test_inventory_batch:
            pytest.skip("No inventory batch available for adjustment test")
        
        product_id = test_inventory_batch["product_id"]
        inventory_id = test_inventory_batch.get("inventory_batch_id")
        
        if not inventory_id:
            pytest.skip("No inventory_batch_id available for adjustment test")
        
        adjustment_data = {
            "product_id": product_id,
            "inventory_id": inventory_id,
            "quantity": 0.0,
            "unit": "kg",
            "reason": "Zero adjustment",
            "notes": "Test zero quantity adjustment",
            "adjusted_by": "test_auditor"
        }
        
        response = await client.post(f"{api_prefix}/inventory-movements/manual-adjustment", json=adjustment_data)
        
        # API allows zero quantity adjustments (returns 201)
        assert response.status_code == 201
        data = response.json()
        assert "transaction_id" in data
        assert data["adjustment_quantity"] == 0.0

    # PRODUCT MOVEMENTS QUERY TESTS
    
    async def test_get_product_movements_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-018: Successfully retrieve movements for a product"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/6873372e4a1672992ce8b353")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are movements
            movement = data[0]
            assert "id" in movement or "_id" in movement
            assert "movement_type" in movement
            assert "product_id" in movement
            assert "quantity" in movement
            assert "unit" in movement
            assert "movement_date" in movement
            assert "created_at" in movement

    async def test_get_product_movements_filtered_by_institution(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-019: Successfully retrieve movements filtered by institution"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/6873372e4a1672992ce8b353", params={"institution_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_product_movements_filtered_by_type(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-020: Successfully retrieve movements filtered by type"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/6873372e4a1672992ce8b353", params={"movement_type": "receipt"})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_product_movements_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-021: Successfully retrieve movements with pagination"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/6873372e4a1672992ce8b353", params={"limit": 10, "offset": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    async def test_get_product_movements_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-022: Retrieve movements for non-existent product returns empty array"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/{non_existent_product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty array for non-existent product

    async def test_get_product_movements_invalid_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-023: Fail with invalid product_id format"""
        response = await client.get(f"{api_prefix}/inventory-movements/product/invalid_id")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # CURRENT STOCK TESTS
    
    async def test_get_current_stock_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-024: Successfully get current stock"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock/6873372e4a1672992ce8b353/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "institution_id" in data
        assert "current_stock" in data
        assert "unit" in data
        assert data["product_id"] == "6873372e4a1672992ce8b353"
        assert data["institution_id"] == 1

    async def test_get_current_stock_filtered_by_storage(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-025: Successfully get stock filtered by storage location"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock/6873372e4a1672992ce8b353/1", params={"storage_location": "warehouse-01"})
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "storage_location" in data
        assert data["storage_location"] == "warehouse-01"

    async def test_get_current_stock_filtered_by_lot(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-026: Successfully get stock filtered by lot"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock/6873372e4a1672992ce8b353/1", params={"lot": "LOT-2024-001"})
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "lot" in data
        assert data["lot"] == "LOT-2024-001"

    async def test_get_current_stock_product_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-027: Get stock for non-existent product returns default response"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock/{non_existent_product_id}/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "institution_id" in data
        assert "current_stock" in data
        assert data["product_id"] == non_existent_product_id
        assert data["institution_id"] == 1
        assert data["current_stock"] == 0  # Should return 0 stock for non-existent product

    async def test_get_current_stock_invalid_product_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-028: Fail with invalid product_id format"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock/invalid_id/1")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # STOCK SUMMARY TESTS
    
    async def test_get_stock_summary_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-029: Successfully get stock summary"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/6873372e4a1672992ce8b353/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "institution_id" in data
        assert "total_available_stock" in data
        assert "number_of_batches" in data
        assert "batches" in data
        assert data["product_id"] == "6873372e4a1672992ce8b353"
        assert data["institution_id"] == 1

    async def test_get_stock_summary_filtered_by_storage(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-030: Successfully get stock summary filtered by storage location"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/6873372e4a1672992ce8b353/1", params={"storage_location": "warehouse-01"})
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "storage_location" in data
        assert data["storage_location"] == "warehouse-01"

    async def test_get_stock_summary_product_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-031: Get summary for non-existent product returns empty summary"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{non_existent_product_id}/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "product_id" in data
        assert "institution_id" in data
        assert "total_available_stock" in data
        assert "number_of_batches" in data
        assert "batches" in data
        assert data["product_id"] == non_existent_product_id
        assert data["institution_id"] == 1
        assert data["total_available_stock"] == 0.0  # Should return 0 stock for non-existent product
        assert data["number_of_batches"] == 0
        assert isinstance(data["batches"], list)
        assert len(data["batches"]) == 0  # Should return empty batches array

    async def test_get_stock_summary_invalid_product_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-032: Fail with invalid product_id format"""
        response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/invalid_id/1")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # CONSUMPTION HISTORY TESTS
    
    async def test_get_consumption_history_success(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-033: Successfully get consumption history"""
        response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/6873372e4a1672992ce8b353")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If there are movements
            movement = data[0]
            assert "id" in movement or "_id" in movement
            assert "movement_type" in movement
            assert "product_id" in movement
            assert "quantity" in movement
            assert "unit" in movement

    async def test_get_consumption_history_filtered_by_institution(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-034: Successfully get consumption history filtered by institution"""
        response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/6873372e4a1672992ce8b353", params={"institution_id": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_consumption_history_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-035: Successfully get consumption history with pagination"""
        response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/6873372e4a1672992ce8b353", params={"limit": 10, "offset": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    async def test_get_consumption_history_product_not_found(self, client: httpx.AsyncClient, api_prefix: str, non_existent_product_id):
        """INV-MOV-036: Get consumption history for non-existent product returns empty array"""
        response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/{non_existent_product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty array for non-existent product

    async def test_get_consumption_history_invalid_product_id(self, client: httpx.AsyncClient, api_prefix: str):
        """INV-MOV-037: Fail with invalid product_id format"""
        response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/invalid_id")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data) 