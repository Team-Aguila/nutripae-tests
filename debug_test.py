import httpx
import asyncio
import sys
import os

# Add the tests directory to Python path
sys.path.append('tests')

from tests.config import settings
from tests.conftest import *

async def test_ingredient_creation():
    """Debug test to see what's happening with ingredient creation"""
    
    # Get auth token
    login_data = {
        "email": settings.ADMIN_USER_EMAIL,
        "password": settings.ADMIN_USER_PASSWORD,
    }
    
    async with httpx.AsyncClient() as client:
        # Login
        print("🔐 Logging in...")
        response = await client.post(
            f"{settings.BASE_AUTH_BACKEND_URL}/auth/login",
            json=login_data,
            timeout=20
        )
        print(f"Login response: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
            
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Got token: {token[:20]}...")
        
        # Test ingredient creation
        headers = {"Authorization": f"Bearer {token}"}
        base_url = settings.BASE_MENUS_BACKEND_URL
        api_prefix = "/api/v1"
        
        # Use exact format that worked for user
        ingredient_data = {
            "name": "Test Tomate Roma",
            "base_unit_of_measure": "kg",
            "status": "active", 
            "description": "Test tomate Roma fresco para ensaladas y salsas",
            "category": "vegetables"
        }
        
        url = f"{base_url}{api_prefix}/ingredients/"
        print(f"🌐 Sending POST to: {url}")
        print(f"📦 Data: {ingredient_data}")
        print(f"🔑 Headers: {headers}")
        
        response = await client.post(url, json=ingredient_data, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("🎉 SUCCESS! Ingredient created!")
        else:
            print("❌ FAILED!")

if __name__ == "__main__":
    asyncio.run(test_ingredient_creation()) 