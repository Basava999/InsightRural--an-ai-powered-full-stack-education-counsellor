"""
Comprehensive endpoint test for InsightRural backend using Flask test_client.
"""
import sys
import os
import json
import traceback

os.environ["PYTHONIOENCODING"] = "utf-8"

print("=" * 70)
print("INSIGHTRURAL ENDPOINT DIAGNOSTIC TEST")
print("=" * 70)

try:
    from app import app
    client = app.test_client()
    print("[OK] Flask app and test_client created successfully.")
except Exception as e:
    print(f"[FAIL] Could not import app: {e}")
    traceback.print_exc()
    sys.exit(1)

def check_endpoint(name, method, url, json_data=None):
    try:
        if method == "GET":
            res = client.get(url)
        elif method == "POST":
            res = client.post(url, json=json_data or {}, content_type="application/json")
        status = res.status_code
        data = res.get_json(silent=True)
        if status in (200, 201):
            print(f"  [PASS] {name} ({method} {url}) -> {status}")
            return True, data
        else:
            print(f"  [FAIL] {name} ({method} {url}) -> {status}: {res.data[:200]}")
            return False, data
    except Exception as e:
        print(f"  [ERROR] {name} ({method} {url}): {e}")
        traceback.print_exc()
        return False, None

print("\n--- Testing Core Endpoints ---")
check_endpoint("Health check", "GET", "/api/health")

print("\n--- Testing KEA & Predictor Endpoints ---")
# 1. /api/predict/college
p_success, p_data = check_endpoint(
    "Predict College (ML Predictor)", 
    "POST", 
    "/api/predict/college",
    {
        "kcet_rank": 12000,
        "category": "2A",
        "preferred_branches": ["CSE", "ECE"],
        "top_n": 5
    }
)
if p_success and p_data:
    print(f"    Total eligible: {p_data.get('total_eligible')}, Predictions: {len(p_data.get('predictions', []))}")
    if p_data.get("predictions"):
        first = p_data["predictions"][0]
        print(f"    Top: {first.get('college')} | {first.get('branch')} | Prob: {first.get('probability')}% | Tier: {first.get('category')}")

# 2. /api/v2/simulate
s_success, s_data = check_endpoint(
    "KEA Seat Allotment Simulate (v2)",
    "POST",
    "/api/v2/simulate",
    {
        "kcet_rank": 12000,
        "category": "2A",
        "branch_preference": ["CSE", "ECE"],
        "top_n": 5
    }
)
if s_success and s_data:
    print(f"    Safe: {s_data.get('total_safe')}, Moderate: {s_data.get('total_moderate')}, Ambitious: {s_data.get('total_ambitious')}")

# 3. /api/v2/ml-info
check_endpoint("ML Info (v2)", "GET", "/api/v2/ml-info")

# 4. /api/recommend/colleges
check_endpoint(
    "Recommend Colleges",
    "POST",
    "/api/recommend/colleges",
    {
        "kcet_rank": 12000,
        "branch": "CSE",
        "category": "GM"
    }
)

# 5. /api/recommend/scholarships
check_endpoint(
    "Recommend Scholarships",
    "POST",
    "/api/recommend/scholarships",
    {
        "category": "2A",
        "income": 200000
    }
)

# 6. /api/counseling/guide
check_endpoint("Counseling Guide", "GET", "/api/counseling/guide")

print("\n--- Testing Career & Admission Endpoints ---")
# 7. /api/admission-counselor
check_endpoint(
    "Admission Counselor",
    "POST",
    "/api/admission-counselor",
    {
        "message": "What is the cutoff for CSE in RV College?",
        "profile": {"rank": 5000, "category": "GM"}
    }
)

# 8. /api/simulate-career
check_endpoint(
    "Simulate Career",
    "POST",
    "/api/simulate-career",
    {
        "rank": 12000,
        "category": "2A",
        "branch": "CSE",
        "interests": ["Machine Learning", "Software Development"]
    }
)

print("\n--- Testing Scholarship Generator Endpoints ---")
# 9. /api/scholarships/generate-essay
e_success, e_data = check_endpoint(
    "Scholarship Essay Gen",
    "POST",
    "/api/scholarships/generate-essay",
    {
        "student_data": {"name": "Test Student", "course": "BE CSE"},
        "scholarship_name": "Vidyasiri",
        "reason": "Financial need for rural student"
    }
)

# 10. /api/scholarships/download-pdf
if e_success and e_data:
    check_endpoint(
        "Scholarship Download PDF",
        "POST",
        "/api/scholarships/download-pdf",
        {
            "student_data": {"name": "Test Student"},
            "essay": e_data.get("essay", "Sample essay")
        }
    )

print("\n--- Testing PDF Report Generation ---")
# 11. /api/report/generate
if p_success and p_data:
    check_endpoint(
        "PDF Report Generation",
        "POST",
        "/api/report/generate",
        {
            "prediction_result": p_data,
            "student_profile": {
                "kcet_rank": 12000,
                "category": "2A",
                "preferred_branches": ["CSE", "ECE"]
            }
        }
    )

print("\n--- Testing AI Chat Endpoint ---")
check_endpoint(
    "AI Chat",
    "POST",
    "/api/chat",
    {
        "message": "Hello, which colleges can I get with KCET rank 10000 in CSE?",
        "language": "en"
    }
)

print("\n" + "=" * 70)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 70)
