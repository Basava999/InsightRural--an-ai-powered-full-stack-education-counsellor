import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# In production, use PostgreSQL URL from .env
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/insightrural")

# Using SQLite for immediate local development and testing, 
# but the ORM is structured to seamlessly drop-in PostgreSQL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./insightrural_core.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # connect_args={"check_same_thread": False} is needed only for SQLite
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------------------------------------
# Core Schema Definitions for Structured Admission Data
# ---------------------------------------------------------

class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    college_code = Column(String, unique=True, index=True) # e.g., 'E001'
    name = Column(String, index=True)
    tier = Column(Integer, default=3) # 1=Top, 2=Mid, 3=Low
    location = Column(String)
    university_affiliation = Column(String)
    type = Column(String) # Government, Aided, Private

class Program(Base):
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey("institutions.id"))
    branch_name = Column(String, index=True)
    branch_code = Column(String, index=True) # e.g., 'CS'

class HistoricalCutoff(Base):
    __tablename__ = "cutoffs_historical"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"))
    year = Column(Integer, index=True) # e.g., 2024
    round_no = Column(Integer) # 1, 2, 3 (Mock, Round 1, Round 2...)
    category = Column(String, index=True) # GM, SC, ST, 2A, 2AG, 2AR...
    opening_rank = Column(Integer)
    closing_rank = Column(Integer)
    
class FeeStructure(Base):
    __tablename__ = "fee_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey("institutions.id"))
    year = Column(Integer, index=True)
    quota = Column(String) # SNQ, GM, Management
    tuition_fee = Column(Float)
    other_fees = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
