# ==============================================================================
# InsightRural — Career Service
# ==============================================================================
# Wraps career simulation and roadmap generation logic.
# ==============================================================================

from typing import Dict, Any, Optional

from core.logging import get_logger

logger = get_logger("services.career")


class CareerService:
    """
    Career guidance service.
    Provides deterministic career paths and LLM-enhanced simulations.
    """

    # Branch → career path mappings
    CAREER_PATHS = {
        "CSE": {
            "roles": ["Software Engineer", "Data Scientist", "AI/ML Engineer", "Full Stack Developer"],
            "avg_salary": "6-12 LPA",
            "top_companies": ["Google", "Microsoft", "Amazon", "Infosys", "TCS", "Wipro"],
            "higher_studies": ["M.Tech CSE", "MS (USA/Germany)", "MBA"],
        },
        "ISE": {
            "roles": ["Software Engineer", "Systems Architect", "DevOps Engineer"],
            "avg_salary": "5-10 LPA",
            "top_companies": ["Infosys", "Wipro", "HCL", "SAP", "Oracle"],
            "higher_studies": ["M.Tech", "MS", "MBA"],
        },
        "ECE": {
            "roles": ["Embedded Engineer", "VLSI Designer", "IoT Developer", "Telecom Engineer"],
            "avg_salary": "4-8 LPA",
            "top_companies": ["Qualcomm", "Intel", "Samsung", "Bosch", "Texas Instruments"],
            "higher_studies": ["M.Tech VLSI", "MS (USA)", "GATE PSU"],
        },
        "MECH": {
            "roles": ["Design Engineer", "Production Engineer", "Automotive Engineer", "R&D"],
            "avg_salary": "3-6 LPA",
            "top_companies": ["Bosch", "L&T", "TATA Motors", "Ashok Leyland", "ISRO"],
            "higher_studies": ["M.Tech", "GATE PSU", "MBA"],
        },
        "CIVIL": {
            "roles": ["Structural Engineer", "Site Engineer", "Urban Planner"],
            "avg_salary": "3-5 LPA",
            "top_companies": ["L&T", "NHAI", "PWD", "Shapoorji Pallonji"],
            "higher_studies": ["M.Tech Structural", "GATE PSU", "UPSC"],
        },
        "MBBS": {
            "roles": ["General Physician", "Surgeon", "Specialist Doctor"],
            "avg_salary": "8-15 LPA",
            "top_companies": ["Apollo", "Manipal", "Narayana Health", "Govt Hospitals"],
            "higher_studies": ["MD/MS", "NEET PG", "Super-specialty"],
        },
    }

    def get_career_info(self, branch: str) -> Dict[str, Any]:
        """Get career information for a specific branch."""
        branch_upper = (branch or "CSE").upper().strip()
        info = self.CAREER_PATHS.get(branch_upper)
        if info:
            return {"branch": branch_upper, **info}
        return {
            "branch": branch_upper,
            "roles": ["Various engineering/professional roles"],
            "avg_salary": "4-8 LPA",
            "top_companies": ["Multiple companies across sectors"],
            "higher_studies": ["M.Tech", "MBA", "MS"],
        }

    def generate_roadmap(
        self,
        branch: str,
        interests: str = "",
        rank: int = 0,
    ) -> Dict[str, Any]:
        """
        Generate a deterministic career roadmap.
        Returns year-wise milestones and expected outcomes.
        """
        career_info = self.get_career_info(branch)

        milestones = [
            {
                "year": "Year 1-2",
                "title": "Foundation",
                "tasks": [
                    f"Build strong fundamentals in {branch}",
                    "Complete 2-3 mini-projects",
                    "Learn programming (Python, SQL minimum)",
                    "Join technical clubs and communities",
                ],
            },
            {
                "year": "Year 2-3",
                "title": "Skill Development",
                "tasks": [
                    "Complete at least 1 internship",
                    "Build portfolio with real projects",
                    "Start competitive programming / Kaggle / research",
                    "Get certifications relevant to your field",
                ],
            },
            {
                "year": "Year 3-4",
                "title": "Placement Preparation",
                "tasks": [
                    "Prepare for campus placements (DSA, aptitude, communication)",
                    "Apply for off-campus opportunities",
                    "Decide on higher studies path (GATE/GRE/CAT/NEET PG)",
                    "Build LinkedIn presence and network",
                ],
            },
            {
                "year": "Year 4+",
                "title": "Launch",
                "tasks": [
                    f"Target companies: {', '.join(career_info.get('top_companies', [])[:4])}",
                    f"Expected salary range: {career_info.get('avg_salary', 'Competitive')}",
                    "Consider startup / freelancing / research paths",
                ],
            },
        ]

        return {
            "branch": branch,
            "career_info": career_info,
            "milestones": milestones,
            "expected_salary": career_info.get("avg_salary", "4-8 LPA"),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[CareerService] = None


def get_career_service() -> CareerService:
    global _instance
    if _instance is None:
        _instance = CareerService()
    return _instance
