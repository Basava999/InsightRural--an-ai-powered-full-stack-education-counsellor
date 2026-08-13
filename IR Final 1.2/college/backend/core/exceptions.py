# ==============================================================================
# InsightRural — Typed Exception Hierarchy
# ==============================================================================
# All application exceptions derive from InsightRuralError. Each maps to a
# specific HTTP status code via FastAPI exception handlers in main.py.
#
# Usage:
#   from core.exceptions import DataNotFoundError
#   raise DataNotFoundError("College 'XYZ' not found in database")
#
# This replaces bare `except Exception` blocks with specific, catchable
# exception types that produce meaningful HTTP responses.
# ==============================================================================

from typing import Optional, Dict, Any


class InsightRuralError(Exception):
    """
    Base exception for all InsightRural application errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code to return (default: 500).
        error_code: Machine-readable error code for frontend parsing.
        details: Optional extra context for debugging.
    """

    def __init__(
        self,
        message: str = "An internal error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_response(self) -> Dict[str, Any]:
        """Convert to API error response body."""
        response = {
            "success": False,
            "error": self.message,
            "error_code": self.error_code,
        }
        if self.details:
            response["details"] = self.details
        return response


# ── Data Errors ───────────────────────────────────────────────────────────────

class DataNotFoundError(InsightRuralError):
    """Raised when requested data does not exist in the database."""

    def __init__(self, message: str = "Requested data not found", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="DATA_NOT_FOUND",
            details=details,
        )


class DataValidationError(InsightRuralError):
    """Raised when input data fails validation beyond Pydantic checks."""

    def __init__(self, message: str = "Invalid input data", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ValidationError(DataValidationError):
    """Alias for DataValidationError to match original plans and tests."""
    pass



# ── Service Errors ────────────────────────────────────────────────────────────

class ServiceUnavailableError(InsightRuralError):
    """Raised when a required service (ML, RAG, LLM) is not available."""

    def __init__(self, service_name: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"{service_name} is currently unavailable",
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service_name, **(details or {})},
        )


class LLMUnavailableError(ServiceUnavailableError):
    """Raised when no LLM provider (Groq, Ollama) is reachable."""

    def __init__(self, details: Optional[Dict] = None):
        super().__init__(service_name="LLM Service", details=details)


class RAGUnavailableError(ServiceUnavailableError):
    """Raised when the RAG/ChromaDB engine is not available."""

    def __init__(self, details: Optional[Dict] = None):
        super().__init__(service_name="RAG Engine", details=details)


class MLModelUnavailableError(ServiceUnavailableError):
    """Raised when ML predictor models are not loaded."""

    def __init__(self, details: Optional[Dict] = None):
        super().__init__(service_name="ML Predictor", details=details)


# ── Auth Errors ───────────────────────────────────────────────────────────────

class AuthenticationError(InsightRuralError):
    """Raised when authentication fails (invalid/expired token)."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTH_FAILED",
            details=details,
        )


class AuthorizationError(InsightRuralError):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Not authorized", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            details=details,
        )


# ── Rate Limiting ─────────────────────────────────────────────────────────────

class RateLimitError(InsightRuralError):
    """Raised when a client exceeds the rate limit."""

    def __init__(self, retry_after: int = 60, details: Optional[Dict] = None):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            status_code=429,
            error_code="RATE_LIMITED",
            details={"retry_after_seconds": retry_after, **(details or {})},
        )


# ── Pipeline Errors ───────────────────────────────────────────────────────────

class PipelineError(InsightRuralError):
    """Raised when the recommendation/prediction pipeline encounters an error."""

    def __init__(self, stage: str, message: str = "Pipeline error", details: Optional[Dict] = None):
        super().__init__(
            message=f"Pipeline error at stage '{stage}': {message}",
            status_code=500,
            error_code="PIPELINE_ERROR",
            details={"stage": stage, **(details or {})},
        )


class ConstraintViolationError(InsightRuralError):
    """Raised when all colleges are filtered out by user constraints."""

    def __init__(self, constraints: Dict[str, Any], details: Optional[Dict] = None):
        super().__init__(
            message=(
                "No college in the current database satisfies all specified "
                "constraints. Consider relaxing one or more constraints."
            ),
            status_code=200,  # Not an error — valid empty result
            error_code="NO_RESULTS",
            details={"constraints_applied": constraints, **(details or {})},
        )
