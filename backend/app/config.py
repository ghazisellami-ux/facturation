from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration."""

    # App
    APP_NAME: str = "SIC Facture"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://sicfacture:sicfacture2024@db:5432/sicfacture"

    # JWT
    SECRET_KEY: str = "sic-facture-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Tax Configuration (Tunisia)
    DEFAULT_TVA_RATE: float = 19.0
    FODEC_RATE: float = 1.0
    TIMBRE_FISCAL: float = 1.0  # 1 TND

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
