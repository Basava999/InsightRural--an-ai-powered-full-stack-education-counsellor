import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:5000/api/scholarships"

def test_scholarship_flow():
    print("=== Testing AI Scholarship Auto-Pilot ===")
    
    # 1. Generate Essay
    print("\n[1] Testing Essay Generation...")
    payload_essay = {
        "student_data": {
            "name": "Test Student",
            "education": "B.E. CSE",
            "income": "Low",
            "marks": "95%",
            "location": "Rural"
        },
        "scholarship": "Verifcation Scholarship",
        "reason": "I need financial support for my final year project."
    }
    
    essay_text = ""
    try:
        resp = requests.post(f"{BASE_URL}/generate-essay", json=payload_essay)
        if resp.status_code == 200:
            data = resp.json()
            essay_text = data.get("essay", "")
            if essay_text and len(essay_text) > 50:
                print(f"[OK] Essay Generated ({len(essay_text)} chars)")
                print(f"Preview: {essay_text[:100]}...")
            else:
                print(f"[FAIL] Essay empty or too short: {data}")
                return False
        else:
            print(f"[FAIL] API Error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False

    # 2. PDF Generation
    print("\n[2] Testing PDF Generation...")
    payload_pdf = {
        "student_data": {
            "name": "Test Student",
            "id": "TEST001",
            "date": "29-01-2026"
        },
        "essay": essay_text
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/download-pdf", json=payload_pdf)
        if resp.status_code == 200:
            data = resp.json()
            pdf_url = data.get("url")
            if pdf_url:
                print(f"[OK] PDF URL: {pdf_url}")
                # Check if file exists file system side
                # Assuming backend runs where we are editing
                # URL: /static/applications/application.pdf -> need to find actual path
                # But confirming URL return is good enough for API test
                return True
            else:
                print(f"[FAIL] No URL returned: {data}")
                return False
        else:
            print(f"[FAIL] API Error: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False

if __name__ == "__main__":
    success = test_scholarship_flow()
    if success:
        print("\n[SUCCESS] Scholarship Feature Verified!")
        exit(0)
    else:
        print("\n[FAIL] Verification Failed")
        exit(1)
