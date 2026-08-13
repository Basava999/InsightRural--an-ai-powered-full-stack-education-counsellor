# ==============================================================================
# InsightRural — Admission Service (Unified JEE/NEET/KCET)
# ==============================================================================
# Clean service wrapper around existing admission logic.
# Receives dependencies via constructor injection.
# ==============================================================================

from typing import Dict, Any, List, Optional

from core.logging import get_logger
from core.exceptions import ValidationError, DataNotFoundError

logger = get_logger("services.admission")


class AdmissionService:
    """
    Unified admission counseling service.

    Orchestrates:
    - Admission probability calculation
    - JEE rank-based prediction
    - NEET rank-based prediction
    - College comparison
    - Career roadmap generation

    All heavy logic is delegated to existing modules. This class
    provides a clean typed interface for the API routers.
    """

    def __init__(self):
        self._jee_predictor = None
        self._neet_predictor = None
        self._init_predictors()

    def _init_predictors(self):
        """Lazy-load ML predictors."""
        try:
            from ml_predictor import get_jee_predictor, get_neet_predictor
            self._jee_predictor = get_jee_predictor()
            self._neet_predictor = get_neet_predictor()
            logger.info("AdmissionService: JEE/NEET predictors loaded")
        except ImportError:
            logger.warning("ML predictor module not available")
        except Exception as e:
            logger.warning("ML predictor init failed: %s", e)

    def calculate_probability(
        self,
        rank: int,
        previous_cutoff: int,
        category: str = "OPEN",
    ) -> Dict[str, Any]:
        """Calculate rank-vs-cutoff admission probability (0-100)."""
        from admission_probability import calculate_admission_probability
        return calculate_admission_probability(rank, previous_cutoff, category)

    def predict_jee(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Run JEE prediction pipeline."""
        from admissions_service import predict_jee
        return predict_jee(profile)

    def predict_neet(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Run NEET prediction pipeline."""
        from admissions_service import predict_neet
        return predict_neet(profile)

    def get_jee_cutoffs(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Retrieve JEE cutoff data with filters."""
        from admissions_service import get_jee_cutoffs
        return get_jee_cutoffs(filters)

    def get_neet_cutoffs(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Retrieve NEET cutoff data with filters."""
        from admissions_service import get_neet_cutoffs
        return get_neet_cutoffs(filters)

    def compare_jee_options(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare JEE options or named colleges."""
        from admissions_service import compare_jee_options
        return compare_jee_options(data)

    def compare_colleges(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple colleges on fees, placement, hostel, location."""
        from admissions_service import compare_colleges
        return compare_colleges(data)

    def build_neet_counseling_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build full NEET counseling plan."""
        from admissions_service import build_neet_counseling_plan
        return build_neet_counseling_plan(data)

    def generate_career_roadmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deterministic 5-year career roadmap."""
        from admissions_service import generate_career_roadmap
        return generate_career_roadmap(data)

    def answer_admission_query(
        self,
        message: str,
        profile: Dict[str, Any],
        llm=None,
    ) -> Dict[str, Any]:
        """RAG-powered admission counselor response."""
        from admissions_service import answer_admission_query
        return answer_admission_query(message, profile, llm=llm)


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[AdmissionService] = None


def get_admission_service() -> AdmissionService:
    global _instance
    if _instance is None:
        _instance = AdmissionService()
    return _instance
