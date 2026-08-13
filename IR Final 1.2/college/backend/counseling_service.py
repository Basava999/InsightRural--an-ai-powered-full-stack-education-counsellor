import json
import os

# Load college data once
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_colleges_data():
    path = os.path.join(DATA_DIR, 'Production_Ready_Colleges.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading college data: {e}")
        return []

def get_counseling_guide():
    path = os.path.join(DATA_DIR, 'counseling_guide.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading counseling guide: {e}")
        return {}

def generate_option_entry_list(rank, category, branches):
    """
    Generate a prioritized list of colleges for Option Entry using the upgraded ML Predictor.
    Buckets:
    - Ambitious (Red): ML Probability 'Dream'
    - Realistic (Yellow): ML Probability 'Moderate'
    - Safe (Green): ML Probability 'Safe'
    """
    try:
        from ml_predictor import get_predictor
        predictor = get_predictor()
    except ImportError as e:
        print(f"Error importing ml_predictor: {e}")
        return {"summary": {"total_options": 0, "safe_count": 0, "realistic_count": 0, "ambitious_count": 0}, "options": []}
    
    # Predict using the new ML pipeline (top_n=50 for a broad option list)
    if not isinstance(branches, list):
        branches = [branches]
        
    result = predictor.predict(
        kcet_rank=int(rank),
        category=category,
        preferred_branches=branches,
        top_n=50
    )
    
    if not result.get("success", False):
        print(f"Prediction failed: {result.get('error', 'Unknown error')}")
        return {"summary": {"total_options": 0, "safe_count": 0, "realistic_count": 0, "ambitious_count": 0}, "options": []}
    
    options = []
    recs = result.get("predictions", [])
    
    safe_count = 0
    realistic_count = 0
    ambitious_count = 0
    
    for rec in recs:
        # Map ML Predictor labels to frontend expected types
        label = rec.get("admission_chance", "Moderate")
        
        if label == "Safe":
            prob_type = "safe"
            chance = "Safe"
            safe_count += 1
        elif label == "Moderate":
            prob_type = "realistic"
            chance = "Realistic"
            realistic_count += 1
        else:
            prob_type = "ambitious"
            chance = "Ambitious"
            ambitious_count += 1
            
        options.append({
            "college_name": rec.get("college_name"),
            "college_code": rec.get("college_id", "N/A"),
            "branch": rec.get("branch"),
            "cutoff": rec.get("predicted_cutoff", "N/A"),
            "location": rec.get("location", "N/A"),
            "fee": "N/A",  # Could be added if needed, UI hides it mostly
            "chance": chance,
            "type": prob_type,
            "score": rec.get("recommendation_score", 0)
        })
        
    # Sort purely by Cutoff (Ascending implies Quality) for the Option Entry List
    options.sort(key=lambda x: x['cutoff'] if isinstance(x['cutoff'], (int, float)) else 999999)
    
    # Add temporary sequence number
    for idx, opt in enumerate(options, 1):
        opt['sequence'] = idx
        
    return {
        "summary": {
            "total_options": len(options),
            "safe_count": safe_count,
            "realistic_count": realistic_count,
            "ambitious_count": ambitious_count
        },
        "options": options
    }

