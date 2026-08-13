"""
Risk Analyzer Service — Wrapper that bridges the old API with the new engine.
Keeps backward compatibility with any code that imports from risk_analyzer_service.
"""
import json
import os
from risk_analyzer import analyze_risk, generate_ai_explanation

try:
    from db_models import SessionLocal, StudentRiskProfile
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class RiskAnalyzerEngine:
    """Backward-compatible wrapper around the new analyze_risk() engine."""

    def __init__(self):
        pass

    def analyze_student(self, data):
        """Main entry point for risk analysis. Returns the full report."""
        # Run the new 11-dimensional engine
        report = analyze_risk(data)

        # Generate AI explanation
        ai_explanation = generate_ai_explanation(data, report)
        report["ai_explanation"] = ai_explanation

        # Save to DB
        self._save_to_db(data, report)

        return report

    def _save_to_db(self, data, report):
        if not DB_AVAILABLE:
            return
        db = SessionLocal()
        try:
            interests = data.get("interests", "")
            if isinstance(interests, list):
                interests = ", ".join(interests)

            income_raw = float(data.get("income", 0))
            income_lakhs = income_raw / 100000 if income_raw > 100 else income_raw

            profile = StudentRiskProfile(
                rank=int(data.get("rank", 0)) if data.get("rank") else None,
                category=data.get("category", ""),
                income_lakhs=income_lakhs,
                interests=interests,
                career_goals=data.get("career_goals", ""),
                preferred_branches=data.get("branch", ""),
                success_score=report.get("success_score"),
                academic_risk=report.get("academic_risk"),
                financial_risk=report.get("financial_risk"),
                placement_risk=report.get("placement_risk"),
                regret_probability=report.get("regret_probability"),
                branch_compatibility_score=report.get("branch_compatibility_score"),
                roi_score=report.get("roi_label", ""),
                ai_explanation=report.get("ai_explanation", "")
            )
            db.add(profile)
            db.commit()
        except Exception as e:
            print(f"Error saving risk profile: {e}")
            db.rollback()
        finally:
            db.close()


# Singleton instance
risk_analyzer = RiskAnalyzerEngine()
