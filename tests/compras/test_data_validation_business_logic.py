"""
Integration tests for Data Validation and Business Logic
Test cases: VAL-001 to CONS-004
"""
import pytest
import httpx
from typing import Dict, Any
from unittest.mock import Mock, patch

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response
from ..test_metadata import add_test_info


class TestCrossEntityValidation:
    """Test suite for Cross-Entity Validation"""
    
    @add_test_info(
        description="Fallar al crear producto con proveedor no existente",
        expected_result="Status Code: 404, error de proveedor no encontrado",
        module="Compras",
        test_id="VAL-001"
    )
    async def test_create_product_with_non_existent_provider(self, client: httpx.AsyncClient, api_prefix: str, non_existent_provider_id):
        """VAL-001: Fail to create product with non-existent provider"""
        product_data = {
            "provider_id": non_existent_provider_id,
            "name": "Test Product",
            "weight": 1.0,
            "weekly_availability": "MONDAY",
            "life_time": {"value": 30, "unit": "days"}
        }
        
        response = await client.post(f"{api_prefix}/products/", json=product_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")
    
    @add_test_info(
        description="Fallar al crear orden de compra con proveedor no existente",
        expected_result="Status Code: 404, error de proveedor no encontrado",
        module="Compras",
        test_id="VAL-002"
    )
    async def test_create_purchase_order_with_non_existent_provider(self, client: httpx.AsyncClient, api_prefix: str, non_existent_provider_id, test_product):
        """VAL-002: Fail to create purchase order with non-existent provider"""
        product_id = test_product.get("_id")
        
        order_data = {
            "provider_id": non_existent_provider_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 50.0,
                    "unit": "kg",
                    "price": 2500.0
                }
            ],
            "required_delivery_date": "2024-02-01"
        }
        
        response = await client.post(f"{api_prefix}/purchase-orders/", json=order_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")
    
    @add_test_info(
        description="Fallar al crear orden de compra con producto no existente",
        expected_result="Status Code: 404, error de producto no encontrado",
        module="Compras",
        test_id="VAL-003"
    )
    async def test_create_purchase_order_with_non_existent_product(self, client: httpx.AsyncClient, api_prefix: str, test_provider, non_existent_product_id):
        """VAL-003: Fail to create purchase order with non-existent product"""
        provider_id = test_provider.get("_id")
        
        order_data = {
            "provider_id": provider_id,
            "items": [
                {
                    "product_id": non_existent_product_id,
                    "quantity": 50.0,
                    "unit": "kg",
                    "price": 2500.0
                }
            ],
            "required_delivery_date": "2024-02-01"
        }
        
        response = await client.post(f"{api_prefix}/purchase-orders/", json=order_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")
    
    @add_test_info(
        description="Fallar al recibir inventario para orden de compra no existente",
        expected_result="Status Code: 400 o 404, error de orden no encontrada",
        module="Compras",
        test_id="VAL-004"
    )
    async def test_receive_inventory_for_non_existent_purchase_order(self, client: httpx.AsyncClient, api_prefix: str, test_product, non_existent_purchase_order_id):
        """VAL-004: Fail to receive inventory for non-existent purchase order"""
        product_id = test_product.get("_id")
        
        receipt_data = {
            "institution_id": 1,
            "purchase_order_id": non_existent_purchase_order_id,
            "receipt_date": "2024-01-15",
            "delivery_person_name": "Juan Pérez",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 25.0,
                    "unit": "kg",
                    "storage_location": "warehouse-01",
                    "lot": "LOT-2024-001",
                    "expiration_date": "2024-06-15"
                }
            ]
        }
        
        response = await client.post(f"{api_prefix}/ingredient-receipts/", json=receipt_data)
        
        # This should fail because the purchase order doesn't exist
        assert response.status_code in [400, 404]
        data = response.json()
        assert_error_response(data)
    
    @add_test_info(
        description="Crear recibo parcial que no completa la orden de compra",
        expected_result="Status Code: 201, orden permanece en estado pendiente",
        module="Compras",
        test_id="VAL-005"
    )
    async def test_create_partial_receipt_that_does_not_complete_purchase_order(self, client: httpx.AsyncClient, api_prefix: str, test_purchase_order, test_product):
        """VAL-005: Successfully create partial receipt that doesn't complete purchase order"""
        if not test_purchase_order:
            pytest.skip("Could not create test purchase order")
        
        product_id = test_product.get("_id")
        purchase_order_id = test_purchase_order.get("_id")
        
        # Create receipt with partial quantities
        receipt_data = {
            "institution_id": 1,
            "purchase_order_id": purchase_order_id,
            "receipt_date": "2024-01-15",
            "delivery_person_name": "Juan Pérez",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 25.0,  # Partial quantity (ordered 50)
                    "unit": "kg",
                    "storage_location": "warehouse-01",
                    "lot": "LOT-2024-001",
                    "expiration_date": "2024-06-15"
                }
            ]
        }
        
        response = await client.post(f"{api_prefix}/ingredient-receipts/", json=receipt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_response_has_id(data)
        
        # Verify purchase order status remains "pending" or "shipped", not "completed"
        order_id = data["purchase_order_id"]
        order_response = await client.get(f"{api_prefix}/purchase-orders/{order_id}")
        assert order_response.status_code == 200
        order_data = order_response.json()
        assert order_data["status"] in ["pending", "shipped"]  # Not "completed"
    
    @add_test_info(
        description="Crear recibo que completa la orden de compra",
        expected_result="Status Code: 201, orden cambia a estado completada",
        module="Compras",
        test_id="VAL-006"
    )
    async def test_create_receipt_that_completes_purchase_order(self, client: httpx.AsyncClient, api_prefix: str, test_purchase_order, test_product):
        """VAL-006: Successfully create receipt that completes purchase order"""
        if not test_purchase_order:
            pytest.skip("Could not create test purchase order")
        
        product_id = test_product.get("_id")
        purchase_order_id = test_purchase_order.get("_id")
        
        # Create receipt with complete quantities
        receipt_data = {
            "institution_id": 1,
            "purchase_order_id": purchase_order_id,
            "receipt_date": "2024-01-15",
            "delivery_person_name": "Juan Pérez",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 50.0,  # Complete quantity as ordered
                    "unit": "kg",
                    "storage_location": "warehouse-01",
                    "lot": "LOT-2024-001",
                    "expiration_date": "2024-06-15"
                }
            ]
        }
        
        response = await client.post(f"{api_prefix}/ingredient-receipts/", json=receipt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert_response_has_id(data)
        
        # Verify purchase order status changes to "completed"
        order_id = data["purchase_order_id"]
        order_response = await client.get(f"{api_prefix}/purchase-orders/{order_id}")
        assert order_response.status_code == 200
        order_data = order_response.json()
        assert order_data["status"] == "completed"


class TestDataConsistency:
    """Test suite for Data Consistency validation"""
    
    @add_test_info(
        description="Verificar que los niveles de inventario se actualizan después de recibir productos",
        expected_result="Niveles de inventario incrementados correctamente",
        module="Compras",
        test_id="CONS-001"
    )
    async def test_inventory_levels_updated_after_receipt(self, client: httpx.AsyncClient, api_prefix: str, test_product):
        """CONS-001: Verify inventory levels are correctly updated after receipt"""
        product_id = test_product.get("_id")
        institution_id = 1
        
        # Get initial inventory levels
        initial_response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{product_id}/{institution_id}")
        initial_stock = 0
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_stock = initial_data.get("total_available_stock", 0)
        
        # Receive inventory
        receipt_data = {
            "product_id": product_id,
            "institution_id": institution_id,
            "storage_location": "warehouse-01",
            "quantity_received": 25.5,
            "unit_of_measure": "kg",
            "expiration_date": "2024-06-15",
            "batch_number": "BATCH-2024-001",
            "received_by": "warehouse_manager",
            "reception_date": "2024-01-15T08:30:00Z",
            "notes": "Fresh delivery"
        }
        
        receipt_response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
        assert receipt_response.status_code == 201
        
        # Check updated inventory levels
        updated_response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{product_id}/{institution_id}")
        assert updated_response.status_code == 200
        
        updated_data = updated_response.json()
        expected_stock = initial_stock + 25.5
        assert updated_data["total_available_stock"] == expected_stock
    
    @add_test_info(
        description="Verificar que los niveles de inventario se actualizan después del consumo",
        expected_result="Niveles de inventario decrementados correctamente",
        module="Compras",
        test_id="CONS-002"
    )
    async def test_inventory_levels_updated_after_consumption(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """CONS-002: Verify inventory levels are correctly updated after consumption"""
        if not test_inventory_batch:
            pytest.skip("Could not create test inventory batch")
        
        product_id = test_inventory_batch.get("product_id")
        institution_id = test_inventory_batch.get("institution_id")
        
        # Get initial inventory levels
        initial_response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{product_id}/{institution_id}")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        initial_stock = initial_data["total_available_stock"]
        
        # Consume inventory
        consumption_data = {
            "product_id": product_id,
            "institution_id": institution_id,
            "storage_location": "test-warehouse",
            "quantity": 5.5,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Used for lunch menu",
            "consumed_by": "chef_maria"
        }
        
        consumption_response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        assert consumption_response.status_code == 201
        
        # Check updated inventory levels
        updated_response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{product_id}/{institution_id}")
        assert updated_response.status_code == 200
        
        updated_data = updated_response.json()
        expected_stock = initial_stock - 5.5
        assert updated_data["total_available_stock"] == expected_stock
    
    @add_test_info(
        description="Verificar que la lógica FIFO se mantiene en múltiples operaciones de consumo",
        expected_result="Consumo sigue orden FIFO correctamente",
        module="Compras",
        test_id="CONS-003"
    )
    async def test_fifo_logic_maintained_across_multiple_consumption_operations(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """CONS-003: Verify FIFO logic is maintained across multiple consumption operations"""
        if not test_inventory_batch:
            pytest.skip("Could not create test inventory batch")
        
        product_id = test_inventory_batch.get("product_id")
        institution_id = test_inventory_batch.get("institution_id")
        
        # Get initial stock summary to check batch order
        initial_response = await client.get(f"{api_prefix}/inventory-movements/stock-summary/{product_id}/{institution_id}")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        initial_batches = initial_data.get("batches", [])
        
        if not initial_batches:
            pytest.skip("No batches available for FIFO testing")
        
        # Sort batches by admission date to verify FIFO order
        sorted_batches = sorted(initial_batches, key=lambda x: x.get("date_of_admission", ""))
        oldest_batch = sorted_batches[0]
        
        # Consume part of the oldest batch
        consumption_data = {
            "product_id": product_id,
            "institution_id": institution_id,
            "storage_location": "test-warehouse",
            "quantity": 2.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Testing FIFO logic",
            "consumed_by": "chef_maria"
        }
        
        consumption_response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        assert consumption_response.status_code == 201
        
        # Verify the oldest batch was consumed first
        response_data = consumption_response.json()
        if "batch_details" in response_data:
            batch_details = response_data["batch_details"]
            # First batch consumed should be the oldest one
            first_consumed_batch = batch_details[0]
            assert first_consumed_batch["lot"] == oldest_batch["lot"]
    
    @add_test_info(
        description="Verificar que la pista de auditoría de movimientos esté completa",
        expected_result="Historial de movimientos completo y ordenado",
        module="Compras",
        test_id="CONS-004"
    )
    async def test_movement_audit_trail_is_complete(self, client: httpx.AsyncClient, api_prefix: str, test_inventory_batch):
        """CONS-004: Verify movement audit trail is complete"""
        if not test_inventory_batch:
            pytest.skip("Could not create test inventory batch")
        
        product_id = test_inventory_batch.get("product_id")
        institution_id = test_inventory_batch.get("institution_id")
        
        # Get initial movement count
        initial_response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/{product_id}")
        initial_movements = initial_response.json() if initial_response.status_code == 200 else []
        initial_count = len(initial_movements)
        
        # Perform inventory operation (consumption)
        consumption_data = {
            "product_id": product_id,
            "institution_id": institution_id,
            "storage_location": "test-warehouse",
            "quantity": 3.0,
            "unit": "kg",
            "consumption_date": "2024-01-15T10:30:00Z",
            "reason": "menu preparation",
            "notes": "Audit trail test",
            "consumed_by": "chef_maria"
        }
        
        consumption_response = await client.post(f"{api_prefix}/inventory-movements/consume-inventory", json=consumption_data)
        assert consumption_response.status_code == 201
        
        # Get updated movement history
        updated_response = await client.get(f"{api_prefix}/inventory-movements/consumption-history/{product_id}")
        assert updated_response.status_code == 200
        
        updated_movements = updated_response.json()
        
        # Verify new movements were recorded
        assert len(updated_movements) > initial_count
        
        # Verify movements are in chronological order (newest first typically)
        for i in range(len(updated_movements) - 1):
            current_date = updated_movements[i]["movement_date"]
            next_date = updated_movements[i + 1]["movement_date"]
            # Assuming newest first order
            assert current_date >= next_date
        
        # Verify the latest movement matches our consumption
        latest_movement = updated_movements[0]
        assert latest_movement["movement_type"] == "usage"
        assert latest_movement["quantity"] == -3.0  # Negative for consumption
        assert "Audit trail test" in latest_movement["notes"] 