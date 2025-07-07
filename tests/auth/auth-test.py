import requests
import pytest
from ..config import settings

def test_root():
    response = requests.get(f"{settings.BASE_AUTH_BACKEND_URL}/", timeout=5)
    assert response.status_code == 200

def test_login_success():
    """
    Test successful login with valid credentials
    """
    login_data = {"email": settings.ADMIN_USER_EMAIL, "password": settings.ADMIN_USER_PASSWORD}
    
    response = requests.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data, timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """
    Test login with invalid credentials should return 401
    """
    login_data = {"email": settings.ADMIN_USER_EMAIL, "password": "wrong_password"}
    
    response = requests.post(f"{settings.BASE_AUTH_BACKEND_URL}/auth/login", json=login_data, timeout=5)
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]