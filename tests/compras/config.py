"""
Shared configuration for PAE Compras API integration tests
"""
import os
from typing import Optional

from ..config import settings


class TestConfig:
    """Configuration class for API tests"""
    
    # API Configuration
    BASE_URL: str = settings.BASE_COMPRAS_BACKEND_URL
    API_PREFIX: str = "/api/v1"
    TIMEOUT: float = 30.0
    FOLLOW_REDIRECTS: bool = True
    FULL_URL: str = f"{BASE_URL}{API_PREFIX}"
    
    # Environment Detection
    ENVIRONMENT: str = os.getenv("TEST_ENV", "local")
    
    # Test Data Configuration
    USE_REAL_DATA: bool = os.getenv("USE_REAL_DATA", "false").lower() == "true"
    
    @classmethod
    def get_full_url(cls, endpoint: str) -> str:
        """Get full URL for an endpoint"""
        return f"{cls.BASE_URL}{cls.API_PREFIX}{endpoint}"
    
    @classmethod
    def is_local(cls) -> bool:
        """Check if running against local environment"""
        return cls.ENVIRONMENT == "local"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running against production environment"""
        return cls.ENVIRONMENT == "production"


# Sample data fixtures
SAMPLE_PROVIDER_DATA = {
    "name": "Proveedor Test ABC",
    "nit": "900123456-7",
    "address": "Calle 123 # 45-67",
    "responsible_name": "Juan Pérez",
    "email": "juan@proveedor.com",
    "phone_number": "3001234567",
    "is_local_provider": True
}

SAMPLE_PRODUCT_DATA = {
    "provider_id": "687337294a1672992ce8b352",
    "name": "Arroz Blanco Test",
    "weight": 1.0,
    "weekly_availability": "MONDAY",
    "life_time": {"value": 30, "unit": "days"}
}

SAMPLE_PURCHASE_ORDER_DATA = {
    "provider_id": "687337294a1672992ce8b352",
    "items": [
        {
            "product_id": "6873372e4a1672992ce8b353",
            "quantity": 50.0,
            "unit": "kg",
            "unit_price": 2500.0
        }
    ],
    "required_delivery_date": "2024-02-01"
}

SAMPLE_INVENTORY_RECEIPT_DATA = {
    "product_id": "6873372e4a1672992ce8b353",
    "institution_id": 1,
    "storage_location": "warehouse-01",
    "quantity_received": 25.5,
    "unit_of_measure": "kg",
    "expiration_date": "2024-06-15",
    "batch_number": "BATCH-2024-001",
    "purchase_order_id": "PO-2024-123",
    "received_by": "warehouse_manager",
    "reception_date": "2024-01-15T08:30:00Z",
    "notes": "Fresh delivery"
}

SAMPLE_INVENTORY_CONSUMPTION_DATA = {
    "product_id": "6873372e4a1672992ce8b353",
    "institution_id": 1,
    "storage_location": "warehouse-01",
    "quantity": 5.5,
    "unit": "kg",
    "consumption_date": "2024-01-15T10:30:00Z",
    "reason": "menu preparation",
    "notes": "Used for lunch menu",
    "consumed_by": "chef_maria"
}

SAMPLE_INVENTORY_ADJUSTMENT_DATA = {
    "product_id": "6873372e4a1672992ce8b353",
    "inventory_id": "648f8f8f8f8f8f8f8f8f8f8a",
    "quantity": 5.0,
    "unit": "kg",
    "reason": "Physical count found more stock",
    "notes": "Monthly audit correction",
    "adjusted_by": "auditor_maria"
} 

SAMPLE_INGREDIENT_RECEIPT_DATA = {
    "institution_id": 1,
    "purchase_order_id": "687337294a1672992ce8b352",
    "receipt_date": "2024-01-15",
    "delivery_person_name": "Juan Pérez",
    "items": [
        {
            "product_id": "6873372e4a1672992ce8b353",
            "quantity": 25.0,
            "unit": "kg",
            "storage_location": "warehouse-01",
            "lot": "LOT-2024-001",
            "expiration_date": "2024-06-15"
        }
    ]
} 

SAMPLE_PURCHASE_CALCULATION_DATA = {
    "start_date": "2024-02-01",
    "end_date": "2024-02-07",
    "coverage": {
        "type": "municipality",
        "ids": [1, 2, 3]
    }
} 