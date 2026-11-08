"""Quick test of the ML predictor and KEA engine."""
import sys
import traceback

print("=" * 60)
print("TEST 1: ML Predictor (ml_predictor.py)")
print("=" * 60)
try:
    from ml_predictor import get_predictor
    p = get_predictor()
    r = p.predict(kcet_rank=12000, category='2A', preferred_branches=['CSE', 'ECE'], top_n=3)
    print(f"Success: {r['success']}")
    print(f"Total eligible: {r['total_eligible']}")
    print(f"Predictions: {len(r['predictions'])}")
    for pred in r['predictions']:
        print(f"  {pred['college']} - {pred['branch']} - {pred['probability']}% ({pred['category']})")
    print("[PASS] ML Predictor works!\n")
except Exception as e:
    print(f"[FAIL] ML Predictor error: {e}")
    traceback.print_exc()
    print()

print("=" * 60)
print("TEST 2: KEA Allotment Engine (kea_allotment_engine.py)")
print("=" * 60)
try:
    from kea_allotment_engine import get_kea_engine
    engine = get_kea_engine()
    r = engine.simulate(rank=12000, category='2A', branch_preference=['CSE', 'ECE'], top_n=3)
    print(f"Success: {r['success']}")
    print(f"Safe colleges: {r['total_safe']}")
    print(f"Moderate colleges: {r['total_moderate']}")
    print(f"Ambitious colleges: {r['total_ambitious']}")
    for c in r['safe_colleges'][:2]:
        print(f"  SAFE: {c['college_name']} - {c['branch']} - {c['probability']}%")
    for c in r['moderate_colleges'][:2]:
        print(f"  MODERATE: {c['college_name']} - {c['branch']} - {c['probability']}%")
    print("[PASS] KEA Engine works!\n")
except Exception as e:
    print(f"[FAIL] KEA Engine error: {e}")
    traceback.print_exc()
    print()

print("=" * 60)
print("TEST 3: Flask App Import")
print("=" * 60)
try:
    import app as flask_app
    print(f"[PASS] Flask app imported successfully!")
    print(f"  Routes: {len([r for r in flask_app.app.url_map.iter_rules()])}")
except Exception as e:
    print(f"[FAIL] Flask app import error: {e}")
    traceback.print_exc()
    print()

print("=" * 60)
print("TEST 4: Recommendation Service")
print("=" * 60)
try:
    from json_data_service import get_json_data_service
    from services.recommendation_service import RecommendationService
    from models.schemas import PredictRequest

    json_svc = get_json_data_service()
    rec_svc = RecommendationService(json_svc)
    req = PredictRequest(kcet_rank=12000, preferred_branches=['CSE'], category='GM')
    response = rec_svc.recommend(req.to_student_profile())
    print(f"Safe: {len(response.safe)}, Moderate: {len(response.moderate)}, Ambitious: {len(response.ambitious)}")
    print("[PASS] Recommendation Service works!\n")
except Exception as e:
    print(f"[FAIL] Recommendation Service error: {e}")
    traceback.print_exc()
    print()

print("=" * 60)
print("TEST 5: JEE/NEET Predictors")
print("=" * 60)
try:
    from ml_predictor import get_jee_predictor, get_neet_predictor
    jee = get_jee_predictor()
    neet = get_neet_predictor()
    print(f"JEE cutoff data: {len(jee.cutoff_data)} entries")
    print(f"NEET cutoff data: {len(neet.cutoff_data)} entries")
    print("[PASS] JEE/NEET Predictors loaded!\n")
except Exception as e:
    print(f"[FAIL] JEE/NEET error: {e}")
    traceback.print_exc()
    print()

print("ALL TESTS COMPLETE")
