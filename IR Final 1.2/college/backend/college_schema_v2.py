# ==============================================================================
# InsightRural — College Schema V2 (Master Prompt Compliant)
# ==============================================================================
# Pydantic models enforcing the comprehensive college knowledge base schema.
# Every factual field carries optional source provenance.
# ==============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ── Source-tagged value wrapper ───────────────────────────────────────────────

class SourcedValue(BaseModel):
    """Wraps any factual value with its provenance source."""
    value: Any = None
    source: str = "InsightRural Database"
    scraped_at: Optional[str] = None


# ── Sub-models ────────────────────────────────────────────────────────────────

class ApprovalInfo(BaseModel):
    aicte: Optional[bool] = None
    ugc: Optional[bool] = None
    naac_grade: Optional[str] = None
    nba_accredited_branches: Optional[List[str]] = None
    nba_accredited: Optional[bool] = None


class NIRFInfo(BaseModel):
    rank: Optional[int] = None
    year: Optional[int] = None
    source: Optional[str] = None


class LocationInfo(BaseModel):
    address: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    state: str = "Karnataka"
    pin_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_link: Optional[str] = None


class BranchInfo(BaseModel):
    branch_name: str
    branch_code: Optional[str] = None
    intake: Optional[int] = None
    duration: int = 4
    degree: str = "B.E."
    accredited: Optional[bool] = None


class CategoryCutoff(BaseModel):
    """Opening and closing ranks for a single category in a single round."""
    opening_rank: Optional[SourcedValue] = None
    closing_rank: Optional[SourcedValue] = None


class FeeStructure(BaseModel):
    tuition_fee: Optional[SourcedValue] = None
    development_fee: Optional[SourcedValue] = None
    university_fee: Optional[SourcedValue] = None
    examination_fee: Optional[SourcedValue] = None
    hostel_fee: Optional[SourcedValue] = None
    mess_fee: Optional[SourcedValue] = None
    transport_fee: Optional[SourcedValue] = None
    other_charges: Optional[SourcedValue] = None
    management_quota_fee: Optional[SourcedValue] = None
    comedk_fee: Optional[SourcedValue] = None
    kcet_fee_gm: Optional[SourcedValue] = None
    kcet_fee_obc: Optional[SourcedValue] = None
    kcet_fee_sc_st: Optional[SourcedValue] = None


class PlacementInfo(BaseModel):
    year: Optional[int] = None
    highest_package: Optional[SourcedValue] = None
    average_package: Optional[SourcedValue] = None
    median_package: Optional[SourcedValue] = None
    lowest_package: Optional[SourcedValue] = None
    placement_percentage: Optional[SourcedValue] = None
    top_recruiters: Optional[List[str]] = None
    internship_companies: Optional[List[str]] = None
    placement_report_url: Optional[str] = None


class HostelDetails(BaseModel):
    available: bool = False
    capacity: Optional[int] = None
    room_types: Optional[List[str]] = None
    annual_fee: Optional[SourcedValue] = None
    mess_fee_monthly: Optional[SourcedValue] = None
    mess_included: Optional[bool] = None
    wifi: Optional[bool] = None
    laundry: Optional[bool] = None
    gym: Optional[bool] = None
    medical: Optional[bool] = None
    security: Optional[bool] = None
    amenities: Optional[List[str]] = None
    rules: Optional[List[str]] = None
    food_type: Optional[str] = None


class HostelInfo(BaseModel):
    boys_hostel: Optional[HostelDetails] = None
    girls_hostel: Optional[HostelDetails] = None


class FacilitiesInfo(BaseModel):
    campus_area_acres: Optional[float] = None
    library: Optional[bool] = None
    labs: Optional[int] = None
    innovation_centre: Optional[bool] = None
    incubation_centre: Optional[bool] = None
    sports: Optional[List[str]] = None
    medical_facility: Optional[bool] = None
    auditorium: Optional[bool] = None
    transportation: Optional[bool] = None
    cafeteria: Optional[bool] = None
    wifi_campus: Optional[bool] = None


class FacultyInfo(BaseModel):
    total_faculty: Optional[int] = None
    phd_faculty: Optional[int] = None
    student_faculty_ratio: Optional[str] = None


class AdmissionInfo(BaseModel):
    kcet: bool = True
    comedk: Optional[bool] = None
    jee: Optional[bool] = None
    management_quota: Optional[bool] = None
    pgcet: Optional[bool] = None
    lateral_entry: Optional[bool] = None
    eligibility: Optional[str] = None
    documents_required: Optional[List[str]] = None
    counselling_process: Optional[str] = None


class NearbyInfo(BaseModel):
    nearest_railway_station: Optional[str] = None
    nearest_airport: Optional[str] = None
    nearest_bus_stand: Optional[str] = None
    railway_distance_km: Optional[float] = None
    airport_distance_km: Optional[float] = None
    bus_distance_km: Optional[float] = None


# ── Master College Model ─────────────────────────────────────────────────────

class CollegeV2(BaseModel):
    """
    Comprehensive college model matching the Master Prompt schema.
    
    Every factual numeric field uses SourcedValue for provenance.
    Missing data is null — never invented.
    """
    # Basic Information
    college_id: str
    college_name: str
    short_name: Optional[str] = None
    college_code: Optional[str] = None
    established: Optional[int] = None
    ownership: Optional[str] = None  # Government / Private / Aided
    autonomous: Optional[bool] = None
    affiliated_university: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    principal_name: Optional[str] = None
    highlights: Optional[List[str]] = None

    # Structured sub-models
    approval: ApprovalInfo = Field(default_factory=ApprovalInfo)
    nirf: NIRFInfo = Field(default_factory=NIRFInfo)
    location: LocationInfo = Field(default_factory=LocationInfo)
    branches: List[BranchInfo] = Field(default_factory=list)
    
    # Cutoffs: year → round → branch → category → CategoryCutoff
    # Example: cutoffs["2024"]["Round1"]["CSE"]["GM"] = CategoryCutoff(...)
    cutoffs: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = Field(default_factory=dict)
    
    fees: FeeStructure = Field(default_factory=FeeStructure)
    placements: PlacementInfo = Field(default_factory=PlacementInfo)
    hostel: HostelInfo = Field(default_factory=HostelInfo)
    facilities: FacilitiesInfo = Field(default_factory=FacilitiesInfo)
    faculty: FacultyInfo = Field(default_factory=FacultyInfo)
    admission: AdmissionInfo = Field(default_factory=AdmissionInfo)
    nearby: NearbyInfo = Field(default_factory=NearbyInfo)
    
    # Cross-references
    scholarship_ids: List[str] = Field(default_factory=list)
    
    # Provenance
    sources: List[str] = Field(default_factory=lambda: ["InsightRural Database"])
    last_updated: Optional[str] = None

    # Legacy compatibility — flat fee fields used by existing recommend_colleges()
    annual_fee: Optional[Any] = None
    fee_category: Optional[str] = None
    total_seats: Optional[int] = None
    hostel_available: Optional[bool] = None
    
    # Legacy cutoff fields used by existing recommend_colleges()
    cutoff_2024: Optional[Dict[str, Dict[str, int]]] = None
    cutoff_trends: Optional[Dict[str, Dict]] = None
    
    # Legacy placement fields
    placement_avg_lpa: Optional[float] = None
    placement_highest_lpa: Optional[float] = None
    top_recruiters: Optional[List[str]] = None
    naac_grade: Optional[str] = None
    nba_accredited: Optional[bool] = None
