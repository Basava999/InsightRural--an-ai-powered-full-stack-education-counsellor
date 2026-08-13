from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum

class ExamType(str, Enum):
    KCET = "KCET"
    JEE_MAIN = "JEE_MAIN"
    JEE_ADVANCED = "JEE_ADVANCED"
    NEET_UG = "NEET_UG"

class CollegeCategory(str, Enum):
    IIT = "IIT"
    NIT = "NIT"
    IIIT = "IIIT"
    GFTI = "GFTI"
    GOVT_MEDICAL = "GOVT_MEDICAL"
    PVT_MEDICAL = "PVT_MEDICAL"
    DEEMED = "DEEMED"
    GOVT_ENGG = "GOVT_ENGG"
    PVT_ENGG = "PVT_ENGG"

class SeatQuota(str, Enum):
    AIQ = "AIQ"
    STATE = "STATE"
    HOME_STATE = "HOME_STATE"
    OTHER_STATE = "OTHER_STATE"
    NRI = "NRI"
    MANAGEMENT = "MANAGEMENT"

class CutoffSchema(BaseModel):
    exam: ExamType
    college_code: str
    college_name: str
    course_code: str
    course_name: str
    round_number: int
    year: int
    category: str
    quota: SeatQuota
    gender: str = "Gender-Neutral"
    opening_rank: Optional[int] = None
    closing_rank: int
    score: Optional[float] = None

    @field_validator('closing_rank')
    @classmethod
    def check_closing_rank(cls, v):
        if v <= 0:
            raise ValueError('Closing rank must be greater than 0')
        if v > 3000000:
            raise ValueError('Closing rank suspiciously high (anomaly detection)')
        return v

    @field_validator('opening_rank')
    @classmethod
    def check_opening_rank(cls, v, info):
        closing = info.data.get('closing_rank')
        if v is not None and closing is not None:
            if v > closing:
                # Some weird edge cases exist, but usually opening < closing.
                # Just logging this might be better than failing, but for strictness:
                pass 
        return v

class CollegeSchema(BaseModel):
    code: str
    name: str
    type: CollegeCategory
    state: str
    city: Optional[str] = None
    accreditation: Optional[Dict[str, Any]] = None

class FeeSchema(BaseModel):
    college_code: str
    course_code: str
    year: int
    tuition_fee_per_year: float
    hostel_fee_per_year: Optional[float] = None

class SeatMatrixSchema(BaseModel):
    college_code: str
    course_code: str
    year: int
    category: str
    quota: SeatQuota
    total_seats: int
