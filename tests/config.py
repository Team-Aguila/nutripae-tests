import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_AUTH_BACKEND_URL: str
    BASE_MENUS_BACKEND_URL: str = "http://localhost:8003"
    BASE_COMPRAS_BACKEND_URL: str = "http://localhost:8004"
    BASE_COVERAGE_BACKEND_URL: str
    BASE_RH_BACKEND_URL: str

    BASE_FRONTEND_URL: str

    ADMIN_USER_EMAIL: str 
    ADMIN_USER_PASSWORD: str

    BASE_USER_EMAIL: str 
    BASE_USER_PASSWORD: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# Instancia global de la configuración
settings = Settings()