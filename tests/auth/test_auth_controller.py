"""
Integration tests for Authentication Controller Endpoints
Test cases: AUTH-004 to AUTH-009
"""
import pytest
import httpx
import time

from ..config import settings
from ..test_metadata import add_test_info

# Helper to create unique user data for each test run
def unique_user_data(suffix: str):
    timestamp = int(time.time())
    return {
        "email": f"newuser_{timestamp}_{suffix}@example.com",
        "full_name": "New User Test",
        "username": f"newusertest_{timestamp}_{suffix}",
        "password": "NewPassword123!",
        "phone_number": "+1234567890"
    }


@add_test_info(
    description="Crear un usuario exitosamente",
    expected_result="Status Code: 201, datos del usuario creado",
    module="Autenticación",
    test_id="AUTH-004"
)
async def test_register_success():
    """Test successful user registration"""
    user_data = unique_user_data("register_success")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["username"] == user_data["username"]
    assert "id" in data


@add_test_info(
    description="Fallar al registrar con un email duplicado",
    expected_result="Status Code: 400, error de email ya registrado",
    module="Autenticación",
    test_id="AUTH-005"
)
async def test_register_duplicate_email():
    """Test registration with duplicate email should return 400"""
    user_data = {
        "email": settings.ADMIN_USER_EMAIL,  # This email already exists
        "full_name": "Another Admin",
        "password": "Password123!"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@add_test_info(
    description="Cambiar la contraseña exitosamente",
    expected_result="Status Code: 200, mensaje de éxito",
    module="Autenticación",
    test_id="AUTH-006"
)
async def test_change_password_success():
    """Test successful password change with valid authentication"""
    original_password = settings.BASE_USER_PASSWORD
    new_password = "NewPassword456!"
    
    async with httpx.AsyncClient() as client:
        # 1. Login with original password to get token
        login_data = {"email": settings.BASE_USER_EMAIL, "password": original_password}
        login_response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data)
        assert login_response.status_code == 200, "Login failed before password change"
        token = login_response.json()["access_token"]
        
        # 2. Change password to new password
        password_data = {
            "old_password": original_password,
            "new_password": new_password
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
        
        # 3. Cleanup: Change password back to original
        try:
            # 3a. Login with the NEW password to get a new token
            new_login_data = {"email": settings.BASE_USER_EMAIL, "password": new_password}
            new_login_response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=new_login_data)
            assert new_login_response.status_code == 200, "Login with new password failed during cleanup"
            new_token = new_login_response.json()["access_token"]
            
            # 3b. Change password back to original
            cleanup_password_data = {
                "old_password": new_password,
                "new_password": original_password
            }
            cleanup_headers = {"Authorization": f"Bearer {new_token}"}
            cleanup_response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/change-password", json=cleanup_password_data, headers=cleanup_headers)
            assert cleanup_response.status_code == 200, "Failed to change password back during cleanup"
        except Exception as e:
            pytest.fail(f"Password change cleanup failed: {e}. The password for {settings.BASE_USER_EMAIL} may be incorrect for subsequent tests.")


@add_test_info(
    description="Fallar al cambiar contraseña con contraseña antigua incorrecta",
    expected_result="Status Code: 400, error de contraseña incorrecta",
    module="Autenticación",
    test_id="AUTH-007"
)
async def test_change_password_wrong_old_password():
    """Test password change with incorrect old password should return 400"""
    async with httpx.AsyncClient() as client:
        # Login to get token
        login_data = {"email": settings.BASE_USER_EMAIL, "password": settings.BASE_USER_PASSWORD}
        login_response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Try to change password with wrong old password
        password_data = {
            "old_password": "WrongOldPassword",
            "new_password": "NewPassword456!"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 400
        assert "Incorrect old password" in response.json()["detail"]


@add_test_info(
    description="Solicitar reinicio de contraseña para email existente",
    expected_result="Status Code: 200, mensaje de éxito genérico",
    module="Autenticación",
    test_id="AUTH-008"
)
async def test_forgot_password_success():
    """Test forgot password endpoint (always returns success for security)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/forgot-password", params={"email": settings.ADMIN_USER_EMAIL})
    
    assert response.status_code == 200
    assert "If the email exists, you will receive password reset instructions" in response.json()["message"]


@add_test_info(
    description="Solicitar reinicio de contraseña para email no existente",
    expected_result="Status Code: 200, mensaje de éxito genérico",
    module="Autenticación",
    test_id="AUTH-009"
)
async def test_forgot_password_nonexistent_email():
    """Test forgot password with non-existent email (should still return success for security)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/forgot-password", params={"email": "nonexistent.user.test@example.com"})
    
    assert response.status_code == 200
    assert "If the email exists, you will receive password reset instructions" in response.json()["message"] 