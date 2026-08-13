"""
Layer 1: User Query Understanding
Extracts structured student profile from natural language or JSON.
No LLM required — regex + keyword extraction for determinism.
"""

import re
from typing import Any, Dict, Optional

from app.schemas.student import QueryUnderstandingResult, StudentProfile


RANK_PATTERNS = [
    re.compile(r"(?:rank|kcet\s*rank|my\s*rank)\s*(?:is|:)?\s*(\d{1,6})", re.I),
    re.compile(r"(\d{1,6})\s*(?:rank|kcet)", re.I),
]

BRANCH_KEYWORDS = {
    "CSE": ["cse", "computer science", "cs"],
    "ECE": ["ece", "electronics"],
    "ISE": ["ise", "information science"],
    "EEE": ["eee", "electrical"],
    "ME": ["me", "mechanical"],
    "CIVIL": ["civil"],
    "AI": ["ai", "artificial intelligence"],
    "DS": ["ds", "data science"],
    "CY": ["cyber", "cybersecurity"],
}

CITY_ALIASES = {
    "bangalore": ["bangalore", "bengaluru", "blr"],
    "mysore": ["mysore", "mysuru"],
    "mangalore": ["mangalore", "mangaluru"],
    "hubli": ["hubli", "hubballi"],
    "belgaum": ["belgaum", "belagavi"],
    "tumkur": ["tumkur", "tumakuru"],
    "davangere": ["davangere"],
    "shimoga": ["shimoga", "shivamogga"],
}

CATEGORY_PATTERNS = [
    (re.compile(r"\b(sc|scheduled caste)\b", re.I), "SC"),
    (re.compile(r"\b(st|scheduled tribe)\b", re.I), "ST"),
    (re.compile(r"\b(obc|2a|2b|3a|3b|cat.?1)\b", re.I), "OBC"),
    (re.compile(r"\b(gm|general|gen)\b", re.I), "GM"),
]

BUDGET_PATTERN = re.compile(
    r"(?:budget|fee|fees|afford|max(?:imum)?)\s*(?:is|:)?\s*(?:rs\.?|₹|inr)?\s*(\d[\d,]*)",
    re.I,
)


class QueryUnderstandingEngine:
    """Extract structured JSON from user query or explicit profile."""

    def parse(self, query: str, profile: Optional[StudentProfile] = None) -> QueryUnderstandingResult:
        if profile:
            return QueryUnderstandingResult(
                rank=profile.rank,
                category=profile.category,
                gender=profile.gender,
                branch=profile.branch,
                city=profile.city,
                district=profile.district,
                hostel_required=profile.hostel_required,
                budget=profile.budget,
                rural=profile.rural,
                kannada_medium=profile.kannada_medium,
                snq=profile.snq,
                hk_371j=profile.hk_371j,
                minority=profile.minority,
                college_type=profile.college_type,
                raw_query=query,
                extraction_confidence=1.0,
            )

        text = (query or "").strip()
        result = QueryUnderstandingResult(raw_query=text, extraction_confidence=0.5)
        fields_found = 0

        for pattern in RANK_PATTERNS:
            m = pattern.search(text)
            if m:
                result.rank = int(m.group(1))
                fields_found += 1
                break

        for pattern, cat in CATEGORY_PATTERNS:
            if pattern.search(text):
                result.category = cat
                fields_found += 1
                break

        text_lower = text.lower()
        for branch_code, keywords in BRANCH_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                result.branch = branch_code
                fields_found += 1
                break

        for city, aliases in CITY_ALIASES.items():
            if any(alias in text_lower for alias in aliases):
                result.city = city.title()
                fields_found += 1
                break

        bm = BUDGET_PATTERN.search(text)
        if bm:
            result.budget = int(bm.group(1).replace(",", ""))
            fields_found += 1

        if re.search(r"\bhostel\b", text_lower):
            result.hostel_required = "no hostel" not in text_lower and "without hostel" not in text_lower
            fields_found += 1

        if re.search(r"\brural\b", text_lower):
            result.rural = True
            fields_found += 1
        if re.search(r"\bkannada\s*medium\b", text_lower):
            result.kannada_medium = True
            fields_found += 1
        if re.search(r"\b371\s*j\b|\bhk\b", text_lower):
            result.hk_371j = True
            fields_found += 1
        if re.search(r"\bgovernment\b|\bgovt\b", text_lower):
            result.college_type = "Government"
            fields_found += 1
        elif re.search(r"\bprivate\b", text_lower):
            result.college_type = "Private"
            fields_found += 1

        if result.rank:
            result.extraction_confidence = min(1.0, 0.4 + fields_found * 0.1)
        else:
            result.extraction_confidence = max(0.2, fields_found * 0.08)

        return result

    def to_profile(self, parsed: QueryUnderstandingResult) -> Optional[StudentProfile]:
        if not parsed.rank or parsed.rank <= 0:
            return None
        return StudentProfile(
            rank=parsed.rank,
            category=parsed.category,
            gender=parsed.gender,
            branch=parsed.branch,
            city=parsed.city,
            district=parsed.district,
            hostel_required=parsed.hostel_required,
            budget=parsed.budget,
            rural=parsed.rural,
            kannada_medium=parsed.kannada_medium,
            snq=parsed.snq,
            hk_371j=parsed.hk_371j,
            minority=parsed.minority,
            college_type=parsed.college_type,
        )
