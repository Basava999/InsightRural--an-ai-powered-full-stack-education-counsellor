import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_search(query):
    print(f"\nSearching for '{query}'...")
    try:
        url = f"{BASE_URL}/colleges?q={query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"Found {len(items)} results")
            for item in items:
                print(f"  - {item['name']}")
                
            if len(items) > 0:
                print("[OK] Search Successful")
                return True
            else:
                print("[FAIL] No results found")
                return False
        else:
            print(f"[FAIL] API Error: {response.status_code}")
            sanitized_text = response.text.encode('ascii', 'replace').decode()
            print(f"Response: {sanitized_text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Connection Error: {e}")
        return False

if __name__ == "__main__":
    # Test specific cases that were failing
    search_queries = ["RV", "BMS", "engineering"]
    
    for q in search_queries:
        test_search(q)
