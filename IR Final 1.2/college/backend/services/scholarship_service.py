# ==============================================================================
# InsightRural — Scholarship Service
# ==============================================================================
# Wraps scholarship matching, essay generation, and PDF creation.
# ==============================================================================

import json
import os
from typing import Dict, Any, List, Optional

from core.logging import get_logger
from core.config import settings

logger = get_logger("services.scholarship")


class ScholarshipService:
    """
    Scholarship matching and application service.
    Provides smart-match filtering and AI-powered essay/PDF generation.
    """

    def __init__(self):
        self._scholarships: Optional[List[Dict]] = None

    def _load_scholarships(self) -> List[Dict]:
        """Lazy-load scholarships from JSON file."""
        if self._scholarships is None:
            data_file = os.path.join(str(settings.DATA_DIR), "scholarships.json")
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    self._scholarships = json.load(f)
                logger.info("Loaded %d scholarships", len(self._scholarships))
            except Exception as e:
                logger.error("Failed to load scholarships: %s", e)
                self._scholarships = []
        return self._scholarships

    def match_scholarships(
        self,
        category: str = "",
        income: int = 500000,
        gender: str = "",
    ) -> List[Dict]:
        """
        Match student profile to eligible scholarships.
        Uses category, income, and gender filters.
        """
        all_scholarships = self._load_scholarships()
        eligible = []
        category_lower = category.lower()

        for sch in all_scholarships:
            elig = sch.get("eligibility", {})
            income_limit = elig.get(
                "income_limit", elig.get("income_max", float("inf"))
            )
            sch_categories = str(elig.get("category", [])).lower()

            if income > income_limit:
                continue

            # Category matching
            cat_match = False
            if "all categories" in sch_categories or "all" in sch_categories:
                cat_match = True
            elif category_lower in sch_categories:
                cat_match = True
            elif category.upper() in ["SC", "ST"] and (
                "sc" in sch_categories or "st" in sch_categories
            ):
                cat_match = True
            elif "obc" in category_lower and (
                "obc" in sch_categories
                or "2a" in sch_categories
                or "3a" in sch_categories
            ):
                cat_match = True

            # Gender filter
            gender_req = elig.get("gender", "").lower()
            if gender_req and gender and gender_req != gender.lower():
                cat_match = False

            if cat_match:
                eligible.append(sch)

        return eligible

    def generate_essay(
        self,
        student_data: Dict[str, Any],
        scholarship_name: str = "Scholarship",
        reason: str = "",
    ) -> str:
        """
        Generate scholarship application essay using LLM.
        Falls back to template if LLM unavailable.
        """
        try:
            from scholarship_service import generate_scholarship_essay
            return generate_scholarship_essay(student_data, scholarship_name, reason)
        except ImportError:
            logger.warning("Scholarship service not available, using template")
            return self._template_essay(student_data, scholarship_name, reason)

    def _template_essay(
        self,
        student_data: Dict,
        scholarship_name: str,
        reason: str,
    ) -> str:
        """Deterministic essay template when LLM is unavailable."""
        name = student_data.get("name", "Student")
        category = student_data.get("category", "General")
        rank = student_data.get("kcet_rank", "N/A")
        return (
            f"Dear Sir/Madam,\n\n"
            f"I, {name}, am writing to apply for the {scholarship_name}. "
            f"I belong to the {category} category and secured KCET rank {rank}. "
            f"{reason}\n\n"
            f"I come from a humble background and this scholarship would greatly "
            f"help me pursue my engineering education. I am committed to academic "
            f"excellence and promise to make the most of this opportunity.\n\n"
            f"Thank you for considering my application.\n\n"
            f"Yours sincerely,\n{name}"
        )

    def create_application_pdf(
        self,
        student_data: Dict[str, Any],
        essay: str,
    ) -> Optional[tuple]:
        """Generate PDF for scholarship application."""
        try:
            from scholarship_service import create_application_pdf
            return create_application_pdf(student_data, essay)
        except ImportError:
            logger.error("PDF generation module not available")
            return None


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[ScholarshipService] = None


def get_scholarship_service() -> ScholarshipService:
    global _instance
    if _instance is None:
        _instance = ScholarshipService()
    return _instance
