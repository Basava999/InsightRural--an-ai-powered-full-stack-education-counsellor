# backend/models.py - SIMPLIFIED VERSION
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
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


class AdmissionCutoff(Base):
    __tablename__ = "admission_cutoffs"

    id = Column(String, primary_key=True)
    exam = Column(String, nullable=False, index=True)
    institute_type = Column(String, nullable=False, index=True)
    college = Column(String, nullable=False, index=True)
    branch_or_course = Column(String, nullable=False, index=True)
    state = Column(String, nullable=True, index=True)
    quota = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True, index=True)
    gender = Column(String, nullable=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(String, nullable=True)
    opening_rank = Column(Integer, nullable=True)
    closing_rank = Column(Integer, nullable=False, index=True)
    typical_score = Column(Integer, nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CollegeComparisonMetric(Base):
    __tablename__ = "college_comparison_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    college = Column(String, nullable=False, unique=True, index=True)
    college_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    annual_fee = Column(Integer, nullable=True)
    hostel = Column(Boolean, default=False)
    average_package_lpa = Column(Float, nullable=True)
    highest_package_lpa = Column(Float, nullable=True)
    placement_summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CounselingSession(Base):
    __tablename__ = "counseling_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True, index=True)
    exam = Column(String, nullable=False, index=True)
    rank = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    state = Column(String, nullable=True)
    preferred_branches = Column(JSON, nullable=True)
    prediction_result = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CounselorMessage(Base):
    __tablename__ = "counselor_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True, index=True)
    user_message = Column(Text, nullable=False)
    retrieved_context = Column(JSON, nullable=True)
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    profile = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ============================================================================
# JEE MODULE MODELS
# ============================================================================

class JeeCollege(Base):
    __tablename__ = "jee_colleges"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    institute_type = Column(String, nullable=False, index=True) # IIT, NIT, IIIT, GFTI
    location = Column(String, nullable=True)
    state = Column(String, nullable=True, index=True)
    fees = Column(Integer, nullable=True)
    hostel = Column(Boolean, default=False)
    placement_stats = Column(JSON, nullable=True)
    seat_matrix = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JeeCutoff(Base):
    __tablename__ = "jee_cutoffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    college_id = Column(String, ForeignKey("jee_colleges.id"), nullable=False, index=True)
    branch = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    gender = Column(String, nullable=False)
    quota = Column(String, nullable=False, index=True) # HS, OS, AI
    opening_rank = Column(Integer, nullable=True)
    closing_rank = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# NEET MODULE MODELS
# ============================================================================

class NeetCollege(Base):
    __tablename__ = "neet_colleges"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=True, index=True)
    type = Column(String, nullable=True) # Government, Private, Deemed
    fees = Column(Integer, nullable=True)
    hostel = Column(Boolean, default=False)
    seat_matrix = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NeetCutoff(Base):
    __tablename__ = "neet_cutoffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    college_id = Column(String, ForeignKey("neet_colleges.id"), nullable=False, index=True)
    course = Column(String, nullable=False, index=True) # MBBS, BDS, AYUSH
    category = Column(String, nullable=False, index=True)
    quota = Column(String, nullable=False, index=True) # AIQ, State
    gender = Column(String, nullable=True)
    opening_rank = Column(Integer, nullable=True)
    closing_rank = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentRiskProfile(Base):
    __tablename__ = "student_risk_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True, index=True)
    
    # Inputs
    exam = Column(String, nullable=False, default="KCET")
    rank = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    income_lakhs = Column(Float, nullable=True)
    interests = Column(String, nullable=True)
    career_goals = Column(String, nullable=True)
    preferred_branches = Column(String, nullable=True)
    preferred_colleges = Column(String, nullable=True)
    
    # Outputs (Scores & Analysis)
    success_score = Column(Float, nullable=True)
    academic_risk = Column(String, nullable=True) # Low, Medium, High
    financial_risk = Column(String, nullable=True)
    placement_risk = Column(String, nullable=True)
    location_risk = Column(String, nullable=True)
    regret_probability = Column(Float, nullable=True) # 0-100%
    
    branch_compatibility_score = Column(Float, nullable=True)
    roi_score = Column(String, nullable=True) # High, Medium, Low
    
    ai_explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ============================================================================
# NEW ENTITIES: PLACEMENTS, SCHOLARSHIPS, HOSTELS
# ============================================================================

class PlacementRecord(Base):
    __tablename__ = "placement_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    college_id = Column(String, ForeignKey("colleges.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    branch = Column(String, nullable=True, index=True)
    avg_lpa = Column(Float, nullable=True)
    highest_lpa = Column(Float, nullable=True)
    placement_rate_percent = Column(Float, nullable=True)
    top_recruiters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScholarshipScheme(Base):
    __tablename__ = "scholarship_schemes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False) # Government, Private, College
    eligibility_criteria = Column(JSON, nullable=True) # Income limit, Categories, etc.
    benefits = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    application_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HostelInfo(Base):
    __tablename__ = "hostel_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    college_id = Column(String, ForeignKey("colleges.id"), nullable=False, index=True)
    type = Column(String, nullable=False) # Boys, Girls, Both
    annual_fee = Column(Integer, nullable=True)
    mess_fee_included = Column(Boolean, default=False)
    facilities = Column(JSON, nullable=True)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
