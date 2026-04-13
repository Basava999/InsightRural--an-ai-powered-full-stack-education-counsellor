import json
import os

# Load college data once
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_colleges_data():
    path = os.path.join(DATA_DIR, 'kea_colleges_complete.json')
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
    Generate a prioritized list of colleges for Option Entry.
    Buckets:
    - Ambitious (Red): Cutoff < Rank (Hard to get, but try)
    - Realistic (Yellow): Cutoff approx == Rank (High chance)
    - Safe (Green): Cutoff > Rank (Guaranteed backup)
    """
    colleges = get_colleges_data()
    options = []
    
    # Standardize inputs
    rank = int(rank)
    if not isinstance(branches, list):
        branches = [branches]
    
    # Map KEA category codes to cutoff_2024 keys (data uses GM, OBC, SC, ST)
    category_lookup = category
    if category in ("2A", "2B", "3A", "3B", "OBC"):
        category_lookup = "OBC"
    elif category in ("GM", "General", "1G"):
        category_lookup = "GM"
    
    for college in colleges:
        cutoffs = college.get('cutoff_2024', {})
        
        for branch in branches:
            if branch in cutoffs:
                branch_data = cutoffs[branch]
                # Get cutoff for category, fallback to GM, then infinite
                cutoff_rank = branch_data.get(category_lookup) or branch_data.get(category)
                if not cutoff_rank:
                    cutoff_rank = branch_data.get("GM", 999999)
                
                # Logic for categorization
                chance = "Unknown"
                color = "gray"
                
                # Deviation factor
                # Ambitious: Cutoff is 70% to 100% of User Rank (e.g. Rank 10k, Cutoff 7k-10k)
                # Matches: Cutoff is 100% to 120% of User Rank (e.g. Rank 10k, Cutoff 10k-12k)
                # Safe: Cutoff > 120% of User Rank (e.g. Rank 10k, Cutoff > 12k)
                
                if cutoff_rank < rank * 0.7:
                    chance = "Dream (Very Hard)"
                    prob_type = "dream" # Too hard, maybe skip? or keep as top priority
                elif rank * 0.7 <= cutoff_rank < rank:
                    chance = "Ambitious"
                    prob_type = "ambitious"
                elif rank <= cutoff_rank <= rank * 1.3:
                    chance = "Realistic"
                    prob_type = "realistic"
                else:
                    chance = "Safe"
                    prob_type = "safe"

                option = {
                    "college_name": college['name'],
                    "college_code": college['college_id'],
                    "branch": branch,
                    "cutoff": cutoff_rank,
                    "location": college['location'],
                    "fee": college.get('annual_fee', {}).get(category.lower(), 'N/A'),
                    "chance": chance,
                    "type": prob_type
                }
                
                # Filter out impossible ones (e.g. Rank 50k trying for RVCE CSE cutoff 500)
                # Logic: Only show if cutoff is at least 20% of rank? 
                # Actually for Option Entry, students should put top colleges first anyway.
                # So we include everything, but sorted intelligently.
                options.append(option)

    # Sorting Logic for Option Entry
    # 1. First sort by Preference buckets: Dream -> Ambitious -> Realistic -> Safe
    #    Actually Option Entry should be ordered by Quality (Cutoff), not probability.
    #    Because if you put Safe college 1st, you get it and lose chance for Ambitious.
    #    The "correct" order is always best college first.
    
    # Sort purely by Cutoff (Ascending implies Quality)
    options.sort(key=lambda x: x['cutoff'])
    
    # Add temporary sequence number
    for idx, opt in enumerate(options, 1):
        opt['sequence'] = idx
        
    return {
        "summary": {
            "total_options": len(options),
            "safe_count": len([x for x in options if x['type'] == 'safe']),
            "realistic_count": len([x for x in options if x['type'] == 'realistic']),
            "ambitious_count": len([x for x in options if x['type'] in ['ambitious', 'dream']])
        },
        "options": options
    }
