import os
import sys
import json

# Fix Windows console encoding for ₹ and emojis
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from llm_service import get_llm_service

def run_tests():
    llm = get_llm_service()
    
    queries = [
        "What is RVCE hostel gate timing?",
        "What is RVCE hostel fee?",
        "What is RVCE placement percentage?",
        "Which colleges in Bangalore offer AI branch and hostel?"
    ]
    
    print("Running hallucination tests...")
    results = {}
    for q in queries:
        print(f"\nQuery: {q}")
        response = llm.generate_response(query=q)
        print(f"Response: {response}")
        results[q] = response

if __name__ == "__main__":
    run_tests()
