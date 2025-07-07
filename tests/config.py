import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_AUTH_BACKEND_URL: str
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