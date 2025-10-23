"""
Configuración de la aplicación
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings
    """
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGSSLMODE: str = "require"
    PGCHANNELBINDING: str = "require"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de conexión a PostgreSQL"""
        return (
            f"postgresql://{self.PGUSER}:{self.PGPASSWORD}"
            f"@{self.PGHOST}/{self.PGDATABASE}"
            f"?sslmode={self.PGSSLMODE}"
        )
    
    PROJECT_NAME: str = "Planner Universitario API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True

settings = Settings() # type: ignore
