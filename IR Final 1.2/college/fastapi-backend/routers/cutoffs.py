from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Adjust import path so we can import database models locally
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, HistoricalCutoff, Program, Institution

router = APIRouter()

from pydantic import BaseModel

class PredictRequest(BaseModel):
    kcet_rank: int
    category: str = "GM"
    preferred_branches: List[str] = []
    budget: Optional[int] = None
    preferred_state: Optional[str] = None

@router.post("/predict")
def predict_colleges(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    """
    Query the relational database to find safe, moderate, and dream colleges.
    """
    query = db.query(HistoricalCutoff, Program, Institution).join(
        Program, HistoricalCutoff.program_id == Program.id
    ).join(
        Institution, Program.institute_id == Institution.id
    ).filter(
        HistoricalCutoff.category == request.category,
        HistoricalCutoff.year == 2024
    )
    
    if request.preferred_branches and len(request.preferred_branches) > 0:
        query = query.filter(Program.branch_name.ilike(f"%{request.preferred_branches[0]}%"))

    results = query.all()
    
    if not results:
        return {"success": False, "predictions": [], "message": "No historical data found for this category/branch."}

    predictions = []
    
    for cutoff, prog, inst in results:
        closing = cutoff.closing_rank
        diff = ((request.kcet_rank - closing) / closing) * 100
        
        # Calculate Probability
        if request.kcet_rank <= closing:
            prob = 90.0 - (diff if diff < 0 else 0)  # Safe
            prob = min(99.0, prob)
            cat_label = "Safe"
            reason = f"Rank is well within the {closing} cutoff."
        elif diff < 10:
            prob = 60.0 - diff  # Moderate
            cat_label = "Moderate"
            reason = f"Rank is close to the {closing} cutoff."
        elif diff < 25:
            prob = 30.0 - diff  # Dream
            cat_label = "Dream"
            reason = f"Stretch target. Cutoff was {closing}."
        else:
            continue
            
        predictions.append({
            "college_id": str(inst.id) + str(prog.id),
            "probability": prob,
            "category": cat_label,
            "location": "Karnataka",
            "college": inst.name,
            "reason": reason,
            "cutoff": closing,
            "placement_avg_lpa": 8.5 + (3.0 / inst.tier), # Dummy placement logic for UI
            "recommendation_score": int(prob + (10 / inst.tier))
        })
            
    predictions.sort(key=lambda x: x["probability"], reverse=True)
    predictions = predictions[:15]

    return {
        "success": True,
        "predictions": predictions
    }
