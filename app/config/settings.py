"""
Application Settings Module.

This module loads and manages environment-based configuration for the
entire FastAPI application. It uses Pydantic Settings to automatically
read values from environment variables and `.env` files.

Key responsibilities:
- Centralized configuration management
- Secure loading of secrets (JWT keys, DB URL)
- Environment detection (development, production, etc.)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration class.

    Loads environment variables for:
        - Database connection
        - JWT algorithm and secret keys
        - Token/session expiry durations
        - Application environment mode

    Pydantic Settings automatically validates and parses values,
    ensuring strong typing and preventing misconfiguration.
    """

    # -------------------------
    # Database Configuration
    # -------------------------
    APP_DATABASE_URL: str  # Full database connection string

    # -------------------------
    # JWT / Security Settings
    # -------------------------
    APP_ALGORITHM: str  # Algorithm used for signing JWTs

    APP_ACCESS_TOKEN_SECRET_KEY: str  # Secret key for access tokens
    APP_REFRESH_TOKEN_SECRET_KEY: str  # Secret key for refresh tokens

    # -------------------------
    # Token Expiry Durations
    # -------------------------
    APP_REFRESH_TOKEN_EXPIRE_DAYS: int  # Refresh token lifetime
    APP_ACCESS_TOKEN_EXPIRE_MINUTES: int  # Access token lifetime
    APP_SESSION_EXPIRE_MINUTES: int  # Session cookie lifetime
    APP_SESSION_EXPIRE_DAYS: int  # Session persistence duration

    # -------------------------
    # Environment Mode
    # -------------------------
    APP_ENVIRONMENT: str = "development"  # Default environment

    # -------------------------
    # Pydantic Settings Config
    # -------------------------
    model_config = SettingsConfigDict(
        env_file=".env",              # Load variables from .env file
        env_file_encoding="utf-8"     # Ensure correct encoding
    )

    # -------------------------
    # Helper Methods
    # -------------------------
    def is_development(self) -> bool:
        """
        Returns True if the application is running in development mode.

        Useful for enabling debug features or verbose logging.
        """
        return self.APP_ENVIRONMENT.lower() == "development"


# Instantiate settings so the rest of the app can import it directly
settings = Settings()