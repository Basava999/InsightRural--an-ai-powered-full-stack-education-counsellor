# backend/models.py - SIMPLIFIED VERSION
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.types import JSON
from db import Base

class FeeStructure(Base):
    __tablename__ = "fees"
    category = Column(String, primary_key=True, index=True)
    gm_and_others_above_income_limit = Column(Integer, nullable=True)
    snq_quota = Column(Integer, nullable=True)
    sc_st_concession = Column(Integer, nullable=True)
    cat1_upto_2_5_lakhs = Column(Integer, nullable=True)
    others_upto_10_lakhs = Column(Integer, nullable=True)
    cat1_above_2_5_lakhs = Column(Integer, nullable=True)

class College(Base):
    __tablename__ = "colleges"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=True)
    location = Column(String, nullable=True, index=True)
    affiliation = Column(String, nullable=True)
    hostel_available = Column(Boolean, default=False)
    branches = Column(JSON, nullable=True)
    fee_category = Column(String, ForeignKey("fees.category"), nullable=True)
    cutoff_data = Column(JSON, nullable=True)