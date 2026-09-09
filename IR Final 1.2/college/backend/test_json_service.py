"""
Quick validation test for the JSON Data Service.
Run from the backend directory: python test_json_service.py
"""
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from json_data_service import get_json_data_service

def test_service():
    svc = get_json_data_service()
    print("=" * 60)
    print("JSON DATA SERVICE VALIDATION")
    print("=" * 60)

    # Test 1: College lookup
    print("\n--- TEST 1: Find college 'RVCE' ---")
    college = svc.find_college("rvce")
    if college:
        print(f"  Found: {college.get('name')} ({college.get('location')})")
        print(f"  Cutoff CSE GM 2024: {college.get('cutoff_2024', {}).get('CSE', {}).get('GM', 'N/A')}")
        print(f"  Fee GM: {college.get('annual_fee', {}).get('gm', 'N/A')}")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - College not found")

    # Test 2: College recommendations
    print("\n--- TEST 2: Recommend for Rank 5000, CSE, GM ---")
    results = svc.recommend_colleges(rank=5000, branch="CSE", category="GM")
    safe_count = len(results["safe"])
    mod_count = len(results["moderate"])
    amb_count = len(results["ambitious"])
    print(f"  Safe: {safe_count}, Moderate: {mod_count}, Ambitious: {amb_count}")
    if safe_count + mod_count + amb_count > 0:
        if results["safe"]:
            top = results["safe"][0]
            print(f"  Top Safe: {top['name']} (cutoff: {top['cutoff_rank']}, fee: {top['annual_fee']})")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - No recommendations found")

    # Test 3: Recommendations for SC category
    print("\n--- TEST 3: Recommend for Rank 10000, CSE, SC ---")
    results = svc.recommend_colleges(rank=10000, branch="CSE", category="SC")
    total = sum(len(results[t]) for t in ("safe", "moderate", "ambitious"))
    print(f"  Total matches: {total}")
    if total > 0:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

    # Test 4: Fee structure
    print("\n--- TEST 4: Fee structure for 'RVCE' ---")
    fee_info = svc.get_fee_structure(college_name="rvce")
    if fee_info and "₹" in fee_info:
        print(f"  {fee_info[:200]}...")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - No fee info")

    # Test 5: Hostel lookup
    print("\n--- TEST 5: Hostel info for 'Siddaganga' ---")
    hostel_info = svc.get_hostel_info(college_name="siddaganga")
    if hostel_info and "₹" in hostel_info:
        print(f"  Found hostel data ({len(hostel_info)} chars)")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - No hostel info")

    # Test 6: Scholarship lookup
    print("\n--- TEST 6: Scholarships for SC, income 200000 ---")
    schol_info = svc.get_scholarships(category="SC", income=200000)
    if schol_info:
        print(f"  Found scholarship data ({len(schol_info)} chars)")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - No scholarship info")

    # Test 7: Loans
    print("\n--- TEST 7: Education loans ---")
    loan_info = svc.get_loans(income=200000)
    if loan_info and "SBI" in loan_info:
        print(f"  Found loan data ({len(loan_info)} chars)")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

    # Test 8: Context builder
    print("\n--- TEST 8: Context for 'which college for rank 3000 CSE' ---")
    context = svc.build_context_for_query(
        "which college can I get for rank 3000 in CSE",
        {"kcet_rank": 3000, "branch": "CSE", "category": "GM"}
    )
    if context and "PRIORITY 1" in context:
        print(f"  Context built: {len(context)} chars")
        print(f"  Contains PRIORITY 1 header: ✅")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

    # Test 9: Hostel for BCM category
    print("\n--- TEST 9: BCM hostels for OBC students ---")
    hostel_info = svc.get_hostel_info(category="OBC")
    if hostel_info and "BCM" in hostel_info:
        print(f"  Found BCM hostel data")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

    # Test 10: Cutoff trends
    print("\n--- TEST 10: Cutoff trends for RVCE CSE GM ---")
    trends = svc.get_cutoff_trends("rvce", "CSE", "GM")
    if trends and "2024" in trends:
        print(f"  Found trend data with 2024")
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_service()
