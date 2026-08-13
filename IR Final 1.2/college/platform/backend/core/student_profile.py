"""
StudentProfile Engine — Extracts structured profile from natural language input.
ALL decisions are deterministic. LLM is never used here.
"""

import re
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


# ── Known branch aliases ──────────────────────────────────────────────────────
BRANCH_ALIASES: Dict[str, str] = {
    "computer science": "CSE", "cse": "CSE", "cs": "CSE", "comps": "CSE",
    "software engineering": "CSE", "it": "ISE", "information science": "ISE",
    "ise": "ISE", "information technology": "ISE",
    "electronics": "ECE", "ece": "ECE", "e&c": "ECE", "e and c": "ECE",
    "electrical": "EEE", "eee": "EEE", "e&e": "EEE",
    "mechanical": "ME", "mech": "ME", "me": "ME",
    "civil": "CIVIL", "civil engineering": "CIVIL",
    "artificial intelligence": "AI_DS", "ai": "AI_DS",
    "ai&ds": "AI_DS", "ai and ds": "AI_DS", "aids": "AI_DS",
    "data science": "AI_DS", "ds": "AI_DS",
    "machine learning": "ML", "ml": "ML",
    "aiml": "AI_DS", "ai&ml": "AI_DS",
    "cyber security": "CY", "cybersecurity": "CY", "cs cy": "CY", "cy": "CY",
    "aerospace": "AERO", "aeronautical": "AERO", "aero": "AERO",
    "chemical": "CHEM", "chemical engineering": "CHEM",
    "biotechnology": "BIOTECH", "biotech": "BIOTECH",
    "industrial": "IE", "industrial engineering": "IE",
    "automobile": "AUTO", "automotive": "AUTO",
}

# ── Category aliases ──────────────────────────────────────────────────────────
CATEGORY_ALIASES: Dict[str, str] = {
    "general": "GM", "gm": "GM", "oc": "GM", "open": "GM", "unreserved": "GM",
    "sc": "SC", "scheduled caste": "SC", "dalit": "SC",
    "st": "ST", "scheduled tribe": "ST", "tribal": "ST",
    "obc": "OBC", "2a": "2A", "2b": "2B", "3a": "3A", "3b": "3B",
    "cat1": "CAT1", "cat-1": "CAT1", "category 1": "CAT1", "category-1": "CAT1",
    "ews": "EWS", "economically weaker": "EWS",
}

# ── Karnataka city normalizations ─────────────────────────────────────────────
CITY_ALIASES: Dict[str, str] = {
    "bangalore": "Bangalore", "bengaluru": "Bangalore", "blr": "Bangalore",
    "mysore": "Mysore", "mysuru": "Mysore",
    "mangalore": "Mangalore", "mangaluru": "Mangalore",
    "hubli": "Hubli", "hubballi": "Hubli",
    "dharwad": "Dharwad",
    "belgaum": "Belagavi", "belagavi": "Belagavi",
    "bellary": "Ballari", "ballari": "Ballari",
    "gulbarga": "Kalaburagi", "kalaburagi": "Kalaburagi",
    "bidar": "Bidar", "raichur": "Raichur",
    "davanagere": "Davanagere", "davangere": "Davanagere",
    "tumkur": "Tumkur", "tumakuru": "Tumkur",
    "shimoga": "Shivamogga", "shivamogga": "Shivamogga",
    "hassan": "Hassan", "udupi": "Udupi",
    "chikmagalur": "Chikkamagaluru", "chikkamagaluru": "Chikkamagaluru",
}

# ── Hyderabad-Karnataka districts ─────────────────────────────────────────────
HK_DISTRICTS = {
    "bidar", "gulbarga", "kalaburagi", "yadgir", "raichur",
    "koppal", "bellary", "ballari", "vijayanagara", "bagalkot"
}


@dataclass
class StudentProfile:
    """
    Fully structured student profile.
    All fields are deterministically extracted — never invented.
    """
    # Core exam data
    rank: Optional[int] = None
    category: str = "GM"
    gender: str = "male"

    # Branch preferences (ordered)
    preferred_branches: List[str] = field(default_factory=list)

    # Location preferences
    preferred_locations: List[str] = field(default_factory=list)
    preferred_district: Optional[str] = None

    # Budget
    budget: Optional[int] = None  # Annual fee budget in ₹

    # Hostel
    hostel_required: bool = False

    # College type preference
    college_type: Optional[str] = None  # "Government", "Private", "Aided"

    # Special quotas / reservations
    rural_quota: bool = False
    kannada_medium: bool = False
    snq: bool = False          # Supernumerary (PwD / ex-serviceman)
    hk_371j: bool = False      # Hyderabad-Karnataka 371(J)
    minority_status: bool = False

    # Income (for scholarship eligibility)
    annual_income: Optional[int] = None

    # Extraction metadata
    extraction_confidence: float = 0.0
    missing_fields: List[str] = field(default_factory=list)
    raw_input: str = ""

    @property
    def fee_category_key(self) -> str:
        """Map student category to fee lookup key."""
        cat = self.category.upper()
        if cat in ("SC", "ST"):
            return "sc_st"
        elif cat in ("OBC", "2A", "2B", "3A", "3B", "CAT1"):
            return "obc"
        return "gm"

    @property
    def is_hk_eligible(self) -> bool:
        """True if student is from HK region."""
        loc = (self.preferred_district or "").lower()
        return loc in HK_DISTRICTS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProfileExtractor:
    """
    Deterministic NLP parser for student queries.
    Extracts structured StudentProfile from natural language.
    Never uses LLM. Never invents data.
    """

    def extract(self, text: str) -> StudentProfile:
        """Main entry point — extract profile from free text."""
        text_lower = text.lower().strip()
        profile = StudentProfile(raw_input=text)

        # Extract each field deterministically
        profile.rank = self._extract_rank(text_lower)
        profile.category = self._extract_category(text_lower)
        profile.gender = self._extract_gender(text_lower)
        profile.preferred_branches = self._extract_branches(text_lower)
        profile.preferred_locations = self._extract_locations(text_lower)
        profile.budget = self._extract_budget(text_lower)
        profile.hostel_required = self._extract_hostel(text_lower)
        profile.college_type = self._extract_college_type(text_lower)
        profile.rural_quota = self._extract_rural(text_lower)
        profile.kannada_medium = self._extract_kannada_medium(text_lower)
        profile.hk_371j = self._extract_371j(text_lower)
        profile.snq = self._extract_snq(text_lower)
        profile.annual_income = self._extract_income(text_lower)

        # Calculate confidence
        profile.extraction_confidence = self._confidence(profile)
        profile.missing_fields = self._missing(profile)

        return profile

    def update(self, existing: StudentProfile, new_text: str) -> StudentProfile:
        """
        Update existing profile with new information from follow-up input.
        Only overwrites fields that are explicitly mentioned in the new text.
        """
        new_lower = new_text.lower().strip()

        new_rank = self._extract_rank(new_lower)
        if new_rank:
            existing.rank = new_rank

        new_cat = self._extract_category(new_lower)
        if new_cat != "GM" or "general" in new_lower:
            existing.category = new_cat

        new_branches = self._extract_branches(new_lower)
        if new_branches:
            # Merge (new preferences take priority at front)
            merged = new_branches + [b for b in existing.preferred_branches if b not in new_branches]
            existing.preferred_branches = merged

        new_locs = self._extract_locations(new_lower)
        if new_locs:
            merged = new_locs + [l for l in existing.preferred_locations if l not in new_locs]
            existing.preferred_locations = merged

        new_budget = self._extract_budget(new_lower)
        if new_budget:
            existing.budget = new_budget

        if self._extract_hostel(new_lower):
            existing.hostel_required = True

        new_type = self._extract_college_type(new_lower)
        if new_type:
            existing.college_type = new_type

        # Update quotas
        if self._extract_rural(new_lower):
            existing.rural_quota = True
        if self._extract_371j(new_lower):
            existing.hk_371j = True
        if self._extract_kannada_medium(new_lower):
            existing.kannada_medium = True
        if self._extract_snq(new_lower):
            existing.snq = True

        new_income = self._extract_income(new_lower)
        if new_income:
            existing.annual_income = new_income

        # Recalculate
        existing.extraction_confidence = self._confidence(existing)
        existing.missing_fields = self._missing(existing)
        existing.raw_input = existing.raw_input + " | " + new_text

        return existing

    # ──────────────────────────────────────────────────────────────────────────
    # Individual field extractors (ALL deterministic)
    # ──────────────────────────────────────────────────────────────────────────

    def _extract_rank(self, text: str) -> Optional[int]:
        """Extract KCET rank from text."""
        patterns = [
            r'(?:kcet|cet|rank)[\s:=]*(?:is\s*)?(\d{1,6})',
            r'rank[\s:=]*(?:of\s*)?(\d{1,6})',
            r'(\d{1,6})\s*(?:kcet\s+)?rank',
            r'my\s+rank\s+(?:is\s+)?(\d{1,6})',
            r'scored?\s+(\d{1,6})\s*(?:in\s+)?(?:kcet|rank)',
            r'got\s+(\d{1,6})\s*(?:rank)?',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 300000:  # Valid KCET rank range
                    return val
        return None

    def _extract_category(self, text: str) -> str:
        """Extract reservation category."""
        for alias, cat in CATEGORY_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', text):
                return cat
        return "GM"

    def _extract_gender(self, text: str) -> str:
        """Extract gender."""
        if re.search(r'\b(female|girl|woman|f)\b', text):
            return "female"
        if re.search(r'\b(male|boy|man|m)\b', text):
            return "male"
        return "male"

    def _extract_branches(self, text: str) -> List[str]:
        """Extract preferred branches in order of mention."""
        found = []
        found_positions = []

        for alias, branch in BRANCH_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            m = re.search(pattern, text)
            if m and branch not in found:
                found.append(branch)
                found_positions.append((m.start(), branch))

        # Sort by position in text (preserves user's priority order)
        found_positions.sort(key=lambda x: x[0])
        return [b for _, b in found_positions]

    def _extract_locations(self, text: str) -> List[str]:
        """Extract preferred cities/districts."""
        found = []
        for alias, city in CITY_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', text):
                if city not in found:
                    found.append(city)
        return found

    def _extract_budget(self, text: str) -> Optional[int]:
        """Extract budget in ₹. Handles lakhs, thousands, ranges."""
        # Patterns: "below 1 lakh", "under 50000", "budget 1.5 lakh"
        lakh_pattern = r'(?:below|under|within|budget|upto?|less\s+than)\s*(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*lakh'
        m = re.search(lakh_pattern, text)
        if m:
            return int(float(m.group(1)) * 100000)

        # "1,00,000" or "100000"
        rupee_pattern = r'(?:below|under|within|budget|upto?|less\s+than)\s*(?:rs\.?\s*)?(\d[\d,]*)'
        m = re.search(rupee_pattern, text)
        if m:
            val = int(m.group(1).replace(",", ""))
            if 1000 <= val <= 5000000:
                return val

        # Standalone lakh mention
        lakh2 = r'(\d+(?:\.\d+)?)\s*lakh'
        m = re.search(lakh2, text)
        if m and any(w in text for w in ["budget", "fee", "cost", "afford"]):
            return int(float(m.group(1)) * 100000)

        return None

    def _extract_hostel(self, text: str) -> bool:
        """Check if hostel is required."""
        return bool(re.search(r'\b(hostel|accommodation|stay|boarding|residential)\b', text))

    def _extract_college_type(self, text: str) -> Optional[str]:
        """Extract college type preference."""
        if re.search(r'\b(govt\.?|government|sarkari)\b', text):
            return "Government"
        if re.search(r'\b(private|pvt\.?)\b', text):
            return "Private"
        if re.search(r'\b(aided|government.?aided)\b', text):
            return "Aided"
        return None

    def _extract_rural(self, text: str) -> bool:
        """Check rural quota eligibility."""
        return bool(re.search(r'\b(rural|village|gram|countryside)\b', text))

    def _extract_kannada_medium(self, text: str) -> bool:
        """Check Kannada medium quota."""
        return bool(re.search(r'\b(kannada\s*medium|km\s*quota|studied\s*in\s*kannada)\b', text))

    def _extract_371j(self, text: str) -> bool:
        """Check 371(J) HK region eligibility."""
        return bool(re.search(r'\b(371j|371\(j\)|hyderabad.?karnataka|hk\s*region)\b', text))

    def _extract_snq(self, text: str) -> bool:
        """Check supernumerary quota (PwD / ex-serviceman)."""
        return bool(re.search(r'\b(pwd|disabled|differently.?abled|ex.?service|snq)\b', text))

    def _extract_income(self, text: str) -> Optional[int]:
        """Extract annual income for scholarship eligibility."""
        # "income below 2.5 lakh", "family income 1 lakh"
        m = re.search(r'(?:annual\s+)?income[\s:]*(?:below|under|of|is)?\s*(?:rs\.?\s*)?(\d+(?:\.\d+)?)\s*lakh', text)
        if m:
            return int(float(m.group(1)) * 100000)
        m = re.search(r'(?:annual\s+)?income[\s:]*(?:rs\.?\s*)?(\d[\d,]+)', text)
        if m:
            val = int(m.group(1).replace(",", ""))
            if 10000 <= val <= 5000000:
                return val
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # Quality checks
    # ──────────────────────────────────────────────────────────────────────────

    def _confidence(self, profile: StudentProfile) -> float:
        """Calculate extraction confidence (0-1)."""
        score = 0.0
        if profile.rank:
            score += 0.40
        if profile.preferred_branches:
            score += 0.25
        if profile.category != "GM" or True:  # GM is a valid default
            score += 0.15
        if profile.preferred_locations:
            score += 0.10
        if profile.budget:
            score += 0.10
        return min(1.0, score)

    def _missing(self, profile: StudentProfile) -> List[str]:
        """Identify critical missing fields."""
        missing = []
        if not profile.rank:
            missing.append("kcet_rank")
        if not profile.preferred_branches:
            missing.append("preferred_branch")
        return missing


# ── Singleton ────────────────────────────────────────────────────────────────
_extractor: Optional[ProfileExtractor] = None


def get_profile_extractor() -> ProfileExtractor:
    global _extractor
    if _extractor is None:
        _extractor = ProfileExtractor()
    return _extractor
