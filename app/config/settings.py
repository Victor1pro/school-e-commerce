# app/config/settings.py
"""
Application Settings Module
---------------------------
Centralized configuration for the entire FastAPI application.

Features:
- Loads environment variables from `.env`
- Strong typing via Pydantic Settings 
- Production‑ready defaults
- Secure JWT configuration
- Environment mode detection
- CORS, cookie, and session settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application configuration class.

    Loads environment variables for:
        - Database connection
        - JWT algorithm and secret keys
        - Token/session expiry durations
        - CORS configuration
        - Cookie security settings
        - Environment mode (dev/prod)
    """

    # ------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------
    APP_DATABASE_URL: str

    # ------------------------------------------------------------
    # JWT / Security Settings
    # ------------------------------------------------------------
    APP_JWT_ALGORITHM: str = "HS256"

    APP_USER_ACCESS_TOKEN_SECRET_KEY: str
    APP_USER_REFRESH_TOKEN_SECRET_KEY: str


    APP_ADMIN_ACCESS_TOKEN_SECRET_KEY: str
    APP_ADMIN_REFRESH_TOKEN_SECRET_KEY: str

    # ------------------------------------------------------------
    # Token Expiry Durations for User
    # ------------------------------------------------------------
    APP_USER_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    APP_USER_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_SESSION_EXPIRE_MINUTES: int = 60
    APP_SESSION_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------
    # Token Expiry Durations for User
    # ------------------------------------------------------------
    APP_ADMIN_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    APP_ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10

    # ------------------------------------------------------------
    # Cookie / CORS Settings
    # ------------------------------------------------------------
    APP_DOMAIN: str = "localhost"
    APP_SECURE_COOKIES: bool = False  # True in production (HTTPS)
    APP_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:5500"]

    # ------------------------------------------------------------
    # Environment Mode
    # ------------------------------------------------------------
    APP_ENVIRONMENT: str = "development"  # development | production | staging
    APP_DEBUG: bool = True

    # ------------------------------------------------------------
    # Pydantic Settings Config
    # ------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore unknown env vars instead of crashing
    )

    # ------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------
    def is_development(self) -> bool:
        """Returns True if running in development mode."""
        return self.APP_ENVIRONMENT.lower() == "development"

    def is_production(self) -> bool:
        """Returns True if running in production mode."""
        return self.APP_ENVIRONMENT.lower() == "production"


# Global settings instance
settings = Settings()