"""Pydantic schemas for student profiles and recommendations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class StudentProfile(BaseModel):
    rank: int = Field(..., gt=0, description="KCET rank (lower is better)")
    category: str = Field(default="GM")
    gender: Optional[str] = Field(default=None)
    branch: str = Field(default="CSE")
    city: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)
    hostel_required: bool = Field(default=False)
    budget: Optional[int] = Field(default=None, ge=0)
    rural: bool = Field(default=False)
    kannada_medium: bool = Field(default=False)
    snq: bool = Field(default=False)
    hk_371j: bool = Field(default=False)
    minority: bool = Field(default=False)
    college_type: Optional[str] = Field(default=None)

    @field_validator("branch")
    @classmethod
    def normalize_branch(cls, v: str) -> str:
        return v.upper().replace(" ", "_").replace("-", "_")

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        return v.upper().strip()


class QueryUnderstandingResult(BaseModel):
    """Layer 1 output — structured extraction from user query."""
    rank: Optional[int] = None
    category: str = "GM"
    gender: Optional[str] = None
    branch: str = "CSE"
    city: Optional[str] = None
    district: Optional[str] = None
    hostel_required: bool = False
    budget: Optional[int] = None
    rural: bool = False
    kannada_medium: bool = False
    snq: bool = False
    hk_371j: bool = False
    minority: bool = False
    college_type: Optional[str] = None
    raw_query: Optional[str] = None
    extraction_confidence: float = Field(default=1.0, ge=0, le=1)


class CollegeRecommendation(BaseModel):
    college_id: str
    college_name: str
    branch: str
    location: str
    district: Optional[str] = None
    college_type: str
    cutoff_rank: int
    predicted_cutoff: Optional[int] = None
    admission_probability: float = Field(ge=0, le=100)
    tier: str  # SAFE, MODERATE, AMBITIOUS
    composite_score: float
    annual_fee: Optional[float] = None
    hostel_available: bool = False
    placement_avg_lpa: Optional[float] = None
    naac_grade: Optional[str] = None
    explanation: List[str] = Field(default_factory=list)
    data_completeness: float = Field(default=1.0, ge=0, le=1)


class RecommendationResponse(BaseModel):
    profile: StudentProfile
    safe: List[CollegeRecommendation] = Field(default_factory=list)
    moderate: List[CollegeRecommendation] = Field(default_factory=list)
    ambitious: List[CollegeRecommendation] = Field(default_factory=list)
    total_eligible: int = 0
    total_after_filters: int = 0
    confidence: float = Field(ge=0, le=1)
    data_completeness: float = Field(ge=0, le=1)
    engine_version: str
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    hostels: List[Dict[str, Any]] = Field(default_factory=list)
    scholarships: List[Dict[str, Any]] = Field(default_factory=list)
    explanation_summary: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    profile: Optional[StudentProfile] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    recommendations: Optional[RecommendationResponse] = None
    sources: List[str] = Field(default_factory=list)
    engine_used: str = "deterministic"
