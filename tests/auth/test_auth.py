import requests
import pytest
from ..config import settings
from ..test_metadata import add_test_info

@add_test_info(
    description="Verificar que el endpoint raíz responda correctamente",
    expected_result="Status Code: 200",
    module="Autenticación",
    test_id="AUTH-001"
)
def test_root():
    """Test del endpoint raíz del servicio de autenticación"""
    response = requests.get(f"{settings.BASE_AUTH_BACKEND_URL}/", timeout=5)
    assert response.status_code == 200

@add_test_info(
    description="Verificar login exitoso con credenciales válidas",
    expected_result="Status Code: 200, Access Token, Token Type Bearer",
    module="Autenticación",
    test_id="AUTH-002"
)
def test_login_success():
    """Test de login exitoso con credenciales administrativas válidas"""
    login_data = {"email": settings.ADMIN_USER_EMAIL, "password": settings.ADMIN_USER_PASSWORD}
    
    response = requests.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data, timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@add_test_info(
    description="Verificar login fallido con credenciales inválidas",
    expected_result="Status Code: 401, Error de credenciales incorrectas",
    module="Autenticación",
    test_id="AUTH-003"
)
def test_login_invalid_credentials():
    """Test de login fallido con credenciales incorrectas"""
    login_data = {"email": settings.ADMIN_USER_EMAIL, "password": "wrong_password"}
    
    response = requests.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data, timeout=5)
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]