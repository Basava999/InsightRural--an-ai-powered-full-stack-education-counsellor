# ==============================================================================
# InsightRural — Application Configuration (Backward Compatibility Layer)
# ==============================================================================
# This file now delegates to core.config which is the single source of truth.
# All existing `from config import ...` statements continue to work unchanged.
# ==============================================================================

# Re-export everything from core.config so existing imports don't break
from core.config import (
    # Settings instance
    settings,
    # Path constants
    BASE_DIR,
    DATA_DIR,
    MODELS_DIR,
    CHROMA_DIR,
    # Database
    DATABASE_URL,
    # LLM
    OLLAMA_HOST,
    OLLAMA_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_URL,
    # Auth
    JWT_SECRET_KEY,
    # CORS
    CORS_ORIGINS,
    # KEA Domain Constants (SINGLE SOURCE OF TRUTH)
    KEA_RESERVATION_POLICY,
    KEA_SPECIAL_QUOTAS,
    HK_DISTRICTS,
    CATEGORY_TO_DATASET,
    OBC_RELAXATION,
    BRANCH_CODES,
    TYPE_PRESTIGE,
    NAAC_SCORE,
    RANKING_WEIGHTS,
    # Web Intelligence
    ALLOWED_WEB_SOURCES,
    BLOCKED_WEB_SOURCES,
    # Category Margin
    CATEGORY_MARGIN,
    # Application Info
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
)

# Rate limiting (also from core.config settings)
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
