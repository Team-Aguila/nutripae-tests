import pytest
import json
import asyncio
import httpx

from tests.test_metadata import MetadataRegistry
from tests.config import settings


# Hook to write metadata to file at the end of the test session
def pytest_sessionfinish(session):
    """
    Hook para escribir la metadata en un archivo al final de la sesión de tests.
    """
    registry = MetadataRegistry()
    registry_data = registry.get_all_tests()
    
    # Store metadata in a file
    with open("test_metadata_registry.json", "w") as f:
        json.dump(registry_data, f, indent=4)

@pytest.fixture(scope="session")
def event_loop():
    """Force the event_loop fixture to be session-scoped."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def auth_token():
    """Logs in and retrieves an authentication token for the session."""
    login_data = {
        "email": settings.ADMIN_USER_EMAIL,
        "password": settings.ADMIN_USER_PASSWORD,
    }
    async with httpx.AsyncClient() as client:
        try:
            # The URL for login does not need the /api/v1 prefix as it's included in BASE_AUTH_BACKEND_URL
            response = await client.post(
                f"{settings.BASE_AUTH_BACKEND_URL}/auth/login",
                json=login_data,
                timeout=20, # Increased timeout for login
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            token_data = response.json()
            if "access_token" not in token_data:
                pytest.fail("'access_token' not found in login response.")
            return token_data["access_token"]
        except (httpx.RequestError, KeyError) as e:
            pytest.fail(f"Authentication failed: Could not retrieve auth token. Error: {e}")
        except httpx.HTTPStatusError as e:
            pytest.fail(f"Authentication failed with status {e.response.status_code}: {e.response.text}")

# Import fixtures from other conftest files to make them available globally if needed
# Example: from tests.menus.conftest import some_fixture 