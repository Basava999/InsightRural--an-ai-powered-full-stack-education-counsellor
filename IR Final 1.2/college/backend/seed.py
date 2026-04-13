# backend/seed.py - SIMPLIFIED VERSION
import json
from pathlib import Path
from db import SessionLocal, engine, Base
from models import College, FeeStructure

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    try:
        # Clear existing data
        session.query(College).delete()
        session.query(FeeStructure).delete()
        session.commit()
        
        # Load fees first
        fees_path = DATA_DIR / "Fee.json"
        if fees_path.exists():
            fees = load_json(fees_path)
            for f in fees:
                record = FeeStructure(
                    category=f.get("category"),
                    gm_and_others_above_income_limit=f.get("gm_and_others_above_income_limit"),
                    snq_quota=f.get("snq_quota"),
                    sc_st_concession=f.get("sc_st_concession"),
                    cat1_upto_2_5_lakhs=f.get("cat1_upto_2_5_lakhs"),
                    others_upto_10_lakhs=f.get("others_upto_10_lakhs"),
                    cat1_above_2_5_lakhs=f.get("cat1_above_2_5_lakhs")
                )
                session.add(record)
        
        # Load colleges
        colleges_path = DATA_DIR / "College.json"
        if colleges_path.exists():
            colleges = load_json(colleges_path)
            for c in colleges:
                record = College(
                    id=c.get("college_id"),
                    name=c.get("name"),
                    type=c.get("type"),
                    location=c.get("location"),
                    affiliation=c.get("affiliation"),
                    hostel_available=bool(c.get("hostel_available", False)),
                    branches=c.get("branches") or [],
                    fee_category=c.get("fee_category"),
                    cutoff_data=c.get("cutoff_data") or {}
                )
                session.add(record)
        
        session.commit()
        print(f"âœ“ Seeded {len(fees) if fees_path.exists() else 0} fee structures")
        print(f"âœ“ Seeded {len(colleges) if colleges_path.exists() else 0} colleges")
        print("âœ… Seeding complete!")
        
    except Exception as e:
        session.rollback()
        print(f"âŒ Seeding failed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed()
