# ==============================================================================
# InsightRural — Pydantic Schemas (Request/Response Validation)
# ==============================================================================
# All input/output contracts for the recommendation pipeline.
# Enforces type safety and field validation at the API boundary.
# ==============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class CategoryEnum(str, Enum):
    GM = "GM"
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    CAT1 = "CAT1"
    CAT_1 = "CAT-1"
    TWO_A = "2A"
    TWO_B = "2B"
    THREE_A = "3A"
    THREE_B = "3B"
    EWS = "EWS"
    GENERAL = "GENERAL"


class CollegeTypeEnum(str, Enum):
    GOVERNMENT = "Government"
    GOVERNMENT_AIDED = "Government_Aided"
    PRIVATE_AUTONOMOUS = "Private_Autonomous"
    TYPE1_UNAIDED = "Type1_Unaided"
    TYPE2_UNAIDED = "Type2_Unaided"
    DEEMED_PRIVATE = "Deemed_Private"
    ANY = "Any"


class AdmissionTier(str, Enum):
    SAFE = "Safe"
    MODERATE = "Moderate"
    AMBITIOUS = "Ambitious"


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class ExamType(str, Enum):
    KCET = "KCET"
    JEE_MAIN = "JEE_MAIN"
    JEE_ADVANCED = "JEE_ADVANCED"
    NEET_UG = "NEET_UG"


# ── Student Profile ───────────────────────────────────────────────────────────

class StudentProfile(BaseModel):
    """
    Complete student profile extracted from form input or natural language query.
    This is the single input contract for the entire recommendation pipeline.
    """
    # Core identity
    rank: int = Field(..., gt=0, le=500000, description="KCET/JEE/NEET rank")
    category: str = Field(default="GM", description="Reservation category")
    gender: Optional[str] = Field(default=None, description="Male/Female/Other")
    exam: str = Field(default="KCET", description="Exam type")

    # Preferences
    preferred_branches: List[str] = Field(
        default_factory=lambda: ["CSE"],
        description="List of preferred branches in order"
    )
    preferred_locations: Optional[List[str]] = Field(
        default=None,
        description="City/district preferences. None = no location constraint"
    )
    college_type: Optional[str] = Field(
        default=None,
        description="Government, Private, Any"
    )

    # Constraints (HARD — never relaxed)
    budget: Optional[int] = Field(
        default=None, gt=0,
        description="Maximum annual fee in INR. None = no budget constraint"
    )
    hostel_required: bool = Field(default=False, description="Must have hostel")

    # Special quotas
    rural_quota: bool = Field(default=False, description="Rural quota eligibility")
    kannada_medium: bool = Field(default=False, description="Kannada medium quota")
    snq: bool = Field(default=False, description="Supernumerary quota")
    hk_371j: bool = Field(default=False, description="Hyderabad-Karnataka 371J")
    minority: bool = Field(default=False, description="Minority institution quota")

    # Academic data (optional, for enhanced prediction)
    puc_marks: Optional[Dict[str, int]] = Field(
        default=None,
        description="PUC subject marks {physics, chemistry, maths}"
    )
    kcet_marks: Optional[Dict[str, int]] = Field(
        default=None,
        description="KCET subject marks {physics, chemistry, maths}"
    )
    income_lakhs: Optional[float] = Field(
        default=None, ge=0,
        description="Annual family income in lakhs"
    )

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        """Normalize category strings to standard KEA format."""
        if not v:
            return "GM"
        v = v.upper().strip()
        mapping = {
            "GENERAL": "GM", "GEN": "GM", "OC": "GM",
            "CATEGORY-1": "CAT1", "CAT-1": "CAT1",
        }
        return mapping.get(v, v)

    @field_validator("preferred_branches", mode="before")
    @classmethod
    def normalize_branches(cls, v):
        """Accept both string and list formats."""
        if isinstance(v, str):
            return [b.strip().upper() for b in v.split(",") if b.strip()]
        if isinstance(v, list):
            return [str(b).strip().upper() for b in v if str(b).strip()]
        return ["CSE"]

    @field_validator("preferred_locations", mode="before")
    @classmethod
    def normalize_locations(cls, v):
        """Accept both string and list formats. None means no constraint."""
        if v is None or v == "" or v == []:
            return None
        if isinstance(v, str):
            locs = [l.strip() for l in v.split(",") if l.strip()]
            return locs if locs else None
        if isinstance(v, list):
            locs = [str(l).strip() for l in v if str(l).strip()]
            return locs if locs else None
        return None

    @property
    def dataset_category(self) -> str:
        """Map detailed category to dataset lookup category."""
        cat_map = {
            "GM": "GM", "GENERAL": "GM", "GEN": "GM", "OC": "GM", "EWS": "GM",
            "SC": "SC", "ST": "ST",
            "OBC": "OBC", "2A": "OBC", "2B": "OBC", "3A": "OBC", "3B": "OBC",
            "CAT1": "OBC", "CAT-1": "OBC", "CATEGORY-1": "OBC",
        }
        return cat_map.get(self.category, "GM")

    @property
    def fee_category_key(self) -> str:
        """Map category to fee lookup key."""
        if self.dataset_category in ("SC", "ST"):
            return "sc_st"
        elif self.dataset_category == "OBC":
            return "obc"
        return "gm"


# ── Recommendation Results ────────────────────────────────────────────────────

class AdmissionProbability(BaseModel):
    """Admission probability for a specific college-branch combination."""
    probability: float = Field(ge=0, le=100, description="Admission probability %")
    tier: AdmissionTier = Field(description="Safe/Moderate/Ambitious classification")
    predicted_round: str = Field(description="Expected allotment round")
    confidence_score: int = Field(ge=0, le=100, description="Prediction confidence")
    confidence_label: str = Field(description="High/Good/Medium/Low")


class ReservationResult(BaseModel):
    """Reservation benefit calculation result."""
    effective_cutoff: int = Field(description="Cutoff after reservation adjustment")
    original_cutoff: int = Field(description="Raw cutoff rank")
    multiplier: float = Field(description="Reservation multiplier applied")
    benefits: List[str] = Field(default_factory=list, description="Applied benefits")
    has_benefit: bool = Field(default=False)


class SubScores(BaseModel):
    """Detailed sub-scores for recommendation ranking transparency."""
    admission_probability: float = Field(ge=0, le=100)
    placement_score: float = Field(ge=0, le=100)
    accreditation_score: float = Field(ge=0, le=100)
    hostel_score: float = Field(ge=0, le=100)
    fee_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)


class CollegeRecommendation(BaseModel):
    """Single college recommendation with all metadata."""
    # Identity
    college_id: str
    college_name: str
    location: str
    college_type: str

    @field_validator("location", mode="before")
    @classmethod
    def normalize_rec_location(cls, v):
        if isinstance(v, dict):
            parts = [str(val) for k, val in v.items() if k in ("district", "city", "state", "place") and val]
            if not parts:
                parts = [str(val) for val in v.values() if isinstance(val, str)]
            return ", ".join(parts) if parts else "Karnataka"
        return str(v or "Unknown")

    # Branch & cutoff
    branch: str
    cutoff_rank: int
    original_cutoff: int
    predicted_cutoff: Optional[int] = None
    gm_cutoff: Optional[int] = None
    category_cutoff: Optional[int] = None

    # Scores
    recommendation_score: int = Field(ge=0, le=100, description="Weighted composite score")
    sub_scores: SubScores
    admission: AdmissionProbability
    reservation: ReservationResult

    # College details
    annual_fee: int = Field(default=0)
    four_year_cost: int = Field(default=0)
    hostel_available: bool = Field(default=False)
    naac_grade: Optional[str] = None
    placement_avg_lpa: Optional[float] = None
    placement_highest_lpa: Optional[float] = None

    # Trend data
    trend_direction: str = Field(default="stable")
    historical_cutoffs: Dict[str, Any] = Field(default_factory=dict)

    # Explainability
    reason: str = Field(description="Why this college is recommended")
    map_link: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None


class RecommendationResponse(BaseModel):
    """Full recommendation pipeline response."""
    success: bool = True
    student_profile: Dict[str, Any]

    # Classified results
    safe: List[CollegeRecommendation] = Field(default_factory=list)
    moderate: List[CollegeRecommendation] = Field(default_factory=list)
    ambitious: List[CollegeRecommendation] = Field(default_factory=list)

    # Totals
    total_eligible: int = 0
    total_colleges_checked: int = 0

    # Strategy
    option_entry_sequence: List[Dict[str, Any]] = Field(default_factory=list)
    counselling_guidance: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    kea_info: Dict[str, Any] = Field(default_factory=dict)
    ml_model_used: Optional[str] = None
    confidence: Dict[str, Any] = Field(default_factory=dict)


# ── Chat Schemas ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Chat endpoint request."""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str = Field(default="default")
    history: List[Dict[str, str]] = Field(default_factory=list)
    language: str = Field(default="en-IN")
    profile: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat endpoint response."""
    response: str
    session_id: str
    model_used: Optional[str] = None
    recommendations: Optional[RecommendationResponse] = None
    error: bool = False


# ── Prediction Request ────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """KCET college prediction request."""
    kcet_rank: int = Field(..., gt=0, le=500000)
    category: str = Field(default="GM")
    preferred_branches: List[str] = Field(default_factory=lambda: ["CSE"])
    preferred_locations: Optional[List[str]] = None
    budget: Optional[int] = Field(default=None, gt=0)
    college_type: Optional[str] = None
    hostel_required: bool = False
    rural_quota: bool = False
    kannada_medium: bool = False
    hk_371j: bool = False
    snq: bool = False
    minority: bool = False
    puc_marks: Optional[Dict[str, int]] = None
    kcet_marks: Optional[Dict[str, int]] = None
    income_lakhs: Optional[float] = None
    top_n: int = Field(default=15, ge=1, le=50)

    def to_student_profile(self) -> StudentProfile:
        """Convert to StudentProfile for the recommendation pipeline."""
        return StudentProfile(
            rank=self.kcet_rank,
            category=self.category,
            preferred_branches=self.preferred_branches,
            preferred_locations=self.preferred_locations,
            budget=self.budget,
            college_type=self.college_type,
            hostel_required=self.hostel_required,
            rural_quota=self.rural_quota,
            kannada_medium=self.kannada_medium,
            snq=self.snq,
            hk_371j=self.hk_371j,
            minority=self.minority,
            puc_marks=self.puc_marks,
            kcet_marks=self.kcet_marks,
            income_lakhs=self.income_lakhs,
        )


# ── Compare Schemas ───────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    """Compare colleges request."""
    college_ids: List[str] = Field(..., min_length=2, max_length=5)
    branch: str = Field(default="CSE")
    category: str = Field(default="GM")


class CompareResponse(BaseModel):
    """Compare colleges response."""
    colleges: List[Dict[str, Any]]
    comparison_matrix: Dict[str, Any]
    recommendation: str


# ── Scholarship Schemas ───────────────────────────────────────────────────────

class ScholarshipCheckRequest(BaseModel):
    """Scholarship eligibility check request."""
    category: str = Field(default="GM")
    income_lakhs: Optional[float] = None
    gender: Optional[str] = None
    rank: Optional[int] = None
    marks: Optional[float] = None


# ── Health Schemas ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    database: Dict[str, Any]
    engines: Dict[str, bool]
    version: str = "2.0.0"
