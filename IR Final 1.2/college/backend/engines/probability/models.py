# InsightRural Probability Models
"""
InsightRural 3.0
Probability Engine Models

Author: InsightRural

Shared data models used by the Probability Engine.

These models should NEVER contain business logic.
Only data structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ==========================================================
# Student Profile
# ==========================================================

@dataclass
class StudentProfile:

    rank: int

    category: str

    branch: str

    exam: str = "KCET"

    round: int = 1

    year: int = 2026

    gender: Optional[str] = None

    income: Optional[float] = None

    district: Optional[str] = None

    state: str = "Karnataka"

    budget: Optional[float] = None

    hostel_required: bool = False

    rural: bool = False

    snq: bool = False

    pwd: bool = False

    ews: bool = False

    kannada_medium: bool = False

    hk_region: bool = False

    defence: bool = False

    sports: bool = False

    ex_serviceman: bool = False

    preferred_college: Optional[str] = None

    preferred_location: Optional[str] = None

    preferred_college_type: Optional[str] = None


# ==========================================================
# Cutoff Record
# ==========================================================

@dataclass
class CutoffRecord:

    year: int

    round: int

    closing_rank: int

    category: str

    seats: Optional[int] = None


# ==========================================================
# College Record
# ==========================================================

@dataclass
class CollegeRecord:

    college_code: str

    college_name: str

    branch: str

    category: str

    district: str

    annual_fee: float

    hostel_available: bool

    hostel_fee: Optional[float]

    placement_average: Optional[float]

    placement_highest: Optional[float]

    nirf_rank: Optional[int]

    college_type: str

    seat_intake: Optional[int]

    cutoff_history: List[CutoffRecord] = field(default_factory=list)


# ==========================================================
# Trend Analysis
# ==========================================================

@dataclass
class TrendResult:

    predicted_cutoff: float

    moving_average: float

    slope: float

    trend: str

    confidence: float


# ==========================================================
# Score Breakdown
# ==========================================================

@dataclass
class ScoreBreakdown:

    historical_score: float

    distance_score: float

    reservation_score: float

    seat_score: float

    trend_score: float

    popularity_score: float

    final_score: float


# ==========================================================
# Final Prediction
# ==========================================================

@dataclass
class ProbabilityResult:

    probability: float

    chance: str

    confidence: str

    predicted_cutoff: int

    score_breakdown: ScoreBreakdown

    trend: TrendResult

    explanation: List[str]

    warnings: List[str] = field(default_factory=list)
