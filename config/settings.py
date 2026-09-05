"""
Application settings configuration using Pydantic Settings.
"""
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kisan Dost - Pakistani Agronomy AI"
    environment: str = "development"
    debug: bool = True

    # Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # API Keys & Endpoints
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    amis_api_url: str = "https://amis.pk/api"

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    dataset_dir: Path = base_dir / "app" / "data" / "processed"
    raw_data_dir: Path = base_dir / "app" / "data" / "raw"
    sqlite_db_path: Path = base_dir / "app" / "data" / "kisan_dost.db"

    # Default Agro Parameters
    default_currency: str = "PKR"
    default_language: str = "ur"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
