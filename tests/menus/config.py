"""
Shared configuration for PAE Menus API integration tests
"""
import os
from typing import Optional

class TestConfig:
    """Configuration class for API tests"""
    
    # API Configuration
    BASE_URL: str = os.getenv("PAE_MENUS_BASE_URL", "http://127.0.0.1:8001")
    API_PREFIX: str = "/api/v1"
    TIMEOUT: float = 30.0
    FOLLOW_REDIRECTS: bool = True
    
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


# Sample data fixtures for ingredients
SAMPLE_INGREDIENT_DATA = {
    "name": "Arroz Blanco Test",
    "base_unit_of_measure": "kg",
    "status": "active",
    "description": "Arroz blanco de grano largo para preparaciones",
    "category": "cereales",
    "nutritional_info": {
        "per_100g": {
            "calories": 365.0,
            "protein": 7.1,
            "carbohydrates": 78.9,
            "fat": 0.7,
            "fiber": 1.3,
            "sodium": 5.0
        }
    }
}

SAMPLE_INGREDIENT_UPDATE_DATA = {
    "name": "Arroz Blanco Premium Test",
    "description": "Arroz blanco premium de grano largo",
    "category": "cereales_premium"
}

# Sample data fixtures for dishes
SAMPLE_DISH_DATA = {
    "name": "Arroz con Pollo Test",
    "description": "Plato principal con arroz y pollo",
    "status": "active",
    "compatible_meal_types": ["almuerzo"],  # Use Spanish values
    "recipe": {
        "ingredients": []  # Will be filled with actual Portion objects
    },
    "nutritional_info": {
        "calories": 520.0,
        "protein": 25.0,
        "carbohydrates": 65.0,
        "fat": 12.0,
        "fiber": 2.5,
        "sodium": 180.0,
        "photo_url": "https://example.com/arroz-con-pollo.jpg"
    },
    "dish_type": "protein"
}

SAMPLE_DISH_UPDATE_DATA = {
    "name": "Arroz con Pollo Premium Test",
    "description": "Plato principal premium con arroz y pollo orgánico",
    "compatible_meal_types": ["almuerzo", "refrigerio"]  # Use Spanish values
}

# Sample data fixtures for menu cycles
SAMPLE_MENU_CYCLE_DATA = {
    "name": "Ciclo Semanal Test",
    "description": "Ciclo de menús semanal para pruebas",
    "status": "active",
    "duration_days": 7,
    "daily_menus": []  # Will be filled with actual DailyMenu objects
}

SAMPLE_MENU_CYCLE_UPDATE_DATA = {
    "name": "Ciclo Semanal Premium Test",
    "description": "Ciclo de menús semanal premium para pruebas",
    "status": "active"
}

# Sample data fixtures for menu schedules (assignment request)
SAMPLE_MENU_SCHEDULE_ASSIGNMENT_DATA = {
    "menu_cycle_id": None,  # Will be filled with actual cycle ID (string)
    "campus_ids": ["campus_1", "campus_2"],
    "town_ids": ["town_1"],
    "start_date": "2024-02-01",
    "end_date": "2024-02-28"
}

SAMPLE_MENU_SCHEDULE_UPDATE_DATA = {
    "name": "Horario Premium Test Institución 1",
    "status": "active",
    "nutritional_targets": {
        "daily_calories": 2200.0,
        "daily_protein": 70.0,
        "daily_carbohydrates": 275.0,
        "daily_fat": 70.0
    }
}

# Sample portion data for recipes
SAMPLE_PORTION = {
    "ingredient_id": None,  # Will be filled with actual ingredient ID (PydanticObjectId)
    "quantity": 200.0,
    "unit": "g"
}

# Sample nutritional analysis data
SAMPLE_NUTRITIONAL_ANALYSIS_DATA = {
    "analysis_type": "menu_cycle",
    "target_id": None,  # Will be filled with actual menu cycle ID
    "period_start": "2024-02-01",
    "period_end": "2024-02-07",
    "institution_id": 1,
    "analysis_parameters": {
        "age_group": "school_age",
        "target_population": 100,
        "dietary_restrictions": []
    }
}

# Invalid data samples for validation testing
INVALID_INGREDIENT_DATA = {
    "missing_name": {
        "base_unit_of_measure": "kg",
        "status": "active"
    },
    "empty_name": {
        "name": "",
        "base_unit_of_measure": "kg"
    },
    "invalid_status": {
        "name": "Invalid Status Test",
        "base_unit_of_measure": "kg",
        "status": "invalid_status"
    },
    "missing_unit": {
        "name": "Missing Unit Test",
        "status": "active"
    }
}

INVALID_DISH_DATA = {
    "missing_name": {
        "compatible_meal_types": ["almuerzo"],
        "recipe": {"ingredients": []}
    },
    "empty_meal_types": {
        "name": "Empty Meal Types Test",
        "compatible_meal_types": [],
        "recipe": {"ingredients": []}
    },
    "invalid_meal_type": {
        "name": "Invalid Meal Type Test",
        "compatible_meal_types": ["invalid_meal"],
        "recipe": {"ingredients": []}
    },
    "missing_recipe": {
        "name": "Missing Recipe Test",
        "compatible_meal_types": ["almuerzo"]
    }
} 