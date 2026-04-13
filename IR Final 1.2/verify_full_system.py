import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_result(name, passed, elapsed=0, msg=""):
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} {name} ({elapsed:.2f}s) {msg}")

def test_endpoint(name, method, endpoint, data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
            
        elapsed = time.time() - start_time
        
        if response.status_code in [200, 201]:
            print_result(name, True, elapsed)
            return True
        else:
            print_result(name, False, elapsed, f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_result(name, False, 0, f"Error: {str(e)}")
        return False

def test_scholarship_autopilot():
    print(f"\n{Colors.HEADER}=== Testing AI Scholarship Auto-Pilot ==={Colors.ENDC}")
    try:
        # Test 1: Essay Generation
        print(f"{Colors.BLUE}[1] Testing Essay Generation...{Colors.ENDC}")
        payload = {
            "student_data": {"name": "Test User", "course": "BE CSE"},
            "scholarship_name": "Test Scholarship",
            "reason": "Financial Need"
        }
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/scholarships/generate-essay", json=payload)
        duration = time.time() - start_time
        
        if resp.status_code == 200:
            essay = resp.json().get("essay", "")
            if len(essay) > 100:
                print(f"{Colors.GREEN}[OK] Essay Generated ({len(essay)} chars) in {duration:.2f}s{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[FAIL] Essay too short{Colors.ENDC}")
                return False
        else:
            print(f"{Colors.FAIL}[FAIL] API Error: {resp.status_code}{Colors.ENDC}")
            return False

        # Test 2: PDF Generation
        print(f"{Colors.BLUE}[2] Testing PDF Generation...{Colors.ENDC}")
        pdf_payload = {"student_data": {"name": "Test User"}, "essay": essay}
        start_time_pdf = time.time()
        resp_pdf = requests.post(f"{BASE_URL}/scholarships/download-pdf", json=pdf_payload)
        
        if resp_pdf.status_code != 200:
             print_result("Scholarship Auto-Pilot (PDF Gen)", False, 0, f"Status: {resp_pdf.status_code}")
             return False

        if not resp_pdf.json().get("url"):
             print_result("Scholarship Auto-Pilot (PDF Gen)", False, 0, "No PDF URL returned")
             return False
            
        print_result("Scholarship Auto-Pilot (Full)", True, 0, f"({len(essay)} chars, PDF generated)")
        return True
        
    except Exception as e:
        print_result("Scholarship Auto-Pilot", False, 0, f"Error: {str(e)}")
        return False

def test_counseling_suite():
    print(f"\n{Colors.HEADER}=== Testing KEA Counseling Suite ==={Colors.ENDC}")
    try:
        # Test 1: Guide Data
        print(f"{Colors.BLUE}[1] Fetching Guide Data...{Colors.ENDC}")
        resp = requests.get(f"{BASE_URL}/counseling/guide")
        if resp.status_code == 200:
            data = resp.json()
            if "engineering" in data and "documents" in data:
                print(f"{Colors.GREEN}[OK] Guide Data Valid{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[FAIL] Invalid Guide Data{Colors.ENDC}")
                return False
        else:
            print(f"{Colors.FAIL}[FAIL] Guide API Error: {resp.status_code}{Colors.ENDC}")
            return False

        # Test 2: Option Generator
        print(f"{Colors.BLUE}[2] Testing Option Generator...{Colors.ENDC}")
        payload = {"rank": 10000, "category": "2A", "branches": ["CSE"]}
        resp = requests.post(f"{BASE_URL}/counseling/generate-options", json=payload)
        if resp.status_code == 200:
            summary = resp.json().get("summary", {})
            if summary.get("total_options", 0) > 0:
                print(f"{Colors.GREEN}[OK] Options Generated: {summary['total_options']} (Safe: {summary['safe_count']}){Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[FAIL] No options generated{Colors.ENDC}")
                return False
        else:
            print(f"{Colors.FAIL}[FAIL] Generator API Error: {resp.status_code}{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}[FAIL] Error: {e}{Colors.ENDC}")
        return False
    return True

def run_full_system_verification():
    print("STARTING FULL SYSTEM HEALTH CHECK")
    print("="*50)
    
    # --- CORE FEATURES ---
    print("\n--- CORE FEATURES ---")
    
    # 1. Health Check
    test_endpoint("System Health", "GET", "/health")
    
    # 2. College Search/List
    test_endpoint("College List", "GET", "/colleges?limit=5")
    
    # 3. College Recommendation (RAG/Logic)
    rec_data = {
        "kcet_rank": 15000,
        "category": "GM",
        "branch": "CSE"
    }
    test_endpoint("College Recommendation", "POST", "/recommend/colleges", rec_data)
    
    # 4. Scholarship Recommendation
    schol_data = {
        "category": "SC",
        "income": 200000
    }
    test_endpoint("Scholarship Recommendation", "POST", "/recommend/scholarships", schol_data)
    
    # 5. ML Prediction (Random Forest)
    ml_data = {
        "kcet_rank": 12000,
        "category": "2A",
        "branch": "ECE"
    }
    test_endpoint("ML Admission Prediction", "POST", "/predict/college", ml_data)

    # --- ADVANCED GEN-AI FEATURES ---
    print("\n--- ADVANCED GenAI FEATURES ---")
    
    # 6. Standard Contextual Chat
    chat_data = {"message": "Tell me about BMS College", "feature": "chat"}
    test_endpoint("Standard AI Chat", "POST", "/chat", chat_data)
    
    # 7. Voice Counselor Chat
    voice_data = {"message": "Hello", "feature": "voice", "language": "en-IN"}
    test_endpoint("Voice Counselor API", "POST", "/chat", voice_data)
    
    # 8. Document Scanner
    # 1x1 pixel base64 image
    dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    scan_data = {"image": dummy_image, "document_type": "marksheet"}
    test_endpoint("Document Scanner API", "POST", "/documents/scan", scan_data)

    # 9. Scholarship Auto-Pilot
    test_scholarship_autopilot()

    # 10. KEA Counseling Suite
    test_counseling_suite()

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")

if __name__ == "__main__":
    run_full_system_verification()
