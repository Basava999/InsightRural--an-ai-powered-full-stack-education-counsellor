from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

class CareerRequest(BaseModel):
    interests: str
    skills: List[str] = []
    proposed_branch: str

@router.post("/simulate")
def simulate_career(request: CareerRequest):
    """
    Simulates career outcomes based on interests, skills, and the proposed branch.
    For this startup demo, we use a hybrid of static logic and semi-randomization, 
    but in production, this would query historical placement databases.
    """
    branch = request.proposed_branch.upper()
    interests = request.interests.lower()
    
    # Calculate a baseline compatibility score based on branch and interests
    score = 50
    if branch == "CSE" or branch == "AI":
        if any(w in interests for w in ["coding", "programming", "software", "computers", "ai", "tech"]):
            score += 35
        elif "games" in interests:
            score += 20
    elif branch == "ECE" or branch == "EE":
        if any(w in interests for w in ["electronics", "hardware", "circuits", "robotics"]):
            score += 40
        elif "math" in interests:
            score += 15
    elif branch == "MECH" or branch == "CIVIL":
        if any(w in interests for w in ["building", "machines", "cars", "construction", "physics"]):
            score += 40
            
    # Add minor boost for matching skills
    score += len(request.skills) * 2
    
    # Cap score between 30 and 98
    compatibility_score = min(max(int(score + random.randint(-5, 5)), 30), 98)
    
    # Salary Projections (Y1 to Y5)
    base_salary = 4.5
    if branch in ["CSE", "AI"]:
        base_salary = 8.5
    elif branch in ["ECE", "ISE"]:
        base_salary = 6.0
        
    salary_projection = []
    for year in range(1, 6):
        growth = 1.0 + (year * 0.15)
        # Adjust growth based on compatibility (people who like their job get promoted faster)
        comp_multiplier = compatibility_score / 70.0
        salary_projection.append({
            "year": f"Year {year}",
            "low": round((base_salary * 0.7) * growth, 1),
            "median": round(base_salary * growth * comp_multiplier, 1),
            "high": round((base_salary * 1.5) * growth * (comp_multiplier * 1.2), 1)
        })
        
    # Top Recruiters
    recruiters = {
        "CSE": ["Google", "Microsoft", "Amazon", "TCS Digital", "Infosys"],
        "AI": ["OpenAI", "Nvidia", "Google", "Meta", "Accenture"],
        "ECE": ["Intel", "Qualcomm", "Texas Instruments", "Samsung", "Bosch"],
        "MECH": ["Tata Motors", "Mahindra", "Boeing", "L&T", "Bosch"],
        "CIVIL": ["L&T Construction", "Tata Projects", "Godrej Properties", "Shapoorji Pallonji"],
        "ISE": ["Amazon", "Flipkart", "Walmart Labs", "TCS", "Wipro"]
    }
    
    top_recruiters = recruiters.get(branch, ["TCS", "Infosys", "Wipro", "Cognizant"])
    
    # Alternative Branches (if score is low)
    alternatives = []
    if compatibility_score < 60:
        if branch == "CSE": alternatives = ["ISE", "ECE (Software Track)"]
        elif branch == "ECE": alternatives = ["CSE", "EE"]
        elif branch == "MECH": alternatives = ["Industrial Engineering", "Automobile"]
        elif branch == "CIVIL": alternatives = ["Architecture", "Environmental Engineering"]
        elif branch == "AI": alternatives = ["CSE", "Data Science"]
    
    return {
        "success": True,
        "branch": branch,
        "compatibility_score": compatibility_score,
        "salary_projection": salary_projection,
        "top_recruiters": top_recruiters,
        "alternatives": alternatives
    }
