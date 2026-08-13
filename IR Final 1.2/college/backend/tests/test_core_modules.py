# ==============================================================================
# InsightRural — Core Module Tests
# ==============================================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestCoreConfig:
    """Test unified configuration module."""

    def test_settings_loads(self):
        from core.config import settings
        assert settings is not None

    def test_settings_has_project_name(self):
        from core.config import settings
        assert settings.PROJECT_NAME == "InsightRural"

    def test_settings_has_data_dir(self):
        from core.config import settings
        assert settings.DATA_DIR is not None

    def test_settings_has_jwt_secret(self):
        from core.config import settings
        assert settings.JWT_SECRET_KEY is not None
        assert len(settings.JWT_SECRET_KEY) > 0


class TestCoreLogging:
    """Test structured logging module."""

    def test_logger_creates(self):
        from core.logging import get_logger
        logger = get_logger("test_module")
        assert logger is not None

    def test_logger_has_standard_methods(self):
        from core.logging import get_logger
        logger = get_logger("test_module")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_logger_does_not_crash(self):
        from core.logging import get_logger
        logger = get_logger("test_module")
        logger.info("Test message: %s", "hello")
        logger.warning("Test warning")
        logger.error("Test error")


class TestCoreExceptions:
    """Test exception hierarchy."""

    def test_base_error(self):
        from core.exceptions import InsightRuralError
        err = InsightRuralError("test")
        assert err.message == "test"
        assert err.status_code == 500

    def test_validation_error(self):
        from core.exceptions import ValidationError
        err = ValidationError("bad input")
        assert err.status_code == 422

    def test_data_not_found_error(self):
        from core.exceptions import DataNotFoundError
        err = DataNotFoundError("missing")
        assert err.status_code == 404

    def test_service_unavailable_error(self):
        from core.exceptions import ServiceUnavailableError
        err = ServiceUnavailableError("LLM")
        assert err.status_code == 503

    def test_error_to_response(self):
        from core.exceptions import InsightRuralError
        err = InsightRuralError("test error", error_code="TEST_ERR")
        response = err.to_response()
        assert response["success"] is False
        assert response["error"] == "test error"
        assert response["error_code"] == "TEST_ERR"


class TestCoreDependencies:
    """Test dependency injection helpers."""

    def test_llm_availability_check(self):
        from core.dependencies import is_llm_available
        result = is_llm_available()
        assert isinstance(result, bool)

    def test_rag_availability_check(self):
        from core.dependencies import is_rag_available
        result = is_rag_available()
        assert isinstance(result, bool)

    def test_kea_availability_check(self):
        from core.dependencies import is_kea_available
        result = is_kea_available()
        assert isinstance(result, bool)

    def test_ml_availability_check(self):
        from core.dependencies import is_ml_available
        result = is_ml_available()
        assert isinstance(result, bool)


class TestRAGEngine:
    """Test RAG engine components."""

    def test_search_result_model(self):
        from rag_engine import SearchResult
        sr = SearchResult(content="test data", source="db", relevance_score=0.9)
        assert sr.content == "test data"
        assert sr.source == "db"
        assert sr.relevance_score == 0.9

    def test_search_result_to_dict(self):
        from rag_engine import SearchResult
        sr = SearchResult(content="hello", source="test")
        d = sr.to_dict()
        assert d["content"] == "hello"
        assert d["source"] == "test"
        assert "relevance_score" in d

    def test_bm25_index_empty(self):
        from rag_engine import BM25Index
        idx = BM25Index()
        assert idx.is_built is False
        assert idx.search("test") == []

    def test_bm25_index_build_and_search(self):
        from rag_engine import BM25Index
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            import pytest
            pytest.skip("rank_bm25 not installed")

        idx = BM25Index()
        docs = [
            "RV College of Engineering CSE cutoff 3500",
            "BMS College ECE placement 6 LPA average",
            "NIE Mysore mechanical engineering hostel",
        ]
        meta = [{"source": "test"}] * len(docs)
        sources = ["test_db"] * len(docs)
        idx.build(docs, meta, sources)

        assert idx.is_built is True

        results = idx.search("CSE cutoff RV College", top_k=3)
        assert len(results) > 0
        # First result should be the CSE cutoff doc (most keyword overlap)
        assert "CSE" in results[0].content or "cutoff" in results[0].content
