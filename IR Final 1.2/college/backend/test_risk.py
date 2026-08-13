import requests
import json

def test():
    # first signup to get a token
    base_url = "http://127.0.0.1:5000/api"
    try:
        resp = requests.post(f"{base_url}/auth/signup", json={
            "name": "Test User",
            "phone": "9999999999",
            "password": "password123"
        })
        token = ""
        if resp.status_code == 201 or resp.status_code == 200:
            token = resp.json().get("token")
        else:
            # Login if user already exists
            resp = requests.post(f"{base_url}/auth/login", json={
                "phone": "9999999999",
                "password": "password123"
            })
            token = resp.json().get("token")
            
        print("Token:", token)
        
        # Now test risk analyzer
        payload = {
            "rank": 15000,
            "college": "RV College of Engineering",
            "college_tier": 1,
            "branch": "Computer Science",
            "fees": 150000,
            "hostel_fees": 80000,
            "income": 600000,
            "marks": 85,
            "skills": ["coding", "math"],
            "interests": ["software", "ai"],
            "loan_required": False,
            "has_scholarship": False
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = requests.post(f"{base_url}/analyze/risk", json=payload, headers=headers)
        print("Status:", resp.status_code)
        print("Response:", json.dumps(resp.json(), indent=2))
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
