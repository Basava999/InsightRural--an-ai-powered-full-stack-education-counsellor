"""Direct test of CollegePredictor to verify data loading and predictions."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_predictor import CollegePredictor

predictor = CollegePredictor()

print(f"Total cutoff_data entries: {len(predictor.cutoff_data)}")
print(f"Total college_data entries: {len(predictor.college_data)}")

# Check if cutoffs are properly loaded
has_cutoffs = 0
has_2024 = 0
has_5yr = 0
for c in predictor.cutoff_data:
    ct = c.get("cutoffs", {})
    yrs = [k for k in ct if k.isdigit()]
    if yrs:
        has_cutoffs += 1
    if "2024" in ct:
        has_2024 += 1
    if len(yrs) >= 5:
        has_5yr += 1

print(f"\nCutoffs loaded in predictor:")
print(f"  With any year cutoffs: {has_cutoffs}")
print(f"  With 2024 cutoffs: {has_2024}")
print(f"  With 5-year cutoffs: {has_5yr}")

# Check trend lookup
print(f"\nTrend lookup entries: {len(predictor.cutoff_trends_lookup)}")
print(f"Placement lookup entries: {len(predictor.placement_lookup)}")
print(f"Fee lookup entries: {len(predictor.fee_lookup)}")

# Run a prediction
print("\n" + "="*60)
print("TEST PREDICTION: Rank 12000, Category 2A, CSE+ECE")
print("="*60)
result = predictor.predict(
    kcet_rank=12000,
    category="2A",
    preferred_branches=["CSE", "ECE", "ISE"],
    top_n=5
)

print(f"Success: {result['success']}")
print(f"Total eligible: {result['total_eligible']}")
print(f"Total colleges checked: {result['total_colleges_checked']}")
print(f"Algorithm: {result['kea_info']['algorithm']}")

for i, p in enumerate(result["predictions"][:5]):
    print(f"\n  {i+1}. {p['college']} — {p['branch']}")
    print(f"     Probability: {p['probability']}% ({p['category']})")
    print(f"     Score: {p['recommendation_score']}/100")
    print(f"     Cutoff: {p['cutoff_rank']}")
    print(f"     Round: {p['predicted_round']}")
    print(f"     Historical: {p.get('historical_cutoffs', {})}")
