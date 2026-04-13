import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'college', 'backend'))

from db import SessionLocal
from models import College
from sqlalchemy import or_

def debug_search():
    session = SessionLocal()
    try:
        # Simulate app.py logic
        q = "RV"
        print(f"Simulating search for q='{q}'")
        
        all_colleges = session.query(College).all()
        print(f"Fetched {len(all_colleges)} colleges")
        
        filtered_colleges = []
        for col in all_colleges:
            # Normalize text: remove dots, spaces, special chars
            def normalize(text):
                return "".join(e for e in str(text).lower() if e.isalnum())
            
            norm_q = normalize(q)
            norm_name = normalize(col.name)
            norm_loc = normalize(col.location or "")  # Fix for None location
            
            if (q.lower() in col.name.lower()) or \
               (norm_q in norm_name) or \
               (q.lower() in (col.location or "").lower()) or \
               (col.affiliation and q.lower() in col.affiliation.lower()):
                filtered_colleges.append(col)
                
        print(f"Filtered count: {len(filtered_colleges)}")
        for c in filtered_colleges:
            print(f" - {c.name}")

    except Exception as e:
        import traceback
        print(f"❌ CRASH: {e}")
        print(traceback.format_exc())
    finally:
        session.close()

if __name__ == "__main__":
    debug_search()
