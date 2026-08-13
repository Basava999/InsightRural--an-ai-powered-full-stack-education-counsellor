"""Application configuration."""

import os
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]
COLLEGE_ROOT = BASE_DIR.parent
DATA_DIR = COLLEGE_ROOT / "data"
LEGACY_BACKEND = COLLEGE_ROOT / "backend"
CHROMA_DIR = LEGACY_BACKEND / "chroma_db"
ML_MODELS_DIR = LEGACY_BACKEND / "models"


class Settings:
    APP_NAME: str = "KCET Counselling Platform"
    APP_VERSION: str = "3.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://kcet:kcet@localhost:5432/kcet_platform",
    )
    USE_JSON_DATA: bool = os.getenv("USE_JSON_DATA", "true").lower() == "true"
    DATA_DIR: Path = DATA_DIR
    CHROMA_DIR: Path = Path(os.getenv("CHROMA_DIR", str(CHROMA_DIR)))
    ML_MODELS_DIR: Path = Path(os.getenv("ML_MODELS_DIR", str(ML_MODELS_DIR)))

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    ENGINE_VERSION: str = "3.0.0"

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 100

    OFFICIAL_DOMAINS: tuple = (
        "kea.kar.nic.in", "cetonline.karnataka.gov.in", "vtu.ac.in",
        "aicte-india.org", "ugc.ac.in", "scholarships.gov.in",
        "karnataka.gov.in", "nsp.gov.in",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
