# ==============================================================================
# InsightRural Services Package
# ==============================================================================
# Business orchestration layer. Each service wraps domain logic and provides
# a clean typed interface for API routers.
# ==============================================================================

from services.admission_service import AdmissionService, get_admission_service
from services.counseling_service import CounselingService, get_counseling_service
from services.career_service import CareerService, get_career_service
from services.scholarship_service import ScholarshipService, get_scholarship_service

__all__ = [
    "AdmissionService",
    "CounselingService",
    "CareerService",
    "ScholarshipService",
    "get_admission_service",
    "get_counseling_service",
    "get_career_service",
    "get_scholarship_service",
]
