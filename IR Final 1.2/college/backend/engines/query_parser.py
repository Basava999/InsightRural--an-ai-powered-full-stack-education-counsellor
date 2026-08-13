# ==============================================================================
# InsightRural — Layer 1: Query Understanding Engine
# ==============================================================================
# Extracts structured profile data from natural language queries.
# Uses regex + keyword matching — NO LLM. This ensures the parsing is
# deterministic, fast, and reproducible.
#
# Handles both:
#   1. Structured form input (from frontend predictor page)
#   2. Natural language chat messages (from chat interface)
# ==============================================================================

import re
import logging
from typing import Dict, Any, Optional, List, Tuple

from models.schemas import StudentProfile

logger = logging.getLogger("QueryParser")


# ── Regex Patterns ────────────────────────────────────────────────────────────

RANK_PATTERN = re.compile(
    r'(?:my\s+)?(?:kcet\s+)?rank\s*(?:is|:)?\s*(\d{1,6})',
    re.IGNORECASE
)
RANK_PATTERN_ALT = re.compile(
    r'(\d{1,6})\s*(?:rank|kcet)',
    re.IGNORECASE
)
RANK_PATTERN_INLINE = re.compile(
    r'(?:rank)\s*[-:]?\s*(\d{1,6})',
    re.IGNORECASE
)

BUDGET_PATTERN = re.compile(
    r'(?:budget|fee|afford|pay)\s*(?:is|:|\s)?\s*(?:₹|rs\.?|inr)?\s*'
    r'(\d[\d,]*)\s*(?:lakh|lac|l|k)?',
    re.IGNORECASE
)
BUDGET_UNDER_PATTERN = re.compile(
    r'(?:under|below|less\s+than|max(?:imum)?|within)\s*(?:₹|rs\.?|inr)?\s*'
    r'(\d[\d,]*)\s*(?:lakh|lac|l|k)?',
    re.IGNORECASE
)

CATEGORY_PATTERN = re.compile(
    r'\b(GM|SC|ST|OBC|CAT[- ]?1|CATEGORY[- ]?1|2A|2B|3A|3B|EWS|'
    r'general\s*merit|general|schedule[d]?\s*caste|schedule[d]?\s*tribe)\b',
    re.IGNORECASE
)

BRANCH_KEYWORDS = {
    "cse": "CSE", "computer science": "CSE", "cs": "CSE",
    "ise": "ISE", "information science": "ISE",
    "ece": "ECE", "electronics": "ECE", "e&c": "ECE",
    "eee": "EEE", "electrical": "EEE",
    "mech": "ME", "mechanical": "ME",
    "civil": "CIVIL",
    "ai": "AI", "aiml": "AI", "ai & ml": "AI", "artificial intelligence": "AI",
    "ds": "DS", "data science": "DS", "ai & ds": "AI_DS",
    "cyber": "CY", "cyber security": "CY",
    "biotech": "BIOTECH", "biotechnology": "BIOTECH",
    "aero": "AERO", "aeronautical": "AERO", "aerospace": "AERO",
    "chemical": "CHEM",
    "mining": "MINING",
    "automobile": "AUTO",
    "it": "ISE", "information technology": "ISE",
}

CITY_KEYWORDS = [
    "bangalore", "bengaluru", "mysore", "mysuru", "mangalore", "mangaluru",
    "hubli", "hubballi", "dharwad", "dharwar", "belgaum", "belagavi",
    "gulbarga", "kalaburagi", "davanagere", "davangere", "shimoga",
    "shivamogga", "tumkur", "tumakuru", "bellary", "ballari",
    "hassan", "mandya", "raichur", "udupi", "chitradurga", "bidar",
    "haveri", "gadag", "chikmagalur", "chikkamagaluru", "karwar",
    "bagalkot", "koppal", "yadgir", "chamarajanagar", "kodagu",
    "kolar", "chikkaballapur", "ramanagara",
]

LOCATION_PATTERN = re.compile(
    r'\b(' + '|'.join(CITY_KEYWORDS) + r')\b',
    re.IGNORECASE
)

HOSTEL_KEYWORDS = ["hostel", "accommodation", "staying", "need hostel", "with hostel"]
RURAL_KEYWORDS = ["rural", "rural quota", "rural area"]
KANNADA_KEYWORDS = ["kannada medium", "kannada"]
GOVT_KEYWORDS = ["government college", "government only", "govt college", "govt only"]
PRIVATE_KEYWORDS = ["private college", "private only", "pvt"]
HK_KEYWORDS = ["hyderabad karnataka", "371j", "hk region", "hk quota"]
SNQ_KEYWORDS = ["supernumerary", "snq", "divyang", "disability"]

GENDER_PATTERN = re.compile(r'\b(male|female|girl|boy|woman|man)\b', re.IGNORECASE)


class QueryParser:
    """
    Deterministic query parser. Extracts structured profile data from
    natural language. No LLM dependency.
    """

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Backward compatible parse method returning a raw dictionary.
        """
        # Parse using internal helper methods
        rank = self._extract_rank(query)
        category = self._extract_category(query)
        branches = self._extract_branches(query)
        locations = self._extract_locations(query)
        budget = self._extract_budget(query)
        gender = self._extract_gender(query)

        result = {
            "rank": rank or 50000,
            "kcet_rank": rank or 50000,
            "category": category or "GM",
            "branch": branches[0] if branches else "CSE",
            "preferred_branch": branches[0] if branches else "CSE",
            "location": locations[0] if locations else None,
            "city": locations[0] if locations else None,
            "intent": "general",
        }
        query_lower = query.lower()
        if any(kw in query_lower for kw in HOSTEL_KEYWORDS):
            result["is_hostel_query"] = True
            result["intent"] = "hostel"
        if any(kw in query_lower for kw in RURAL_KEYWORDS):
            result["rural_quota"] = True
        if any(kw in query_lower for kw in KANNADA_KEYWORDS):
            result["kannada_medium"] = True
        if any(kw in query_lower for kw in HK_KEYWORDS):
            result["hk_371j"] = True
        if any(kw in query_lower for kw in SNQ_KEYWORDS):
            result["snq"] = True
        if "scholarship" in query_lower or "concession" in query_lower or "fee waiver" in query_lower:
            result["is_scholarship_query"] = True
            result["intent"] = "scholarship"
        return result

    def parse_chat_query(

        self,
        query: str,
        existing_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[StudentProfile, Dict[str, Any]]:
        """
        Parse a chat message into a StudentProfile.
        Merges with existing profile if available.

        Returns:
            Tuple of (StudentProfile, extraction_metadata)
        """
        extracted = {}
        metadata = {"source": "chat", "raw_query": query}

        # ── Extract rank ──────────────────────────────────────────────
        rank = self._extract_rank(query)
        if rank:
            extracted["rank"] = rank

        # ── Extract category ──────────────────────────────────────────
        category = self._extract_category(query)
        if category:
            extracted["category"] = category

        # ── Extract branches ──────────────────────────────────────────
        branches = self._extract_branches(query)
        if branches:
            extracted["preferred_branches"] = branches

        # ── Extract location ──────────────────────────────────────────
        locations = self._extract_locations(query)
        if locations:
            extracted["preferred_locations"] = locations

        # ── Extract budget ────────────────────────────────────────────
        budget = self._extract_budget(query)
        if budget:
            extracted["budget"] = budget

        # ── Extract gender ────────────────────────────────────────────
        gender = self._extract_gender(query)
        if gender:
            extracted["gender"] = gender

        # ── Extract boolean flags ─────────────────────────────────────
        query_lower = query.lower()

        if any(kw in query_lower for kw in HOSTEL_KEYWORDS):
            extracted["hostel_required"] = True

        if any(kw in query_lower for kw in RURAL_KEYWORDS):
            extracted["rural_quota"] = True

        if any(kw in query_lower for kw in KANNADA_KEYWORDS):
            extracted["kannada_medium"] = True

        if any(kw in query_lower for kw in HK_KEYWORDS):
            extracted["hk_371j"] = True

        if any(kw in query_lower for kw in SNQ_KEYWORDS):
            extracted["snq"] = True

        if any(kw in query_lower for kw in GOVT_KEYWORDS):
            extracted["college_type"] = "Government"
        elif any(kw in query_lower for kw in PRIVATE_KEYWORDS):
            extracted["college_type"] = "Private"

        # ── Merge with existing profile ───────────────────────────────
        merged = dict(existing_profile or {})
        merged.update(extracted)

        # Ensure required fields have defaults
        if "rank" not in merged:
            merged["rank"] = 50000  # Default for general query
            metadata["rank_source"] = "default"
        else:
            metadata["rank_source"] = "extracted"

        if "preferred_branches" not in merged:
            merged["preferred_branches"] = ["CSE"]
            metadata["branch_source"] = "default"
        else:
            metadata["branch_source"] = "extracted"

        metadata["fields_extracted"] = list(extracted.keys())

        try:
            profile = StudentProfile(**merged)
        except Exception as e:
            logger.warning(f"Profile validation error: {e}. Using defaults.")
            profile = StudentProfile(rank=merged.get("rank", 50000))

        return profile, metadata

    def parse_form_input(self, data: Dict[str, Any]) -> StudentProfile:
        """
        Parse structured form input directly into StudentProfile.
        This handles the frontend predictor form submission.
        """
        # Map frontend field names to schema field names
        mapped = {}

        mapped["rank"] = int(data.get("kcet_rank") or data.get("rank", 50000))
        mapped["category"] = data.get("category", "GM")
        mapped["gender"] = data.get("gender")
        mapped["exam"] = data.get("exam", "KCET")

        # Branches
        branches = data.get("preferred_branches") or data.get("branch")
        if isinstance(branches, str):
            mapped["preferred_branches"] = [b.strip() for b in branches.split(",")]
        elif isinstance(branches, list):
            mapped["preferred_branches"] = branches
        else:
            mapped["preferred_branches"] = ["CSE"]

        # Location
        location = data.get("preferred_locations") or data.get("location")
        if location:
            if isinstance(location, str):
                mapped["preferred_locations"] = [l.strip() for l in location.split(",")]
            elif isinstance(location, list):
                mapped["preferred_locations"] = location

        # Budget
        budget = data.get("budget")
        if budget:
            mapped["budget"] = int(budget)

        # College type
        mapped["college_type"] = data.get("college_type")

        # Hostel
        hostel = data.get("hostel_required") or data.get("hostel_needed")
        mapped["hostel_required"] = bool(hostel)

        # Quotas
        mapped["rural_quota"] = bool(data.get("rural_quota"))
        mapped["kannada_medium"] = bool(data.get("kannada_medium"))
        mapped["snq"] = bool(data.get("snq") or data.get("snq_quota"))
        mapped["hk_371j"] = bool(data.get("hk_371j") or data.get("hyderabad_karnataka"))
        mapped["minority"] = bool(data.get("minority"))

        # Academic
        puc = data.get("puc_marks")
        if puc and isinstance(puc, dict):
            mapped["puc_marks"] = puc
        kcet = data.get("kcet_marks")
        if kcet and isinstance(kcet, dict):
            mapped["kcet_marks"] = kcet

        income = data.get("income_lakhs") or data.get("income")
        if income:
            val = float(income)
            # Auto-detect: if > 100, it's INR not lakhs
            mapped["income_lakhs"] = val / 100000 if val > 100 else val

        return StudentProfile(**mapped)

    # ══════════════════════════════════════════════════════════════════════════
    # Individual Extractors
    # ══════════════════════════════════════════════════════════════════════════

    def _extract_rank(self, query: str) -> Optional[int]:
        """Extract KCET rank from natural language."""
        for pattern in [RANK_PATTERN, RANK_PATTERN_ALT, RANK_PATTERN_INLINE]:
            match = pattern.search(query)
            if match:
                rank = int(match.group(1))
                if 1 <= rank <= 500000:
                    return rank

        # Fallback: look for standalone large numbers that could be ranks
        numbers = re.findall(r'\b(\d{3,6})\b', query)
        for num_str in numbers:
            num = int(num_str)
            if 100 <= num <= 250000:
                # Check it's not a fee amount (usually > 10000 with ₹/rs prefix)
                fee_context = re.search(
                    r'(?:₹|rs\.?|fee|budget|cost)\s*' + num_str, query, re.IGNORECASE
                )
                if not fee_context:
                    return num

        return None

    def _extract_category(self, query: str) -> Optional[str]:
        """Extract reservation category."""
        match = CATEGORY_PATTERN.search(query)
        if match:
            cat = match.group(1).upper().strip()

            # Map verbose names
            verbose_map = {
                "GENERAL MERIT": "GM", "GENERAL": "GM",
                "SCHEDULED CASTE": "SC", "SCHEDULE CASTE": "SC",
                "SCHEDULED TRIBE": "ST", "SCHEDULE TRIBE": "ST",
            }
            return verbose_map.get(cat, cat.replace(" ", "").replace("-", ""))

        return None

    def _extract_branches(self, query: str) -> Optional[List[str]]:
        """Extract preferred branches from query."""
        query_lower = query.lower()
        found = []
        seen = set()

        for keyword, branch_code in BRANCH_KEYWORDS.items():
            if keyword in query_lower and branch_code not in seen:
                found.append(branch_code)
                seen.add(branch_code)

        return found if found else None

    def _extract_locations(self, query: str) -> Optional[List[str]]:
        """Extract preferred locations from query."""
        matches = LOCATION_PATTERN.findall(query)
        if matches:
            # Capitalize for consistency
            return list({m.strip().capitalize() for m in matches})
        return None

    def _extract_budget(self, query: str) -> Optional[int]:
        """Extract budget amount from query."""
        for pattern in [BUDGET_PATTERN, BUDGET_UNDER_PATTERN]:
            match = pattern.search(query)
            if match:
                num_str = match.group(1).replace(",", "")
                num = int(num_str)

                # Detect unit
                full_match = match.group(0).lower()
                if "lakh" in full_match or "lac" in full_match:
                    return num * 100000
                elif full_match.endswith("l"):
                    return num * 100000
                elif full_match.endswith("k"):
                    return num * 1000
                elif num < 100:
                    # Likely in lakhs
                    return num * 100000
                else:
                    return num

        return None

    def _extract_gender(self, query: str) -> Optional[str]:
        """Extract gender from query."""
        match = GENDER_PATTERN.search(query)
        if match:
            g = match.group(1).lower()
            if g in ("male", "boy", "man"):
                return "Male"
            elif g in ("female", "girl", "woman"):
                return "Female"
        return None

    # ══════════════════════════════════════════════════════════════════════════
    # Query Intent Detection
    # ══════════════════════════════════════════════════════════════════════════

    def detect_intent(self, query: str) -> str:
        """
        Detect query intent for routing to appropriate engine.

        Returns one of:
            'recommendation', 'scholarship', 'loan', 'hostel',
            'fee', 'counseling', 'comparison', 'cutoff', 'general'
        """
        query_lower = query.lower()

        # Recommendation intent (rank-based college search)
        recommendation_kw = [
            "recommend", "best college", "which college", "college for",
            "can i get", "will i get", "predict", "admission chance",
            "options for rank", "suggest college", "my rank",
        ]
        if any(kw in query_lower for kw in recommendation_kw):
            return "recommendation"

        # Check if query contains rank + branch (implicit recommendation)
        if self._extract_rank(query) and self._extract_branches(query):
            return "recommendation"

        # Comparison intent
        comparison_kw = ["compare", "vs", "versus", "difference between", "which is better"]
        if any(kw in query_lower for kw in comparison_kw):
            return "comparison"

        # Scholarship intent
        scholarship_kw = [
            "scholarship", "vidyasiri", "post matric", "fee waiver",
            "ssp", "stipend", "financial aid", "grant",
        ]
        if any(kw in query_lower for kw in scholarship_kw):
            return "scholarship"

        # Loan intent
        loan_kw = ["loan", "education loan", "sbi", "interest", "emi", "collateral", "ciss"]
        if any(kw in query_lower for kw in loan_kw):
            return "loan"

        # Hostel intent
        hostel_kw = ["hostel", "accommodation", "pg", "mess", "dormitory", "bcm hostel"]
        if any(kw in query_lower for kw in hostel_kw):
            return "hostel"

        # Fee intent
        fee_kw = ["fee", "fees", "tuition", "cost", "afford", "fee structure", "how much"]
        if any(kw in query_lower for kw in fee_kw):
            return "fee"

        # Counseling process intent
        counseling_kw = [
            "counseling", "counselling", "process", "document verification",
            "option entry", "allotment", "choice filling", "kea process",
        ]
        if any(kw in query_lower for kw in counseling_kw):
            return "counseling"

        # Cutoff intent
        cutoff_kw = ["cutoff", "cut off", "closing rank", "last rank", "trend"]
        if any(kw in query_lower for kw in cutoff_kw):
            return "cutoff"

        return "general"
