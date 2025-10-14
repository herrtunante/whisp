"""
Configuration settings for the Whisp API
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """API configuration settings"""

    # API metadata
    API_TITLE: str = "Whisp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for geospatial forest and deforestation risk assessment using Google Earth Engine"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Google Earth Engine
    GEE_PROJECT: Optional[str] = None
    GEE_SERVICE_ACCOUNT: Optional[str] = None
    GEE_PRIVATE_KEY_PATH: Optional[str] = None

    # Whisp configuration
    WHISP_ROOT: Path = Path(__file__).parent.parent.parent.parent
    WHISP_OUTPUT_DIR: Path = WHISP_ROOT / "results"
    WHISP_THRESHOLD_TO_DRIVE: int = 500

    # EUDR risk thresholds
    DEFAULT_IND_1_THRESHOLD: float = 10.0
    DEFAULT_IND_2_THRESHOLD: float = 10.0
    DEFAULT_IND_3_THRESHOLD: float = 0.0
    DEFAULT_IND_4_THRESHOLD: float = 0.0

    # CORS settings
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from parent .env


# Global settings instance
settings = Settings()
