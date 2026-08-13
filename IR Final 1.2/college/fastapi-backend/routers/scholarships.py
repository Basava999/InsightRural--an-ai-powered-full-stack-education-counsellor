from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ScholarshipRequest(BaseModel):
    family_income: int
    category: str
    gender: str = "Male"
    state: str = "Karnataka"
    tenth_marks: Optional[float] = None
    twelfth_marks: Optional[float] = None

@router.post("/match")
def match_scholarships(request: ScholarshipRequest):
    """
    Simulates checking a database of scholarships and returning matching ones.
    """
    matches = []
    
    income = request.family_income
    category = request.category.upper()
    
    # 1. SNQ Quota (Supernumerary Quota for Karnataka)
    if income < 450000 and request.state.lower() == "karnataka":
        matches.append({
            "id": "snq-01",
            "name": "Supernumerary Quota (SNQ)",
            "provider": "KEA / Govt of Karnataka",
            "amount": "100% Tuition Fee Waiver",
            "eligibility": "Family income < ₹4.5 Lakhs. Karnataka Student.",
            "deadline": "At the time of KCET Option Entry",
            "difficulty": "Hard (Merit Based)"
        })
        
    # 2. SSP Post Matric (Karnataka)
    if request.state.lower() == "karnataka":
        if category in ["SC", "ST"] and income <= 250000:
            matches.append({
                "id": "ssp-scst",
                "name": "SSP Post Matric Scholarship (SC/ST)",
                "provider": "Social Welfare Department, Karnataka",
                "amount": "Full Tuition + Hostel Fees (approx ₹50k-₹1L/yr)",
                "eligibility": "SC/ST with family income < ₹2.5 Lakhs.",
                "deadline": "Usually November/December",
                "difficulty": "Easy (Guaranteed if eligible)"
            })
        elif category in ["OBC", "2A", "2B", "3A", "3B"] and income <= 100000:
             matches.append({
                "id": "ssp-obc",
                "name": "Vidyasiri / SSP Post Matric (OBC)",
                "provider": "Backward Classes Welfare Department",
                "amount": "₹15,000 to ₹35,000 / year",
                "eligibility": "OBC category, income < ₹1 Lakh.",
                "deadline": "Usually November/December",
                "difficulty": "Easy"
            })
             
    # 3. Pragati Scholarship (For Girls)
    if request.gender.lower() == "female" and income < 800000:
        matches.append({
            "id": "aicte-pragati",
            "name": "AICTE Pragati Scholarship for Girls",
            "provider": "AICTE (Central Govt)",
            "amount": "₹50,000 / year",
            "eligibility": "Girl student in 1st year Engineering. Income < ₹8 Lakhs.",
            "deadline": "October/November via NSP Portal",
            "difficulty": "Moderate"
        })
        
    # 4. Central Sector Scheme (NSP)
    if request.twelfth_marks and request.twelfth_marks >= 80 and income < 450000:
        matches.append({
            "id": "nsp-css",
            "name": "Central Sector Scheme of Scholarship",
            "provider": "MHRD (National Scholarship Portal)",
            "amount": "₹10,000 / year for UG",
            "eligibility": "Top 20th percentile in 12th board. Income < ₹4.5 Lakhs.",
            "deadline": "October",
            "difficulty": "Hard (Merit Based)"
        })
        
    # 5. FFE Scholarship (Foundation for Excellence)
    if request.twelfth_marks and request.twelfth_marks >= 70 and income < 300000:
        matches.append({
            "id": "ffe-01",
            "name": "Foundation for Excellence (FFE)",
            "provider": "Private NGO",
            "amount": "₹40,000 to ₹50,000 / year",
            "eligibility": "Professional degree students. Income < ₹3 Lakhs.",
            "deadline": "December",
            "difficulty": "Moderate"
        })

    # Sort by "Easy" to "Hard" for UX
    difficulty_order = {"Easy": 1, "Easy (Guaranteed if eligible)": 1, "Moderate": 2, "Hard (Merit Based)": 3}
    matches.sort(key=lambda x: difficulty_order.get(x["difficulty"], 99))

    return {
        "success": True,
        "total_matches": len(matches),
        "scholarships": matches
    }
