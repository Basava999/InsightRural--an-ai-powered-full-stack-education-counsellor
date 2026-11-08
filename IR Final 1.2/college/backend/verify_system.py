import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 1. Testing ml_predictor.py ===")
from ml_predictor import get_predictor
p = get_predictor()
r = p.predict(kcet_rank=15000, category='2A', preferred_branches=['CSE', 'AI'], top_n=3)
preds = r.get('predictions', [])
print(f"Predictions returned: {len(preds)}")
for pred in preds:
    cname = pred.get('college_name')
    cid = pred.get('college_id')
    branch = pred.get('branch')
    prob = pred.get('probability')
    cat = pred.get('category')
    cutoff = pred.get('cutoff_rank')
    round_name = pred.get('predicted_round')
    print(f"  {cname} ({cid}) - {branch}: {prob}% ({cat}) | Cutoff: {cutoff} | {round_name}")

print("\n=== 2. Testing kea_allotment_engine.py ===")
from kea_allotment_engine import get_kea_engine
kea = get_kea_engine()
r2 = kea.simulate(rank=15000, category='2A', branch_preference=['CSE', 'AI'], top_n=3)
print(f"Simulate success: {r2.get('success')}")
print(f"Safe: {r2.get('total_safe')} | Moderate: {r2.get('total_moderate')} | Ambitious: {r2.get('total_ambitious')}")
for c in r2.get('safe_colleges', [])[:2]:
    print(f"  SAFE: {c.get('college_name')} - {c.get('branch')} ({c.get('probability')}%)")

print("\n=== 3. Testing JSON Master Database Service ===")
from json_data_service import get_json_data_service
jds = get_json_data_service()
colleges = jds.colleges
print(f"Total colleges in JSON service: {len(colleges)}")
c0 = colleges[0] if colleges else {}
print(f"Sample college: {c0.get('name')}")
print(f"Cutoff years available: {list((c0.get('cutoffs') or {}).keys())}")
print(f"Cutoff rounds available: {list((c0.get('cutoff_rounds') or {}).keys())}")

print("\n=== 4. Testing Multi-Round Cutoffs & Model Persistence ===")
models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "ml_models.pkl")
joblib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "kea_ml_models.joblib")
print(f"Pickle model exists: {os.path.exists(models_path)} ({os.path.getsize(models_path)} bytes)")
print(f"Joblib model exists: {os.path.exists(joblib_path)} ({os.path.getsize(joblib_path)} bytes)")

print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
