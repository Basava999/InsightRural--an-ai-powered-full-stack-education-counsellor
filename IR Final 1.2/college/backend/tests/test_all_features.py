"""
InsightRural - Comprehensive feature test.
Run from backend folder: python -m tests.test_all_features
Or: cd backend && python -m tests.test_all_features
"""
import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    from app import app
    client = app.test_client()
    results = []

    def test(name, method, url, expected_status=200, json_body=None, form_data=None, accept_optional=None):
        """accept_optional: tuple of status codes to accept (e.g. (200, 503) for optional services)."""
        try:
            if method == 'GET':
                r = client.get(url)
            elif method == 'POST':
                if json_body is not None:
                    r = client.post(url, json=json_body, content_type='application/json')
                elif form_data is not None:
                    r = client.post(url, data=form_data)
                else:
                    r = client.post(url, json={}, content_type='application/json')
            else:
                raise ValueError(method)
            allowed = (expected_status,) if accept_optional is None else accept_optional
            ok = r.status_code in allowed
            results.append((name, ok, r.status_code, getattr(r, 'get_data', lambda: b'')()[:100]))
            return ok, r
        except Exception as e:
            results.append((name, False, str(e), None))
            return False, None

    # ---- Core data ----
    test("GET /api/health", "GET", "/api/health")
    test("GET /api/colleges", "GET", "/api/colleges?limit=5")
    test("GET /api/colleges with filters", "GET", "/api/colleges?q=engineering&branch=CSE&limit=5")
    test("GET /api/branches", "GET", "/api/branches")
    test("GET /api/locations", "GET", "/api/locations")
    test("GET /api/statistics", "GET", "/api/statistics")
    test("GET /api/search/suggestions (short q)", "GET", "/api/search/suggestions?q=a")  # < 2 chars -> []
    test("GET /api/search/suggestions", "GET", "/api/search/suggestions?q=eng")
    test("GET /api/debug", "GET", "/api/debug")

    # Get a real college_id and fee category for next tests
    r = client.get("/api/colleges?limit=1")
    if r.status_code == 200:
        data = r.get_json()
        items = data.get("items", [])
        if items:
            cid = items[0].get("college_id") or items[0].get("id")
            fee_cat = items[0].get("fee_category")
            if cid:
                test("GET /api/colleges/<id>", "GET", f"/api/colleges/{cid}")
            if fee_cat:
                from urllib.parse import quote
                test("GET /api/fees/<category>", "GET", f"/api/fees/{quote(fee_cat)}")

    # ---- Profile ----
    test("GET /api/profile", "GET", "/api/profile?session_id=test")
    test("POST /api/profile", "POST", "/api/profile?session_id=test", json_body={"kcet_rank": 5000, "category": "GM"})

    # ---- AI / Chat (may 200 or 500 if no API key) ----
    test("POST /api/chat no body", "POST", "/api/chat", expected_status=400)
    test("POST /api/chat with message", "POST", "/api/chat", json_body={"message": "What colleges for rank 5000?"}, accept_optional=(200, 500))
    test("GET /api/ai/status", "GET", "/api/ai/status")

    # ---- Recommend (use fallback if no RAG) ----
    test("POST /api/recommend/colleges", "POST", "/api/recommend/colleges", json_body={
        "kcet_rank": 5000, "branch": "CSE", "category": "GM"
    })
    test("POST /api/recommend/scholarships", "POST", "/api/recommend/scholarships", json_body={
        "category": "SC", "income": 200000
    })

    # ---- ML Predict ----
    test("GET /api/predict/status", "GET", "/api/predict/status")
    test("POST /api/predict/college missing fields", "POST", "/api/predict/college", json_body={}, expected_status=400)
    test("POST /api/predict/college", "POST", "/api/predict/college", json_body={
        "kcet_rank": 5000, "category": "GM", "preferred_branches": ["CSE"]
    }, accept_optional=(200, 503))

    # ---- PDF Report ----
    test("GET /api/report/status", "GET", "/api/report/status")
    test("POST /api/report/generate missing body", "POST", "/api/report/generate", expected_status=400)
    # Valid report needs prediction_result + student_profile
    fake_pred = {"predictions": [{"college_name": "Test", "branch": "CSE", "location": "BLR", "cutoff_rank": 5000, "annual_fee": 100000, "probability": 80, "category": "Safe"}], "total_eligible": 1, "option_entry_sequence": [{"college": "Test", "branch": "CSE", "category": "Safe"}], "counselling_guidance": {}}
    fake_profile = {"kcet_rank": 5000, "category": "GM", "preferred_branches": ["CSE"]}
    test("POST /api/report/generate", "POST", "/api/report/generate", json_body={"prediction_result": fake_pred, "student_profile": fake_profile}, accept_optional=(200, 503))

    # ---- Document scanner ----
    test("POST /api/documents/scan no image", "POST", "/api/documents/scan", json_body={}, expected_status=400)
    test("POST /api/documents/scan", "POST", "/api/documents/scan", json_body={"image": "dGVzdA==", "document_type": "marksheet"}, accept_optional=(200, 503))

    # ---- Counseling ----
    test("GET /api/counseling/guide", "GET", "/api/counseling/guide", accept_optional=(200, 503))
    test("POST /api/counseling/generate-options no rank", "POST", "/api/counseling/generate-options", json_body={}, expected_status=400)
    test("POST /api/counseling/generate-options", "POST", "/api/counseling/generate-options", json_body={"rank": 5000, "category": "GM", "branches": ["CSE"]}, accept_optional=(200, 503))

    # ---- Scholarships ----
    test("POST /api/scholarships/generate-essay", "POST", "/api/scholarships/generate-essay", json_body={
        "student_data": {"name": "Test", "income": "2 Lakh"}, "scholarship": "Test Scholarship", "reason": "Need"
    }, accept_optional=(200, 503))
    test("POST /api/scholarships/download-pdf", "POST", "/api/scholarships/download-pdf", json_body={
        "student_data": {"name": "Test"}, "essay": "Sample essay text."
    }, accept_optional=(200, 503))

    # ---- WhatsApp ----
    test("GET /api/whatsapp/status", "GET", "/api/whatsapp/status")
    test("POST /api/whatsapp/test", "POST", "/api/whatsapp/test", json_body={"message": "help"}, accept_optional=(200, 503))

    # ---- Summary ----
    passed = sum(1 for _, ok, _, _ in results if ok)
    total = len(results)
    print("\n" + "=" * 60)
    print("INSIGHTRURAL FEATURE TEST RESULTS")
    print("=" * 60)
    for name, ok, status, _ in results:
        symbol = "PASS" if ok else "FAIL"
        print(f"  [{symbol}] {name} -> {status}")
    print("=" * 60)
    print(f"Total: {passed}/{total} passed")
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
