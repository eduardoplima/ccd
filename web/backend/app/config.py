from __future__ import annotations

import urllib.parse
from functools import lru_cache
from pathlib import Path

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    sql_server_host: str
    sql_server_port: int = 1433
    sql_server_user: str
    sql_server_pass: str
    sql_server_driver: str = "ODBC Driver 18 for SQL Server"
    sql_server_database: str = "BdDIP"

    # Nomes lógicos de DB usados pelo módulo CGAD (todos via pyodbc).
    sql_server_db_processos: str = "processo"
    sql_server_db_decisoes: str = "BdDIP"
    sql_server_db_siai: str = "BdSIAI"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    cors_allowed_origins: str = "http://localhost:3000"
    redis_url: str | None = None

    # Azure OpenAI (módulo CGAD).
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    openai_api_version: str | None = None
    azure_openai_deployment: str = "gpt-4o"

    @field_validator("cors_allowed_origins")
    @classmethod
    def _strip_origins(cls, v: str) -> str:
        return v.strip()

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    def odbc_url(self, database: str) -> str:
        """SQLAlchemy URL (mssql+pyodbc) para um DB específico no mesmo servidor."""
        odbc = (
            f"DRIVER={{{self.sql_server_driver}}};"
            f"SERVER={self.sql_server_host},{self.sql_server_port};"
            f"DATABASE={database};"
            f"UID={self.sql_server_user};PWD={self.sql_server_pass};"
            f"TrustServerCertificate=yes;Encrypt=no;"
        )
        return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc)

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """DB principal (BdDIP): auth + tabelas FRAP* + tabelas CGAD."""
        return self.odbc_url(self.sql_server_database)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
