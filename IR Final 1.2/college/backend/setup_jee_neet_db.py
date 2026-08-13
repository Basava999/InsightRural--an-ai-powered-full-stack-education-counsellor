import json
import os
import uuid
from sqlalchemy.orm import sessionmaker
from db import engine, Base
from db_models import JeeCollege, JeeCutoff, NeetCollege, NeetCutoff

# Create new tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def seed_jee():
    print("Seeding JEE Data...")
    path = os.path.join(DATA_DIR, "jee_cutoffs_sample.json")
    if not os.path.exists(path):
        print(f"Skipping JEE seed, {path} not found.")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    rows = data.get("cutoffs", [])
    college_map = {} # name -> id
    
    # Extract unique colleges
    for row in rows:
        name = row.get("college")
        if not name: continue
        if name not in college_map:
            cid = str(uuid.uuid4())
            college_map[name] = cid
            c = JeeCollege(
                id=cid,
                name=name,
                institute_type=row.get("institute_type", "GFTI"),
                location=row.get("location", ""),
                state=row.get("state", ""),
                fees=row.get("annual_fee", 0),
                hostel=row.get("hostel", False),
                placement_stats={"average_lpa": row.get("average_package_lpa", 0)},
                seat_matrix={}
            )
            session.add(c)
            
    # Add cutoffs
    for row in rows:
        name = row.get("college")
        if not name or name not in college_map: continue
        c = JeeCutoff(
            college_id=college_map[name],
            branch=row.get("branch", ""),
            category=row.get("category", "OPEN"),
            gender=row.get("gender", "Gender Neutral"),
            quota=row.get("quota", "AI"),
            opening_rank=row.get("opening_rank"),
            closing_rank=row.get("closing_rank"),
            year=row.get("year", 2024),
            round=str(row.get("round", "6"))
        )
        session.add(c)
        
    session.commit()
    print("JEE Data seeded.")

def seed_neet():
    print("Seeding NEET Data...")
    path = os.path.join(DATA_DIR, "neet_cutoffs_sample.json")
    if not os.path.exists(path):
        print(f"Skipping NEET seed, {path} not found.")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    rows = data.get("cutoffs", [])
    college_map = {}
    
    # Extract unique colleges
    for row in rows:
        name = row.get("college")
        if not name: continue
        if name not in college_map:
            cid = str(uuid.uuid4())
            college_map[name] = cid
            c = NeetCollege(
                id=cid,
                name=name,
                state=row.get("state", ""),
                type=row.get("track", "Government"),
                fees=row.get("annual_fee", 0),
                hostel=row.get("hostel", False),
                seat_matrix={}
            )
            session.add(c)
            
    # Add cutoffs
    for row in rows:
        name = row.get("college")
        if not name or name not in college_map: continue
        c = NeetCutoff(
            college_id=college_map[name],
            course=row.get("course", "MBBS"),
            category=row.get("category", "OPEN"),
            quota=row.get("quota", "AIQ"),
            gender=row.get("gender", "All"),
            opening_rank=row.get("opening_rank"),
            closing_rank=row.get("closing_rank"),
            year=row.get("year", 2024),
            round=str(row.get("round", "1"))
        )
        session.add(c)
        
    session.commit()
    print("NEET Data seeded.")

if __name__ == "__main__":
    # Clear existing data just in case
    session.query(JeeCutoff).delete()
    session.query(JeeCollege).delete()
    session.query(NeetCutoff).delete()
    session.query(NeetCollege).delete()
    session.commit()
    
    seed_jee()
    seed_neet()
    print("Database seeding complete!")
