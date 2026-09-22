"""
Configurações da aplicação.

Todas as configurações sensíveis ou variáveis por ambiente são lidas de
variáveis de ambiente (via pydantic-settings), nunca hardcoded no código.
Em desenvolvimento, os valores podem vir de um arquivo `.env` na raiz do
backend (veja `.env.example`).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Metadados da aplicação
    app_name: str = "Event Management API"
    environment: str = "development"

    # Banco de dados (SQLite local por padrão, mas pode apontar para Postgres etc.)
    database_url: str = "sqlite:///./data/event_management.db"

    # Autenticação JWT (OAuth2PasswordBearer)
    secret_key: str = "change-this-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS - lista separada por vírgula de origens permitidas para o frontend
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cacheia a instância de settings para evitar reler o ambiente a cada chamada."""
    return Settings()
