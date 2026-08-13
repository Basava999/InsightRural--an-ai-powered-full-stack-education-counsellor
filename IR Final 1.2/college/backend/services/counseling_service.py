# ==============================================================================
# InsightRural — Counseling Service
# ==============================================================================
# Wraps counseling guide generation, option entry, and KEA process help.
# ==============================================================================

import json
from typing import Dict, Any, Optional, List

from core.logging import get_logger

logger = get_logger("services.counseling")


class CounselingService:
    """
    Provides structured counseling guidance for students.
    Combines deterministic process guides with LLM-enhanced explanations.
    """

    # KEA Counseling Process Steps
    KEA_PROCESS_STEPS = [
        {
            "step": 1,
            "title": "Online Registration",
            "description": "Register on KEA website with KCET application number",
            "documents": ["KCET Hall Ticket", "Aadhar Card", "10th & 12th Marks Card"],
            "deadline": "Usually June-July",
        },
        {
            "step": 2,
            "title": "Document Verification",
            "description": "Visit nearest KEA Help Centre with original documents",
            "documents": [
                "KCET Score Card", "Study Certificate", "Income Certificate",
                "Caste Certificate (if applicable)", "Transfer Certificate",
                "Rural Study Certificate (if claiming rural quota)",
            ],
            "deadline": "As per KEA notification",
        },
        {
            "step": 3,
            "title": "Web Option Entry",
            "description": "Enter college + branch choices in order of preference",
            "tips": [
                "Add at least 30-50 options for best chances",
                "Order: Dream colleges first, Safe colleges last",
                "Include multiple branches per college",
            ],
        },
        {
            "step": 4,
            "title": "Seat Allotment",
            "description": "KEA processes options using merit + reservation + preference order",
            "notes": [
                "Round 1 results published first",
                "Can modify options between rounds",
                "Accept or reject within deadline",
            ],
        },
        {
            "step": 5,
            "title": "Admission & Fee Payment",
            "description": "Report to allotted college with documents and pay fees",
            "documents": [
                "Allotment Order", "Original Documents",
                "Demand Draft / Online Payment Receipt",
            ],
        },
    ]

    def get_counseling_process(self, exam: str = "KCET") -> Dict[str, Any]:
        """Return step-by-step counseling process."""
        if exam.upper() == "KCET":
            return {
                "exam": "KCET",
                "authority": "Karnataka Examinations Authority (KEA)",
                "website": "https://cetonline.karnataka.gov.in/kea/",
                "total_steps": len(self.KEA_PROCESS_STEPS),
                "steps": self.KEA_PROCESS_STEPS,
            }
        return {
            "exam": exam,
            "message": f"Counseling process for {exam} will be added soon.",
            "steps": [],
        }

    def generate_option_entry_strategy(
        self,
        rank: int,
        category: str,
        branch_preferences: List[str],
        location_preferences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a ranked list of option entry suggestions.
        Uses deterministic logic (no LLM dependency).
        """
        try:
            from kea_allotment_engine import get_kea_engine
            engine = get_kea_engine()

            result = engine.simulate(
                rank=rank,
                category=category,
                branch_preference=branch_preferences,
                district_preference=location_preferences,
                top_n=30,
            )

            safe = [c for c in result.get("colleges", []) if c.get("confidence", "") == "Safe"]
            moderate = [c for c in result.get("colleges", []) if c.get("confidence", "") == "Moderate"]
            ambitious = [c for c in result.get("colleges", []) if c.get("confidence", "") == "Ambitious"]

            strategy = []
            # Add ambitious first (dream), then moderate, then safe
            for i, college in enumerate(ambitious[:5], 1):
                strategy.append({**college, "option_order": i, "strategy": "Dream"})
            for i, college in enumerate(moderate[:10], len(strategy) + 1):
                strategy.append({**college, "option_order": i, "strategy": "Target"})
            for i, college in enumerate(safe[:15], len(strategy) + 1):
                strategy.append({**college, "option_order": i, "strategy": "Safety"})

            return {
                "success": True,
                "total_options": len(strategy),
                "strategy_breakdown": {
                    "dream": len([s for s in strategy if s["strategy"] == "Dream"]),
                    "target": len([s for s in strategy if s["strategy"] == "Target"]),
                    "safety": len([s for s in strategy if s["strategy"] == "Safety"]),
                },
                "recommended_options": strategy,
                "tip": "Add all these options in this order for the best allotment chances.",
            }

        except ImportError:
            logger.warning("KEA engine not available for option entry strategy")
            return {
                "success": False,
                "message": "KEA simulation engine not available. Try the prediction tool instead.",
            }
        except Exception as e:
            logger.error("Option entry strategy error: %s", e, exc_info=True)
            return {"success": False, "error": str(e)}


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[CounselingService] = None


def get_counseling_service() -> CounselingService:
    global _instance
    if _instance is None:
        _instance = CounselingService()
    return _instance
