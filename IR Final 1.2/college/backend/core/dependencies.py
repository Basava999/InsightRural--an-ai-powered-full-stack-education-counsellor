# ==============================================================================
# InsightRural — FastAPI Dependency Injection Container
# ==============================================================================
# Replaces module-level singletons (_counselor, _engine_instance, etc.) with
# FastAPI's Depends() system. Services are lazily initialized, properly
# scoped, and testable (can be overridden in tests).
#
# Usage in routers:
#   from core.dependencies import get_json_data_service, get_recommendation_svc
#
#   @router.post("/predict/kcet")
#   async def predict(
#       service: RecommendationService = Depends(get_recommendation_svc),
#   ):
#       ...
#
# Usage in tests:
#   app.dependency_overrides[get_json_data_service] = lambda: mock_service
# ==============================================================================

import logging
from typing import Optional

from core.config import settings

logger = logging.getLogger("Dependencies")


# ══════════════════════════════════════════════════════════════════════════════
# Lazy Singleton Registry
# ══════════════════════════════════════════════════════════════════════════════
# Each service is initialized once (on first access) and cached.
# This replaces the scattered module-level `_instance = None` pattern.
# ══════════════════════════════════════════════════════════════════════════════

class _ServiceRegistry:
    """
    Internal registry holding singleton service instances.
    Each attribute is lazily populated by its corresponding getter function.
    """

    def __init__(self):
        self._json_data_service = None
        self._recommendation_service = None
        self._kea_engine = None
        self._llm_service = None
        self._rag_engine = None
        self._query_parser = None
        self._ml_predictor = None

    def reset(self):
        """Reset all cached instances. Used in testing."""
        self.__init__()


_registry = _ServiceRegistry()


# ══════════════════════════════════════════════════════════════════════════════
# Dependency Provider Functions (used with FastAPI Depends())
# ══════════════════════════════════════════════════════════════════════════════

def get_json_data_service():
    """
    Get or create the JSONDataService singleton.
    This is the PRIORITY 1 data source — trusted factual data.
    """
    if _registry._json_data_service is None:
        try:
            from json_data_service import JSONDataService
            _registry._json_data_service = JSONDataService()
            logger.info("JSONDataService initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize JSONDataService: %s", e)
            raise
    return _registry._json_data_service


def get_recommendation_service():
    """
    Get or create the RecommendationService singleton.
    Depends on: JSONDataService
    """
    if _registry._recommendation_service is None:
        try:
            from services.recommendation_service import RecommendationService
            json_data = get_json_data_service()
            _registry._recommendation_service = RecommendationService(json_data)
            logger.info("RecommendationService initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize RecommendationService: %s", e)
            raise
    return _registry._recommendation_service


def get_kea_engine():
    """
    Get or create the KEA Seat Allotment Engine singleton.
    Trains ML models on startup (may take a few seconds).
    """
    if _registry._kea_engine is None:
        try:
            from kea_allotment_engine import KEASeatAllotmentEngine
            _registry._kea_engine = KEASeatAllotmentEngine()
            logger.info("KEASeatAllotmentEngine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize KEASeatAllotmentEngine: %s", e)
            raise
    return _registry._kea_engine


def get_llm_service():
    """
    Get or create the LLM orchestrator singleton.
    Manages Groq → Ollama → RAG fallback chain.
    """
    if _registry._llm_service is None:
        try:
            from llm_service import InsightRuralCounselor
            _registry._llm_service = InsightRuralCounselor()
            logger.info("LLM Service (InsightRuralCounselor) initialized")
        except Exception as e:
            logger.error("Failed to initialize LLM Service: %s", e)
            raise
    return _registry._llm_service


def get_rag_engine():
    """
    Get or create the RAG engine singleton.
    Uses ChromaDB for vector retrieval.
    """
    if _registry._rag_engine is None:
        try:
            from rag_engine import StrictRAGEngine
            _registry._rag_engine = StrictRAGEngine()
            logger.info("RAG Engine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize RAG Engine: %s", e)
            raise
    return _registry._rag_engine


def get_query_parser():
    """
    Get or create the QueryParser singleton.
    Deterministic regex-based query parsing — no LLM dependency.
    """
    if _registry._query_parser is None:
        try:
            from engines.query_parser import QueryParser
            _registry._query_parser = QueryParser()
            logger.info("QueryParser initialized")
        except Exception as e:
            logger.error("Failed to initialize QueryParser: %s", e)
            raise
    return _registry._query_parser


def get_ml_predictor():
    """
    Get or create the ML College Predictor singleton.
    Used for KCET college prediction with scikit-learn models.
    """
    if _registry._ml_predictor is None:
        try:
            from ml_predictor import CollegePredictor
            _registry._ml_predictor = CollegePredictor()
            logger.info("ML Predictor initialized")
        except Exception as e:
            logger.error("Failed to initialize ML Predictor: %s", e)
            raise
    return _registry._ml_predictor


# ══════════════════════════════════════════════════════════════════════════════
# Service Availability Checkers
# ══════════════════════════════════════════════════════════════════════════════
# These replace the module-level boolean flags like AI_MODULES_AVAILABLE,
# KEA_ENGINE_AVAILABLE, etc. scattered across app.py. They attempt lazy
# initialization and return availability status.
# ══════════════════════════════════════════════════════════════════════════════

def is_llm_available() -> bool:
    """Check if the LLM service can be initialized."""
    try:
        get_llm_service()
        return True
    except Exception:
        return False


def is_rag_available() -> bool:
    """Check if the RAG engine can be initialized."""
    try:
        get_rag_engine()
        return True
    except Exception:
        return False


def is_kea_available() -> bool:
    """Check if the KEA engine can be initialized."""
    try:
        get_kea_engine()
        return True
    except Exception:
        return False


def is_ml_available() -> bool:
    """Check if the ML predictor can be initialized."""
    try:
        get_ml_predictor()
        return True
    except Exception:
        return False


def reset_all_services():
    """Reset all service singletons. Used in testing."""
    _registry.reset()
