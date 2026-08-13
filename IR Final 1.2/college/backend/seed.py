# backend/seed.py - SIMPLIFIED VERSION
import json
from pathlib import Path
from db import SessionLocal, engine, Base
from db_models import College, FeeStructure, PlacementRecord, ScholarshipScheme, HostelInfo
from datetime import datetime

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
        session.query(PlacementRecord).delete()
        session.query(ScholarshipScheme).delete()
        session.query(HostelInfo).delete()
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
        colleges_path = DATA_DIR / "Production_Ready_Colleges.json"
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
        
        # Load scholarships
        scholarships_path = DATA_DIR / "scholarships.json"
        if scholarships_path.exists():
            scholarships = load_json(scholarships_path)
            for s in scholarships:
                record = ScholarshipScheme(
                    name=s.get("name"),
                    provider=s.get("provider", "Government"),
                    eligibility_criteria=s.get("eligibility", {}),
                    benefits=s.get("benefits"),
                    application_url=s.get("application_url")
                )
                session.add(record)
                
        # Load hostels
        hostels_path = DATA_DIR / "hostels.json"
        if hostels_path.exists():
            hostels = load_json(hostels_path)
            for h in hostels:
                # We need to ensure college_id exists in our mock data
                cid = h.get("college_id")
                if not cid: continue
                record = HostelInfo(
                    college_id=cid,
                    type=h.get("type", "Both"),
                    annual_fee=h.get("annual_fee"),
                    mess_fee_included=h.get("mess_fee_included", False),
                    facilities=h.get("facilities", []),
                    capacity=h.get("capacity")
                )
                session.add(record)
                
        # Placement records can be extracted from college_master if they exist
        college_master_path = DATA_DIR / "Production_Ready_Colleges.json"
        if college_master_path.exists():
            master_data = load_json(college_master_path)
            for c in master_data:
                cid = c.get("college_id")
                avg_lpa = c.get("placement_avg_lpa")
                if cid and avg_lpa:
                    record = PlacementRecord(
                        college_id=cid,
                        year=2024,
                        avg_lpa=float(avg_lpa),
                        highest_lpa=c.get("highest_package_lpa"),
                        placement_rate_percent=c.get("placement_rate", 85.0)
                    )
                    session.add(record)
                    
        session.commit()
        
        print(f"âœ“ Seeded fee structures")
        print(f"âœ“ Seeded colleges")
        print(f"âœ“ Seeded scholarships, hostels, and placements")
        print("âœ… Seeding complete!")
        
    except Exception as e:
        session.rollback()
        print(f"â Œ Seeding failed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed()
