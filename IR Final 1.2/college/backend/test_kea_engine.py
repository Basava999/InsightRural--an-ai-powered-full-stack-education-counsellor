"""
Quick validation test for the KEA Seat Allotment Simulation Engine.
Run: python test_kea_engine.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kea_allotment_engine import get_kea_engine

def test_engine():
    print("=" * 70)
    print("KEA SEAT ALLOTMENT ENGINE VALIDATION")
    print("=" * 70)

    start = time.time()
    engine = get_kea_engine()
    init_time = time.time() - start
    print(f"\nInit time: {init_time:.2f}s")
    print(f"Colleges loaded: {len(engine.colleges)}")
    print(f"ML trained: {engine.ml_engine.is_trained}")
    print(f"Best ML model: {engine.ml_engine.best_model_name or 'Rule-based'}")

    if engine.ml_engine.metrics:
        print("\n--- ML Model Comparison ---")
        for name, metrics in engine.ml_engine.metrics.items():
            if "mae" in metrics:
                print(f"  {name}: MAE={metrics['mae']}, RMSE={metrics['rmse']}, "
                      f"R2={metrics['r2']}, CV-MAE={metrics['cv_mae']}")

    # Test 1: Simulate for Rank 5000 CSE GM
    print("\n--- TEST 1: Rank 5000, CSE, GM ---")
    start = time.time()
    result = engine.simulate(rank=5000, category="GM", branch_preference=["CSE"])
    sim_time = time.time() - start
    print(f"  Time: {sim_time:.2f}s")
    print(f"  Safe: {result['total_safe']}, Moderate: {result['total_moderate']}, "
          f"Ambitious: {result['total_ambitious']}")
    if result["safe_colleges"]:
        top = result["safe_colleges"][0]
        print(f"  Top Safe: {top['college_name']} ({top['location']}) "
              f"Prob: {top['probability']}%, Cutoff: {top['cutoff_rank']}")
    print(f"  PASS" if result["total_safe"] + result["total_moderate"] > 0 else "  FAIL")

    # Test 2: Simulate for SC category
    print("\n--- TEST 2: Rank 15000, CSE, SC ---")
    result = engine.simulate(rank=15000, category="SC", branch_preference=["CSE", "ECE"])
    print(f"  Safe: {result['total_safe']}, Moderate: {result['total_moderate']}")
    print(f"  Reservation: {result['candidate_profile']['reservation_benefit']}")
    if result["safe_colleges"]:
        top = result["safe_colleges"][0]
        print(f"  Top: {top['college_name']} Prob: {top['probability']}% "
              f"Benefits: {top.get('reservation_benefits', [])}")
    print(f"  PASS" if result["total_safe"] > 0 else "  FAIL")

    # Test 3: Rural + Kannada Medium + 371J
    print("\n--- TEST 3: Rank 20000, ECE, 2A + Rural + KM ---")
    result = engine.simulate(
        rank=20000, category="2A",
        branch_preference=["ECE", "EEE"],
        rural_quota=True, kannada_medium=True,
    )
    print(f"  Safe: {result['total_safe']}, Moderate: {result['total_moderate']}")
    print(f"  Eligible quotas: {result['candidate_profile']['eligible_quotas']}")
    if result["safe_colleges"]:
        top = result["safe_colleges"][0]
        print(f"  Top: {top['college_name']} Benefits: {top.get('reservation_benefits', [])}")
    print(f"  PASS" if result["total_safe"] > 0 else "  FAIL")

    # Test 4: Cutoff prediction
    print("\n--- TEST 4: Predict cutoff for UVCE CSE GM ---")
    pred = engine.predict_cutoff("E001", "CSE", "GM")
    print(f"  Predicted 2025: {pred['predicted']}")
    print(f"  ML predicted: {pred.get('ml_predicted', 'N/A')}")
    print(f"  Trend predicted: {pred.get('trend_predicted', 'N/A')}")
    print(f"  Confidence: {pred['confidence']['label']} ({pred['confidence']['score']})")
    print(f"  Trend: {pred['trend'].get('demand_label', 'N/A')}")
    print(f"  PASS" if pred["predicted"] > 0 else "  FAIL")

    # Test 5: Option entry strategy
    print("\n--- TEST 5: Option entry sequence ---")
    result = engine.simulate(rank=8000, category="GM", branch_preference=["CSE", "ISE", "ECE"])
    seq = result.get("option_entry_sequence", [])
    print(f"  Options generated: {len(seq)}")
    for s in seq[:5]:
        print(f"  #{s['priority']} {s['college']} | {s['branch']} | {s['tier']} | {s['probability']}")
    print(f"  PASS" if len(seq) > 0 else "  FAIL")

    # Test 6: Chat context builder
    print("\n--- TEST 6: Chat context for rank 3000 CSE ---")
    ctx = engine.build_chat_context(rank=3000, category="GM", branch="CSE")
    print(f"  Context length: {len(ctx)} chars")
    print(f"  Contains SAFE: {'SAFE' in ctx}")
    print(f"  Contains simulation header: {'SIMULATION' in ctx}")
    print(f"  PASS" if len(ctx) > 200 else "  FAIL")

    # Test 7: Budget filter
    print("\n--- TEST 7: Budget filter (max 50000/yr) ---")
    result = engine.simulate(rank=5000, category="GM", branch_preference=["CSE"], budget=50000)
    govt_count = sum(1 for c in result["safe_colleges"] if "Government" in c.get("college_type", ""))
    print(f"  Total results: {result['total_safe'] + result['total_moderate']}")
    print(f"  Government colleges in safe: {govt_count}")
    print(f"  PASS" if result['total_safe'] + result['total_moderate'] >= 0 else "  FAIL")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_engine()
