# ==============================================================================
# InsightRural — Unified Application Configuration
# ==============================================================================
# Single source of truth for ALL configuration, constants, and environment
# variables. Replaces the scattered config across config.py, app.py,
# llm_service.py, chat.py, and kea_allotment_engine.py.
#
# Usage:
#   from core.config import settings
#   print(settings.GROQ_API_KEY)
#   print(settings.KEA_RESERVATION_POLICY)
# ==============================================================================

import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ── Path Constants ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR.parent / "data"
MODELS_DIR = BASE_DIR / "models"
CHROMA_DIR = BASE_DIR / "chroma_db"


# ══════════════════════════════════════════════════════════════════════════════
# Settings Class — Typed, Validated Configuration
# ══════════════════════════════════════════════════════════════════════════════

class Settings:
    """
    Application settings loaded from environment variables with sensible
    defaults. All configuration is centralized here — no hardcoded values
    anywhere else in the codebase.
    """

    def __init__(self):
        # ── Paths ─────────────────────────────────────────────────────────
        self.BASE_DIR = BASE_DIR
        self.DATA_DIR = DATA_DIR
        self.MODELS_DIR = MODELS_DIR
        self.CHROMA_DIR = CHROMA_DIR

        # ── Database ──────────────────────────────────────────────────────
        db_path = str(BASE_DIR / "insightrural.db").replace("\\", "/")
        self.DATABASE_URL: str = os.environ.get(
            "DATABASE_URL", f"sqlite:///{db_path}"
        )
        self.DB_ECHO: bool = os.environ.get("DB_ECHO", "false").lower() == "true"

        # ── LLM Configuration ────────────────────────────────────────────
        self.OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3")
        self.GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
        self.GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
        self.OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

        # ── Auth & Security ───────────────────────────────────────────────
        self.JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")
        if not self.JWT_SECRET_KEY:
            import warnings
            warnings.warn(
                "JWT_SECRET_KEY not set in environment. Using insecure default. "
                "Set JWT_SECRET_KEY env var in production.",
                UserWarning,
                stacklevel=2,
            )
            self.JWT_SECRET_KEY = "insightrural_secret_viva_2026_key"

        self.JWT_EXPIRY_SECONDS: int = int(
            os.environ.get("JWT_EXPIRY_SECONDS", str(86400 * 7))
        )

        # ── CORS ──────────────────────────────────────────────────────────
        self.CORS_ORIGINS: List[str] = os.environ.get(
            "CORS_ORIGINS", "*"
        ).split(",")

        # ── Rate Limiting ─────────────────────────────────────────────────
        self.RATE_LIMIT_PER_MINUTE: int = int(
            os.environ.get("RATE_LIMIT_PER_MINUTE", "60")
        )

        # ── Application Info ──────────────────────────────────────────────
        self.PROJECT_NAME: str = "InsightRural"
        self.APP_NAME: str = "InsightRural AI"
        self.APP_VERSION: str = "2.1.0"
        self.APP_DESCRIPTION: str = "AI-Powered College Counselling Platform"
        self.DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"



# ══════════════════════════════════════════════════════════════════════════════
# KEA Domain Constants — SINGLE SOURCE OF TRUTH
# ══════════════════════════════════════════════════════════════════════════════
# Previously duplicated in: config.py, kea_allotment_engine.py, app.py.
# Now defined ONCE here, imported everywhere via `from core.config import ...`
# ══════════════════════════════════════════════════════════════════════════════

KEA_RESERVATION_POLICY: Dict[str, Dict] = {
    "GM":   {"percent": 32, "label": "General Merit"},
    "SC":   {"percent": 15, "label": "Scheduled Caste"},
    "ST":   {"percent": 3,  "label": "Scheduled Tribe"},
    "CAT1": {"percent": 4,  "label": "Category-1 (Brahmins)"},
    "2A":   {"percent": 15, "label": "Category-2A (OBC)"},
    "2B":   {"percent": 4,  "label": "Category-2B (OBC)"},
    "3A":   {"percent": 4,  "label": "Category-3A (OBC)"},
    "3B":   {"percent": 5,  "label": "Category-3B (OBC)"},
}

KEA_SPECIAL_QUOTAS: Dict[str, Dict] = {
    "rural":          {"percent": 15, "label": "Rural Quota (1st-10th in rural area)"},
    "kannada_medium": {"percent": 5,  "label": "Kannada Medium Quota"},
    "snq":            {"percent": 0,  "label": "Supernumerary (physically disabled, ex-servicemen)"},
    "hk_371j":        {"percent": 8,  "label": "Hyderabad-Karnataka 371(J) Reservation"},
}

HK_DISTRICTS: List[str] = [
    "bidar", "gulbarga", "kalaburagi", "yadgir", "raichur",
    "koppal", "bellary", "ballari", "vijayanagara", "bagalkot",
]

CATEGORY_TO_DATASET: Dict[str, str] = {
    "GM": "GM", "GENERAL": "GM", "GEN": "GM", "OC": "GM",
    "SC": "SC", "ST": "ST",
    "OBC": "OBC", "2A": "OBC", "2B": "OBC", "3A": "OBC", "3B": "OBC",
    "CAT1": "OBC", "CAT-1": "OBC", "CATEGORY-1": "OBC",
    "EWS": "GM",
}

OBC_RELAXATION: Dict[str, float] = {
    "OBC": 1.00, "2A": 1.12, "2B": 0.95, "3A": 0.95, "3B": 1.00,
    "CAT1": 0.90, "CAT-1": 0.90,
}

BRANCH_CODES: Dict[str, int] = {
    "CSE": 1, "ISE": 2, "ECE": 3, "EEE": 4, "ME": 5, "CIVIL": 6,
    "AI": 7, "DS": 8, "AI_DS": 9, "CY": 10, "AERO": 11, "CHEM": 12,
    "BIOTECH": 13, "IE": 14, "AUTO": 15, "MINING": 16, "ML": 17,
}

TYPE_PRESTIGE: Dict[str, int] = {
    "Government": 95, "Government_Aided": 90, "Private_Autonomous": 80,
    "Type1_Unaided": 75, "Type2_Unaided": 65, "Deemed_Private": 70,
}

NAAC_SCORE: Dict[str, int] = {
    "A++": 98, "A+": 90, "A": 82, "B++": 75, "B+": 68, "B": 60,
    "C": 45, "N/A": 50,
}

RANKING_WEIGHTS: Dict[str, float] = {
    "admission_probability": 0.40,
    "placements": 0.20,
    "accreditation": 0.15,
    "hostel_quality": 0.10,
    "fees": 0.10,
    "location_preference": 0.05,
}

# ── Web Intelligence ──────────────────────────────────────────────────────────

ALLOWED_WEB_SOURCES: List[str] = [
    "cetonline.karnataka.gov.in",
    "kea.kar.nic.in",
    "vtu.ac.in",
    "aicte-india.org",
    "ugc.gov.in",
    "ssp.karnataka.gov.in",
    "ssp.postmatric.karnataka.gov.in",
    "vidyalakshmi.co.in",
]

BLOCKED_WEB_SOURCES: List[str] = [
    "quora.com", "reddit.com", "medium.com", "blogspot.com",
    "wordpress.com", "shiksha.com", "collegedunia.com",
]

# ── Category Margin (for admission probability calculation) ───────────────────

CATEGORY_MARGIN: Dict[str, int] = {
    "OPEN": 0, "GENERAL": 0, "GEN": 0, "UR": 0,
    "EWS": 2, "OBC": 3, "OBC-NCL": 3, "SC": 5, "ST": 5,
}


# ══════════════════════════════════════════════════════════════════════════════
# Singleton Settings Instance
# ══════════════════════════════════════════════════════════════════════════════

settings = Settings()


# ══════════════════════════════════════════════════════════════════════════════
# Backward Compatibility Exports
# ══════════════════════════════════════════════════════════════════════════════
# The old `config.py` exported these directly. These re-exports ensure
# existing `from config import ...` statements continue to work after
# the old config.py is updated to delegate here.
# ══════════════════════════════════════════════════════════════════════════════

OLLAMA_HOST = settings.OLLAMA_HOST
OLLAMA_MODEL = settings.OLLAMA_MODEL
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
GROQ_API_URL = settings.GROQ_API_URL
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
DATABASE_URL = settings.DATABASE_URL
CORS_ORIGINS = settings.CORS_ORIGINS
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION
APP_DESCRIPTION = settings.APP_DESCRIPTION
