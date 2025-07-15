"""
Integration tests for Providers API
Test cases: PRV-001 to PRV-022
"""
import pytest
import httpx
from typing import Dict, Any

from .conftest import assert_response_has_id, assert_pagination_response, assert_error_response
from ..test_metadata import add_test_info


class TestProvidersAPI:
    """Test suite for Providers API endpoints"""
    
    # CREATE PROVIDER TESTS
    
    @add_test_info(
        description="Crear un proveedor exitosamente con todos los campos requeridos",
        expected_result="Status Code: 201, datos del proveedor creado",
        module="Compras",
        test_id="PRV-001"
    )
    async def test_create_provider_success(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-001: Successfully create a new provider"""
        provider_data = {
            "name": "Test Provider PRV-001",
            "nit": "900999001-1",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test001@provider.com",
            "phone_number": "3009998001",
            "is_local_provider": True
        }
        
        response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        
        assert response.status_code == 201
        data = response.json()
        provider_id = assert_response_has_id(data)
        assert data["name"] == provider_data["name"]
        assert data["nit"] == provider_data["nit"]
        assert data["address"] == provider_data["address"]
        assert data["responsible_name"] == provider_data["responsible_name"]
        assert data["email"] == provider_data["email"]
        assert data["phone_number"] == provider_data["phone_number"]
        assert data["is_local_provider"] == provider_data["is_local_provider"]
        assert "created_at" in data
        assert "updated_at" in data
        assert data.get("deleted_at") is None
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider_id}")

    @add_test_info(
        description="Fallar al crear proveedor con campos requeridos faltantes",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="PRV-002"
    )
    async def test_create_provider_missing_required_fields(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-002: Fail to create provider with missing required fields"""
        invalid_data = {
            "name": "Proveedor ABC",
            "address": "Calle 123"
        }
        
        response = await client.post(f"{api_prefix}/providers/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about the missing 'nit' field
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("nit" in str(error) for error in data["detail"])

    @add_test_info(
        description="Fallar al crear proveedor con email inválido",
        expected_result="Status Code: 422, error de validación de email",
        module="Compras",
        test_id="PRV-003"
    )
    async def test_create_provider_invalid_email(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-003: Fail to create provider with invalid email format"""
        invalid_data = {
            "name": "Proveedor ABC",
            "nit": "900123456-3",
            "address": "Calle 123",
            "responsible_name": "Juan",
            "email": "invalid_email",
            "phone_number": "3001234567"
        }
        
        response = await client.post(f"{api_prefix}/providers/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about the invalid email field
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("email" in str(error) for error in data["detail"])

    @add_test_info(
        description="Fallar al crear proveedor con NIT duplicado",
        expected_result="Status Code: 400, error de conflicto",
        module="Compras",
        test_id="PRV-004"
    )
    async def test_create_provider_duplicate_nit(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-004: Fail to create provider with duplicate NIT"""
        provider_data = {
            "name": "Proveedor Original",
            "nit": "900123456-4",
            "address": "Calle 123",
            "responsible_name": "Juan",
            "email": "juan@proveedor.com",
            "phone_number": "3001234567"
        }
        
        # First create a provider
        response1 = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert response1.status_code == 201
        provider1_id = assert_response_has_id(response1.json())
        
        # Now try to create another provider with the same NIT
        duplicate_data = {
            "name": "Proveedor Duplicado",
            "nit": provider_data["nit"],  # Use the same NIT
            "address": "Calle 456",
            "responsible_name": "Maria",
            "email": "maria@proveedor.com",
            "phone_number": "3007654321"
        }
        
        response2 = await client.post(f"{api_prefix}/providers/", json=duplicate_data)
        
        # Should fail with 409 Conflict due to duplicate NIT
        assert response2.status_code == 409
        error_data = response2.json()
        assert_error_response(error_data, expected_message="Provider with NIT '900123456-4' already exists")
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider1_id}")

    @add_test_info(
        description="Fallar al crear proveedor con nombre vacío",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="PRV-005"
    )
    async def test_create_provider_empty_name(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-005: Fail to create provider with empty name"""
        invalid_data = {
            "name": "",
            "nit": "900123456-5",
            "address": "Calle 123",
            "responsible_name": "Juan",
            "email": "juan@proveedor5.com",
            "phone_number": "3001234567"
        }
        
        response = await client.post(f"{api_prefix}/providers/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        # Check that the error details contain information about the invalid name field
        assert "detail" in data
        assert isinstance(data["detail"], list)
        assert any("name" in str(error) for error in data["detail"])

    # READ PROVIDER TESTS
    
    @add_test_info(
        description="Obtener proveedor por ID exitosamente",
        expected_result="Status Code: 200, datos completos del proveedor",
        module="Compras",
        test_id="PRV-006"
    )
    async def test_get_provider_by_id_success(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-006: Successfully get provider by ID"""
        provider_data = {
            "name": "Test Provider PRV-006",
            "nit": "900123456-6",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test006@provider.com",
            "phone_number": "3009998006"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        created_provider = create_response.json()
        provider_id = assert_response_has_id(created_provider)
        
        # Now get the provider by ID
        response = await client.get(f"{api_prefix}/providers/{provider_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert_response_has_id(data)
        assert data["name"] == provider_data["name"]
        assert data["nit"] == provider_data["nit"]
        assert data["address"] == provider_data["address"]
        assert data["responsible_name"] == provider_data["responsible_name"]
        assert data["email"] == provider_data["email"]
        assert data["phone_number"] == provider_data["phone_number"]
        assert "is_local_provider" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider_id}")

    @add_test_info(
        description="Fallar al obtener proveedor con ID en formato inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="PRV-007"
    )
    async def test_get_provider_by_id_invalid_format(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-007: Fail to get provider with invalid ID format"""
        response = await client.get(f"{api_prefix}/providers/invalid_id")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al obtener proveedor que no existe",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-008"
    )
    async def test_get_provider_by_id_not_found(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-008: Fail to get provider that doesn't exist"""
        response = await client.get(f"{api_prefix}/providers/648f8f8f8f8f8f8f8f8f8f8a")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al obtener proveedor eliminado (soft delete)",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-009"
    )
    async def test_get_provider_soft_deleted(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-009: Fail to get soft-deleted provider"""
        provider_data = {
            "name": "Test Provider PRV-009",
            "nit": "900123456-9",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test009@provider.com",
            "phone_number": "3009998009"
        }
        
        # Create provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        provider_id = assert_response_has_id(create_response.json())
        
        # Delete provider (soft delete)
        delete_response = await client.delete(f"{api_prefix}/providers/{provider_id}")
        assert delete_response.status_code == 204
        
        # Try to retrieve deleted provider
        response = await client.get(f"{api_prefix}/providers/{provider_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    # LIST PROVIDERS TESTS
    
    @add_test_info(
        description="Obtener lista de proveedores con paginación por defecto",
        expected_result="Status Code: 200, lista paginada de proveedores",
        module="Compras",
        test_id="PRV-010"
    )
    async def test_get_providers_list_default_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-010: Successfully get providers list with default pagination"""
        response = await client.get(f"{api_prefix}/providers/")
        
        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data, "providers")
        assert "total_count" in data
        assert isinstance(data["providers"], list)

    @add_test_info(
        description="Obtener lista de proveedores filtrada por proveedores locales",
        expected_result="Status Code: 200, lista filtrada de proveedores",
        module="Compras",
        test_id="PRV-011"
    )
    async def test_get_providers_list_local_filter(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-011: Successfully get providers list with local filter"""
        response = await client.get(f"{api_prefix}/providers/", params={"is_local_provider": True})
        
        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data, "providers")
        # All returned providers should be local
        for provider in data["providers"]:
            assert provider["is_local_provider"] is True

    @add_test_info(
        description="Obtener lista de proveedores con parámetros de paginación personalizados",
        expected_result="Status Code: 200, lista paginada según parámetros",
        module="Compras",
        test_id="PRV-012"
    )
    async def test_get_providers_list_with_pagination(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-012: Successfully get providers list with custom pagination"""
        response = await client.get(f"{api_prefix}/providers/", params={"skip": 0, "limit": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert_pagination_response(data, "providers")
        assert len(data["providers"]) <= 5
        assert data["page_info"]["page_size"] == 5

    @add_test_info(
        description="Fallar al obtener lista de proveedores con límite inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="PRV-013"
    )
    async def test_get_providers_list_invalid_limit(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-013: Fail to get providers list with invalid limit"""
        response = await client.get(f"{api_prefix}/providers/", params={"limit": 1001})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    @add_test_info(
        description="Fallar al obtener lista de proveedores con skip inválido",
        expected_result="Status Code: 422, error de validación",
        module="Compras",
        test_id="PRV-014"
    )
    async def test_get_providers_list_invalid_skip(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-014: Fail to get providers list with invalid skip"""
        response = await client.get(f"{api_prefix}/providers/", params={"skip": -1})
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)

    # UPDATE PROVIDER TESTS
    
    @add_test_info(
        description="Actualizar nombre de proveedor exitosamente",
        expected_result="Status Code: 200, datos del proveedor actualizado",
        module="Compras",
        test_id="PRV-015"
    )
    async def test_update_provider_name_success(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-015: Successfully update provider name"""
        provider_data = {
            "name": "Original Provider PRV-015",
            "nit": "900123456-15",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test015@provider.com",
            "phone_number": "3009998015"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        created_provider = create_response.json()
        provider_id = assert_response_has_id(created_provider)
        
        # Now update the provider
        update_data = {"name": "Updated Provider Name PRV-015"}
        response = await client.put(f"{api_prefix}/providers/{provider_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert_response_has_id(data)
        assert data["name"] == "Updated Provider Name PRV-015"
        assert "updated_at" in data
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider_id}")

    @add_test_info(
        description="Actualizar múltiples campos de proveedor exitosamente",
        expected_result="Status Code: 200, datos del proveedor con cambios",
        module="Compras",
        test_id="PRV-016"
    )
    async def test_update_provider_multiple_fields_success(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-016: Successfully update multiple provider fields"""
        provider_data = {
            "name": "Original Provider PRV-016",
            "nit": "900123456-16",
            "address": "Original Address",
            "responsible_name": "Original Manager",
            "email": "original016@provider.com",
            "phone_number": "3009998016"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        created_provider = create_response.json()
        provider_id = assert_response_has_id(created_provider)
        
        # Now update the provider with multiple fields
        update_data = {
            "name": "New Name PRV-016",
            "address": "New Address PRV-016",
            "email": "new016@provider.com"
        }
        response = await client.put(f"{api_prefix}/providers/{provider_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert_response_has_id(data)
        assert data["name"] == "New Name PRV-016"
        assert data["address"] == "New Address PRV-016"
        assert data["email"] == "new016@provider.com"
        assert "updated_at" in data
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider_id}")

    @add_test_info(
        description="Fallar al actualizar proveedor que no existe",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-017"
    )
    async def test_update_provider_not_found(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-017: Fail to update provider that doesn't exist"""
        update_data = {"name": "Updated Name"}
        response = await client.put(f"{api_prefix}/providers/648f8f8f8f8f8f8f8f8f8f8a", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al actualizar proveedor con email inválido",
        expected_result="Status Code: 422, error de validación de email",
        module="Compras",
        test_id="PRV-018"
    )
    async def test_update_provider_invalid_email(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-018: Fail to update provider with invalid email"""
        provider_data = {
            "name": "Test Provider PRV-018",
            "nit": "900123456-18",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test018@provider.com",
            "phone_number": "3009998018"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        provider_id = assert_response_has_id(create_response.json())
        
        # Try to update with invalid email
        update_data = {"email": "invalid_email"}
        response = await client.put(f"{api_prefix}/providers/{provider_id}", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data)
        
        # Cleanup
        await client.delete(f"{api_prefix}/providers/{provider_id}")

    @add_test_info(
        description="Fallar al actualizar proveedor eliminado (soft delete)",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-019"
    )
    async def test_update_provider_soft_deleted(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-019: Fail to update soft-deleted provider"""
        provider_data = {
            "name": "Test Provider PRV-019",
            "nit": "900123456-19",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test019@provider.com",
            "phone_number": "3009998019"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        provider_id = assert_response_has_id(create_response.json())
        
        # Delete the provider (soft delete)
        delete_response = await client.delete(f"{api_prefix}/providers/{provider_id}")
        assert delete_response.status_code == 204
        
        # Try to update the deleted provider
        update_data = {"name": "Updated Name"}
        response = await client.put(f"{api_prefix}/providers/{provider_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    # DELETE PROVIDER TESTS
    
    @add_test_info(
        description="Eliminar proveedor exitosamente (soft delete)",
        expected_result="Status Code: 200, confirmación de eliminación",
        module="Compras",
        test_id="PRV-020"
    )
    async def test_delete_provider_success(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-020: Successfully delete provider (soft delete)"""
        provider_data = {
            "name": "Test Provider PRV-020",
            "nit": "900123456-20",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test020@provider.com",
            "phone_number": "3009998020"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        created_provider = create_response.json()
        provider_id = assert_response_has_id(created_provider)
        
        # Now delete the provider
        response = await client.delete(f"{api_prefix}/providers/{provider_id}")
        
        assert response.status_code == 204

    @add_test_info(
        description="Fallar al eliminar proveedor que no existe",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-021"
    )
    async def test_delete_provider_not_found(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-021: Fail to delete provider that doesn't exist"""
        response = await client.delete(f"{api_prefix}/providers/648f8f8f8f8f8f8f8f8f8f8a")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found")

    @add_test_info(
        description="Fallar al eliminar proveedor ya eliminado",
        expected_result="Status Code: 404, proveedor no encontrado",
        module="Compras",
        test_id="PRV-022"
    )
    async def test_delete_provider_already_deleted(self, client: httpx.AsyncClient, api_prefix: str):
        """PRV-022: Fail to delete provider that's already deleted"""
        provider_data = {
            "name": "Test Provider PRV-022",
            "nit": "900123456-22",
            "address": "Test Address 123",
            "responsible_name": "Test Manager",
            "email": "test022@provider.com",
            "phone_number": "3009998022"
        }
        
        # First create a provider
        create_response = await client.post(f"{api_prefix}/providers/", json=provider_data)
        assert create_response.status_code == 201
        provider_id = assert_response_has_id(create_response.json())
        
        # Delete the provider
        delete_response = await client.delete(f"{api_prefix}/providers/{provider_id}")
        assert delete_response.status_code == 204
        
        # Try to delete again
        response = await client.delete(f"{api_prefix}/providers/{provider_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert_error_response(data, "not found") 