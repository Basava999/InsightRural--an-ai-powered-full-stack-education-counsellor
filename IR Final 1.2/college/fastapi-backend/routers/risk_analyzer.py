from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hybrid_predictor import HybridIntelligencePredictor

router = APIRouter()

class RiskAnalysisRequest(BaseModel):
    rank: int
    college: str
    college_tier: int
    branch: str
    fees: float
    hostel_fees: float
    income: float
    marks: float
    skills: List[str]
    interests: List[str]
    loan_required: bool
    has_scholarship: bool
    historical_closing_rank: Optional[int] = None

@router.post("/risk")
def analyze_risk(request: RiskAnalysisRequest):
    """
    Executes the Hybrid Intelligence Risk Engine using the student's profile.
    """
    engine = HybridIntelligencePredictor()
    
    # Query database or default the closing rank
    historical_rank = request.historical_closing_rank or (request.rank - 500)
    
    profile_data = {
        "rank": request.rank,
        "historical_closing_rank": historical_rank,
        "income": request.income,
        "fees": request.fees,
        "hostel_fees": request.hostel_fees,
        "loan_required": request.loan_required,
        "has_scholarship": request.has_scholarship,
        "skills": request.skills,
        "interests": request.interests,
        "branch": request.branch,
        "college_tier": request.college_tier,
        "gender": "Male", # Default fallback
        "state": "Karnataka" # Default fallback
    }
    
    risk_results = engine.calculate_compound_risk(profile_data)
    
    # Generate LLM Explanation based on the math
    explanation = (
        f"Based on your profile, your Overall Success Score is {risk_results['success_score']}/100. "
        f"You have a {risk_results['components']['academic']['level']} Academic Risk because your rank "
        f"is {risk_results['components']['academic']['reasoning'].lower()} "
        f"Financially, this choice presents a {risk_results['components']['financial']['level']} risk—"
        f"{risk_results['components']['financial']['reasoning'].lower()} "
        f"Finally, your career alignment is {risk_results['components']['career']['level']} for {request.branch}. "
        f"ROI is rated {risk_results['components']['roi']['level']}: {risk_results['components']['roi']['reasoning']} "
        f"Placement risk is {risk_results['components']['placement']['level']} ({risk_results['components']['placement']['reasoning'].lower()})."
    )
    
    return {
        "success": True,
        "risk_analysis": {
            "success_score": risk_results["success_score"],
            "compound_risk": risk_results["compound_risk_score"],
            "regret_probability": risk_results["regret_probability"],
            "academic_risk": risk_results["components"]["academic"]["level"],
            "financial_risk": risk_results["components"]["financial"]["level"],
            "placement_risk": risk_results["components"]["placement"]["level"],
            "career_alignment_score": risk_results["components"]["career"]["score"],
            "branch_compatibility_score": risk_results["components"]["career"]["score"],
            "college_roi_score": risk_results["components"]["roi"]["score"],
            "scholarship_opportunity_score": risk_results["components"]["scholarship_opp"]["score"]
        },
        "ai_explanation": explanation
    }
