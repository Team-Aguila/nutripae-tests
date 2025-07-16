import os

from ..config import settings


class TestConfig:
    """Configuration class for UI tests"""

    # API Configuration
    BASE_FRONTEND_URL: str = settings.BASE_FRONTEND_URL or os.getenv(
        "BASE_FRONTEND_URL", "http://localhost:5173"
    )
    ADMIN_USER_EMAIL: str = settings.ADMIN_USER_EMAIL or os.getenv(
        "ADMIN_USER_EMAIL", "admin@test.com"
    )
    ADMIN_USER_PASSWORD: str = settings.ADMIN_USER_PASSWORD or os.getenv(
        "ADMIN_USER_PASSWORD", "Password123!"
    )