import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/counseling"

def test_counseling_suite():
    print("=== Testing KEA Counseling Suite API ===")

    # 1. Test Static Guide
    print("\n[1] Fetching Counseling Guide...")
    try:
        resp = requests.get(f"{BASE_URL}/guide")
        if resp.status_code == 200:
            data = resp.json()
            eng_steps = len(data.get("engineering", {}).get("steps", []))
            docs = len(data.get("documents", []))
            print(f"[OK] Guide fetched with {eng_steps} eng steps and {docs} documents.")
        else:
            print(f"[FAIL] Guide API Error: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False

    # 2. Test Smart Option Generator
    print("\n[2] Testing Option Generator (Rank: 10000, Cat: 2A, Branch: CSE)...")
    payload = {
        "rank": 10000,
        "category": "2A",
        "branches": ["CSE"]
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/generate-options", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            summary = data.get("summary", {})
            options = data.get("options", [])
            
            print(f"[OK] Options Generated: {summary['total_options']} total")
            print(f"    - Safe: {summary['safe_count']}")
            print(f"    - Realistic: {summary['realistic_count']}")
            print(f"    - Ambitious: {summary['ambitious_count']}")
            
            if options:
                print("\nSample Output (Top 3):")
                for i, opt in enumerate(options[:3]):
                    print(f"  {i+1}. {opt['college_name']} ({opt['chance']}) - Cutoff: {opt['cutoff']}")
            
            return True
        else:
            print(f"[FAIL] Generator API Error: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False

if __name__ == "__main__":
    if test_counseling_suite():
        print("\n[SUCCESS] Counseling Suite Verified!")
        exit(0)
    else:
        print("\n[FAIL] Verification Failed")
        exit(1)
