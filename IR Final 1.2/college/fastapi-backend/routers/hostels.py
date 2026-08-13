from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class HostelRequest(BaseModel):
    city: str
    college_tier: int = 3 # 1=Top, 2=Mid, 3=Low

@router.post("/search")
def search_hostels(request: HostelRequest):
    """
    Returns comparative cost estimates for Govt Hostels vs Private PGs for a city.
    """
    city = request.city.lower()
    
    # Base costs in Karnataka
    if city in ["bangalore", "bengaluru"]:
        cost_multiplier = 1.8
    elif city in ["mysore", "mysuru", "mangalore", "mangaluru"]:
        cost_multiplier = 1.3
    else:
        cost_multiplier = 1.0 # Hubli, Belgaum, etc.

    # Adjust for college tier (Tier 1 colleges usually have slightly more expensive official hostels but better food)
    tier_premium = 0
    if request.college_tier == 1:
        tier_premium = 20000

    results = []

    # 1. Official College Hostel
    results.append({
        "type": "Official College Hostel",
        "avg_annual_cost": int((60000 * cost_multiplier) + tier_premium),
        "deposit": int(20000 * cost_multiplier),
        "food_included": True,
        "pros": ["Inside campus", "Very safe", "Save transport cost", "Good for networking"],
        "cons": ["Strict timings", "Average food quality", "Hard to get (merit based)"],
        "icon": "college"
    })
    
    # 2. Private PG (Paying Guest)
    results.append({
        "type": "Private PG (Shared 2/3 Sharing)",
        "avg_annual_cost": int(85000 * cost_multiplier),
        "deposit": int(15000 * cost_multiplier),
        "food_included": True,
        "pros": ["Flexible timings", "Better food", "Easy to find", "Wi-Fi included usually"],
        "cons": ["Outside campus", "Transport cost", "Variable safety standards", "Electricity extra"],
        "icon": "pg"
    })
    
    # 3. Government / BCM Hostels
    results.append({
        "type": "Government / BCM Hostel",
        "avg_annual_cost": int(15000), # Subsidized, minimal multiplier
        "deposit": 2000,
        "food_included": True,
        "pros": ["Extremely cheap", "Subsidized by government"],
        "cons": ["Very hard to get", "Income limits apply", "Basic facilities", "Often overcrowded"],
        "icon": "govt"
    })
    
    # 4. Independent Flat / Room (Shared)
    results.append({
        "type": "Rented Flat (Shared among 3-4)",
        "avg_annual_cost": int((50000 * cost_multiplier)),
        "deposit": int(40000 * cost_multiplier),
        "food_included": False,
        "pros": ["Complete freedom", "Cook your own food", "Large space"],
        "cons": ["Have to cook/clean yourself", "High deposit", "Utilities extra", "Need reliable roommates"],
        "icon": "flat"
    })

    return {
        "success": True,
        "city": request.city.capitalize(),
        "cost_index": "High" if cost_multiplier > 1.4 else "Medium" if cost_multiplier > 1.1 else "Low",
        "accommodations": results
    }
