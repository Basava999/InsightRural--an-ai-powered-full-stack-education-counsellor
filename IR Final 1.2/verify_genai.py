import requests
import json
import base64
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_endpoint(name, method, endpoint, data=None):
    print(f"\nTesting {name} ({method} {endpoint})...")
    try:
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
            
        elapsed = time.time() - start_time
        
        if response.status_code in [200, 201]:
            print(f"[OK] SUCCESS ({elapsed:.2f}s)")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
            except:
                print(f"Response: {response.text[:200]}...")
            return True
        else:
            print(f"[FAIL] FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] ERROR: {str(e)}")
        return False

def run_verification():
    print("Starting GenAI Features Verification")
    print("="*50)
    
    # 1. Health Check
    if not test_endpoint("Health Check", "GET", "/health"):
        print("CRITICAL: Backend not healthy! Aborting.")
        return

    # 2. Voice Counselor (Chat with 'voice' flag)
    # Testing simpler voice response optimization
    voice_data = {
        "message": "Hello, can you help me?",
        "feature": "voice",
        "language": "en-IN"
    }
    test_endpoint("Voice Counselor Chat", "POST", "/chat", voice_data)
    
    # 3. Document Scanner
    # Create a dummy base64 image (small white pixel)
    dummy_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    scan_data = {
        "image": dummy_image,
        "document_type": "marksheet"
    }
    test_endpoint("Document Scanner", "POST", "/documents/scan", scan_data)
    
    # 4. Standard Chat (Comparison)
    chat_data = {
        "message": "Tell me about RV College of Engineering",
        "feature": "chat"
    }
    test_endpoint("Standard Chat", "POST", "/chat", chat_data)
    test_endpoint("Standard Chat", "POST", "/chat", chat_data)

    # 5. Career Simulator (New)
    career_data = {
        "rank": 5000,
        "category": "2A",
        "branch": "CSE",
        "interests": "Artificial Intelligence, Space Tech"
    }
    test_endpoint("Career Simulator", "POST", "/api/simulate-career", career_data)

    print("\n" + "="*50)
    print("Verification Complete")

if __name__ == "__main__":
    run_verification()
