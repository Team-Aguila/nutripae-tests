"""
Shared pytest fixtures for PAE Compras API integration tests
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
async def test_provider(client: httpx.AsyncClient, api_prefix: str):
    """Create a test provider and clean up after test"""
    provider_data = {
        "name": "Test Provider Integration",
        "nit": "900999888-7",
        "address": "Test Address 123",
        "responsible_name": "Test Manager",
        "email": "test@provider.com",
        "phone_number": "3009998888",
        "is_local_provider": True
    }
    
    # Create provider
    response = await client.post(f"{api_prefix}/providers/", json=provider_data)
    assert response.status_code == 201
    provider = response.json()
    
    yield provider
    
    # Cleanup: Delete provider
    try:
        provider_id = provider.get("_id")
        if provider_id:
            await client.delete(f"{api_prefix}/providers/{provider_id}")
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_product(client: httpx.AsyncClient, api_prefix: str, test_provider):
    """Create a test product and clean up after test"""
    provider_id = test_provider.get("_id")
    
    product_data = {
        "provider_id": provider_id,
        "name": "Test Product Integration",
        "weight": 1.0,
        "weekly_availability": "MONDAY",
        "life_time": {"value": 30, "unit": "days"}
    }
    
    # Create product
    response = await client.post(f"{api_prefix}/products/", json=product_data)
    assert response.status_code == 201
    product = response.json()
    
    yield product
    
    # Cleanup: Delete product
    try:
        product_id = product.get("_id")
        if product_id:
            await client.delete(f"{api_prefix}/products/{product_id}")
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def test_purchase_order(client: httpx.AsyncClient, api_prefix: str, test_provider, test_product):
    """Create a test purchase order and clean up after test"""
    provider_id = test_provider.get("_id")
    product_id = test_product.get("_id")
    
    order_data = {
        "provider_id": provider_id,
        "items": [
            {
                "product_id": product_id,
                "quantity": 50.0,
                "unit": "kg",
                "unit_price": 2500.0
            }
        ],
        "required_delivery_date": "2024-02-01"
    }
    
    # Create purchase order
    response = await client.post(f"{api_prefix}/purchase-orders/", json=order_data)
    if response.status_code == 201:
        order = response.json()
        yield order
        
        # Cleanup: Cancel order
        try:
            order_id = order.get("_id")
            if order_id:
                cancel_data = {"reason": "Test cleanup"}
                await client.post(f"{api_prefix}/purchase-orders/{order_id}/cancel", json=cancel_data)
        except Exception:
            pass  # Ignore cleanup errors
    else:
        # If we can't create the order, yield None and let tests handle it
        yield None


@pytest.fixture
async def test_inventory_batch(client: httpx.AsyncClient, api_prefix: str, test_product):
    """Create inventory by receiving product and return the batch info"""
    product_id = test_product.get("_id")
    
    receipt_data = {
        "product_id": product_id,
        "institution_id": 1,
        "storage_location": "test-warehouse",
        "quantity_received": 100.0,
        "unit_of_measure": "kg",
        "expiration_date": "2024-12-31",
        "batch_number": f"TEST-BATCH-{ObjectId()}",
        "received_by": "test_manager",
        "reception_date": "2024-01-15T08:30:00Z",
        "notes": "Test inventory setup"
    }
    
    # Create inventory by receiving
    response = await client.post(f"{api_prefix}/inventory-movements/receive-inventory", json=receipt_data)
    if response.status_code == 201:
        receipt_result = response.json()
        # Use inventory_id from the response (API returns inventory_id, not inventory_batch_id)
        inventory_id = receipt_result.get("inventory_id") or receipt_result.get("inventory_batch_id")
        yield {
            "inventory_batch_id": inventory_id,
            "inventory_id": inventory_id,  # Also provide both names for clarity
            "product_id": product_id,
            "institution_id": 1,
            "batch_number": receipt_data["batch_number"]
        }
    else:
        yield None


@pytest.fixture
def sample_inventory_receipt_data(test_product, test_purchase_order):
    """Sample inventory receipt data with valid ObjectIds"""
    product_id = test_product.get("_id")
    purchase_order_id = None
    if test_purchase_order:
        purchase_order_id = test_purchase_order.get("_id")
    
    return {
        "product_id": product_id,
        "institution_id": 1,
        "storage_location": "test-warehouse",
        "quantity_received": 25.5,
        "unit_of_measure": "kg",
        "expiration_date": "2024-06-15",
        "batch_number": f"TEST-BATCH-{ObjectId()}",
        "purchase_order_id": purchase_order_id,
        "received_by": "test_manager",
        "reception_date": "2024-01-15T08:30:00Z",
        "notes": "Test inventory receipt"
    }


@pytest.fixture
def sample_inventory_consumption_data(test_product):
    """Sample inventory consumption data with valid ObjectIds"""
    product_id = test_product.get("_id")
    
    return {
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


@pytest.fixture
def sample_inventory_adjustment_data(test_product, test_inventory_batch):
    """Sample inventory adjustment data with valid ObjectIds"""
    product_id = test_product.get("_id")
    inventory_id = None
    if test_inventory_batch:
        inventory_id = test_inventory_batch.get("inventory_batch_id")
    
    return {
        "product_id": product_id,
        "inventory_id": inventory_id or str(ObjectId()),  # Use valid ObjectId even if batch creation failed
        "quantity": 5.0,
        "unit": "kg",
        "reason": "Test adjustment",
        "notes": "Test inventory adjustment",
        "adjusted_by": "test_auditor"
    }


@pytest.fixture
def non_existent_product_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


@pytest.fixture
def non_existent_inventory_id():
    """Generate a valid but non-existent ObjectId for testing"""
    return str(ObjectId())


# Legacy fixtures for backward compatibility - generate fresh ObjectIds each time
@pytest.fixture
def sample_provider_data():
    """Sample provider data for testing"""
    return {
        "name": "Test Provider Legacy",
        "nit": "900123456-8",
        "address": "Legacy Test Address",
        "responsible_name": "Legacy Manager",
        "email": "legacy@provider.com",
        "phone_number": "3001234567",
        "is_local_provider": True
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "provider_id": str(ObjectId()),  # Will need to be replaced with real provider ID
        "name": "Legacy Test Product",
        "weight": 1.0,
        "weekly_availability": "MONDAY",
        "life_time": {"value": 30, "unit": "days"}
    }


@pytest.fixture
def sample_purchase_order_data():
    """Sample purchase order data for testing"""
    return {
        "provider_id": str(ObjectId()),
        "items": [
            {
                "product_id": str(ObjectId()),
                "quantity": 50.0,
                "unit": "kg",
                "unit_price": 2500.0
            }
        ],
        "required_delivery_date": "2024-02-01"
    }


@pytest.fixture
def sample_ingredient_receipt_data():
    """Sample ingredient receipt data for testing"""
    return {
        "institution_id": 1,
        "purchase_order_id": str(ObjectId()),
        "receipt_date": "2024-01-15",
        "delivery_person_name": "Test Delivery Person",
        "items": [
            {
                "product_id": str(ObjectId()),
                "quantity": 25.0,
                "unit": "kg",
                "storage_location": "test-warehouse",
                "lot": "TEST-LOT-001",
                "expiration_date": "2024-06-15"
            }
        ]
    }


@pytest.fixture
def sample_purchase_calculation_data():
    """Sample purchase calculation data for testing"""
    return {
        "start_date": "2024-02-01",
        "end_date": "2024-02-07",
        "coverage": {
            "type": "municipality",
            "ids": [1, 2, 3]
        }
    }


@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return TestConfig


# Helper functions for common assertions
def assert_response_has_id(data: Dict[str, Any]) -> str:
    """Assert response has an ID field and return it"""
    # The API returns _id field, not id field as expected from the response model
    assert "_id" in data, "Response should contain an _id field"
    id_value = data.get("_id")
    assert id_value is not None, "ID field should not be None"
    return str(id_value)


def assert_pagination_response(data: Dict[str, Any], expected_items_key: str = "items"):
    """Assert response has pagination structure"""
    assert expected_items_key in data, f"Response should contain {expected_items_key}"
    assert "page_info" in data, "Response should contain page_info"
    
    page_info = data["page_info"]
    assert "current_page" in page_info
    assert "page_size" in page_info
    assert "has_next" in page_info
    assert "has_previous" in page_info


def assert_error_response(data: Dict[str, Any], expected_message: Optional[str] = None):
    """Assert response is an error with detail field"""
    assert "detail" in data, "Error response should contain detail field"
    if expected_message is not None:
        assert expected_message in str(data["detail"]), f"Expected '{expected_message}' in error message"


# Export helper functions
__all__ = [
    "assert_response_has_id",
    "assert_pagination_response", 
    "assert_error_response"
] 