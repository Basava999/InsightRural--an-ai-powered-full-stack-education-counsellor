"""
==============================================================================
AI Student Success & Counseling Risk Analyzer — Full Production Engine
==============================================================================
Implements 11 scoring dimensions with Explainable AI logic.
Uses Feature Engineering, Multi-Criteria Decision Analysis, and
Behavioral Risk Profiling to generate actionable counseling insights.
==============================================================================
"""
import json
import math
from typing import Dict, Any, List, Tuple


# ============================================================================
# BRANCH FAMILY TAXONOMY
# ============================================================================
BRANCH_FAMILIES = {
    "tech": ["cse", "ise", "aiml", "ai", "ds", "data science", "ai & ds",
             "computer", "software", "information technology", "it", "cs",
             "ai & ml", "cyber security", "iot", "bca", "mca"],
    "electronics": ["ece", "electronics", "eee", "electrical", "e&c",
                     "instrumentation", "eie", "e&i"],
    "core": ["mech", "mechanical", "civil", "aeronautical", "aerospace",
             "automobile", "mining", "metallurgy", "industrial", "production"],
    "medical": ["mbbs", "bds", "dental", "ayush", "bsc nursing", "pharmacy",
                "biotech", "biotechnology", "medical"],
    "business": ["mba", "bba", "bcom", "commerce", "management"],
}

# Interest-to-branch alignment matrix
INTEREST_ALIGNMENT = {
    "tech": ["coding", "programming", "computers", "software", "ai",
             "machine learning", "data", "algorithms", "web", "app",
             "hacking", "python", "java", "robotics", "automation",
             "gaming", "competitive programming", "mathematics", "math"],
    "electronics": ["circuits", "hardware", "iot", "robotics", "physics",
                     "electronics", "signals", "vlsi", "embedded", "sensors",
                     "telecommunication", "radio"],
    "core": ["design", "machines", "physics", "construction", "mechanics",
             "automotive", "building", "manufacturing", "3d printing",
             "drafting", "structures", "engines", "vehicles"],
    "medical": ["biology", "chemistry", "anatomy", "medicine", "healthcare",
                "helping people", "research", "genetics", "hospitals",
                "pharmacology", "physiology", "life sciences", "biotech"],
    "business": ["business", "entrepreneurship", "marketing", "finance",
                 "economics", "management", "leadership", "startup"],
}

# Career goal alignment
CAREER_ALIGNMENT_MAP = {
    "software engineer": ["tech"],
    "software developer": ["tech"],
    "data scientist": ["tech"],
    "ai researcher": ["tech"],
    "web developer": ["tech"],
    "app developer": ["tech"],
    "cyber security": ["tech"],
    "machine learning engineer": ["tech"],
    "doctor": ["medical"],
    "surgeon": ["medical"],
    "dentist": ["medical"],
    "pharmacist": ["medical"],
    "researcher": ["tech", "medical", "electronics"],
    "professor": ["tech", "core", "electronics", "medical"],
    "entrepreneur": ["tech", "business"],
    "business": ["business", "tech"],
    "mba": ["business"],
    "civil servant": ["core", "tech"],
    "government job": ["core", "electronics", "tech"],
    "scientist": ["electronics", "tech", "medical"],
    "engineer": ["core", "electronics"],
    "automobile engineer": ["core"],
    "mechanical engineer": ["core"],
    "electrical engineer": ["electronics"],
    "electronics engineer": ["electronics"],
    "architect": ["core"],
    "startup founder": ["tech", "business"],
}

# Placement demand multipliers
PLACEMENT_DEMAND = {
    "tech": {"demand": 0.95, "avg_salary_lpa": 8.0, "growth": "Very High"},
    "electronics": {"demand": 0.72, "avg_salary_lpa": 5.5, "growth": "High"},
    "core": {"demand": 0.48, "avg_salary_lpa": 4.0, "growth": "Moderate"},
    "medical": {"demand": 0.80, "avg_salary_lpa": 6.5, "growth": "High"},
    "business": {"demand": 0.65, "avg_salary_lpa": 5.0, "growth": "Moderate"},
}

# Salary expectation by tier and branch family (LPA)
SALARY_MAP = {
    1: {"tech": 12.0, "electronics": 8.0, "core": 6.0, "medical": 9.0, "business": 7.0},
    2: {"tech": 7.0, "electronics": 5.0, "core": 4.0, "medical": 7.0, "business": 5.0},
    3: {"tech": 4.0, "electronics": 3.5, "core": 2.5, "medical": 5.0, "business": 3.5},
}

# Fee structure estimates by tier (INR/year)
FEE_ESTIMATES = {
    1: {"govt": 50000, "private": 200000},
    2: {"govt": 70000, "private": 150000},
    3: {"govt": 80000, "private": 120000},
}


def get_branch_family(branch: str) -> str:
    """Classify a branch string into its family."""
    branch_lower = branch.lower().strip()
    for family, keywords in BRANCH_FAMILIES.items():
        if any(kw in branch_lower for kw in keywords):
            return family
    return "other"


def _normalize_list(val) -> List[str]:
    """Normalize input that could be a string or list."""
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return []


# ============================================================================
# 1. BRANCH COMPATIBILITY ENGINE (0-100)
# ============================================================================
def calculate_branch_compatibility(skills: List[str], interests: List[str],
                                    branch: str) -> Tuple[float, str, list]:
    """
    Calculate how well a branch fits the student's skills and interests.
    Returns: (score, reasoning, mismatches)
    """
    family = get_branch_family(branch)
    all_inputs = [s.lower() for s in skills + interests]
    mismatches = []

    if family == "other":
        return 50.0, "Could not determine branch family for detailed analysis.", []

    # Positive alignment
    alignment_keywords = INTEREST_ALIGNMENT.get(family, [])
    match_count = sum(1 for inp in all_inputs
                      if any(kw in inp for kw in alignment_keywords))

    # Cross-family mismatch detection
    for other_family, other_kws in INTEREST_ALIGNMENT.items():
        if other_family == family:
            continue
        cross_matches = sum(1 for inp in all_inputs
                            if any(kw in inp for kw in other_kws))
        if cross_matches >= 2 and match_count < 2:
            family_display = other_family.capitalize()
            mismatches.append(
                f"Your interests align more with {family_display} "
                f"({cross_matches} matches) than {family.capitalize()} "
                f"({match_count} matches)."
            )

    # Score calculation
    base_score = 40.0
    score = base_score + (match_count * 12)

    # Penalty for mismatches
    if mismatches:
        score -= 15

    # Bonus for strong alignment
    if match_count >= 4:
        score += 10

    score = max(0.0, min(100.0, score))

    # Generate reasoning
    if score >= 80:
        reasoning = (f"Excellent fit! Your interests and skills strongly align "
                     f"with {branch}. {match_count} key matches detected.")
    elif score >= 60:
        reasoning = (f"Good fit. Your profile shows moderate alignment with "
                     f"{branch}. Consider exploring this branch further.")
    elif score >= 40:
        reasoning = (f"Average fit. Some of your interests align with "
                     f"{branch}, but there are notable gaps.")
    else:
        reasoning = (f"⚠️ Weak fit. Your interests don't strongly match "
                     f"{branch}. This could lead to academic struggle "
                     f"and career dissatisfaction.")

    return score, reasoning, mismatches


# ============================================================================
# 2. ACADEMIC RISK ANALYSIS (Low/Medium/High + score 0-100)
# ============================================================================
def calculate_academic_risk(rank: int, marks: float, branch: str,
                            interests: List[str]) -> Tuple[str, float, str]:
    """
    Detect academic mismatches and performance risks.
    Returns: (level, score, reason)
    """
    family = get_branch_family(branch)
    risk_score = 30.0  # Base risk
    reasons = []

    # Rank-based risk
    if rank > 100000:
        risk_score += 25
        reasons.append("Very high rank limits tier-1/2 college options")
    elif rank > 60000:
        risk_score += 15
        reasons.append("Competitive rank may restrict top college choices")
    elif rank <= 10000:
        risk_score -= 15
        reasons.append("Strong rank opens many premium options")

    # Marks-based risk
    if marks < 50:
        risk_score += 25
        reasons.append(f"Low academic marks ({marks}%) indicate potential academic struggle")
    elif marks < 65:
        risk_score += 15
        reasons.append(f"Below-average marks ({marks}%) — may face difficulty in rigorous programs")
    elif marks > 85:
        risk_score -= 10
        reasons.append(f"Strong academic record ({marks}%) supports success")

    # Interest-branch mismatch detection
    interests_lower = [i.lower() for i in interests]

    # Student interested in Biology but choosing CSE
    bio_interest = any(kw in i for i in interests_lower
                       for kw in ["biology", "medicine", "healthcare", "anatomy"])
    if bio_interest and family == "tech":
        risk_score += 20
        reasons.append(
            "⚠️ You have Biology/Medicine interests but chose a Tech branch. "
            "This mismatch often leads to academic struggle with discrete math "
            "and programming fundamentals."
        )

    # Student interested in Coding but choosing Civil
    coding_interest = any(kw in i for i in interests_lower
                          for kw in ["coding", "programming", "software", "ai"])
    if coding_interest and family == "core":
        risk_score += 20
        reasons.append(
            "⚠️ You have strong Coding/Software interests but chose a Core "
            "Engineering branch. This mismatch may lead to frustration and "
            "career regret."
        )

    # Student weak in Math choosing CSE/AIML
    weak_math = any(kw in i for i in interests_lower
                    for kw in ["weak in math", "hate math", "poor mathematics"])
    if weak_math and family == "tech":
        risk_score += 25
        reasons.append(
            "⚠️ Critical: Tech branches require strong mathematical skills. "
            "Weak math foundation will cause severe academic difficulties."
        )

    risk_score = max(0.0, min(100.0, risk_score))

    if risk_score > 65:
        level = "High"
    elif risk_score > 35:
        level = "Medium"
    else:
        level = "Low"

    reason = " | ".join(reasons) if reasons else "Academic profile appears aligned with chosen branch."
    return level, risk_score, reason


# ============================================================================
# 3. FINANCIAL RISK ANALYSIS (Low/Medium/High + score 0-100)
# ============================================================================
def calculate_financial_risk(income_lakhs: float, fees: int, hostel_fees: int,
                              loan_required: bool, has_scholarship: bool,
                              budget: float = None) -> Tuple[str, float, str, dict]:
    """
    Analyze affordability and financial burden.
    Returns: (level, score, reason, details)
    """
    total_annual_cost = fees + hostel_fees
    total_4yr_cost = total_annual_cost * 4
    annual_income = income_lakhs * 100000

    risk_score = 20.0  # Base
    reasons = []
    details = {
        "annual_cost": total_annual_cost,
        "total_4yr_cost": total_4yr_cost,
        "annual_income": annual_income,
        "cost_to_income_ratio": round(total_annual_cost / max(annual_income, 1), 2),
    }

    # Affordability ratio
    ratio = total_annual_cost / max(annual_income, 1)
    if ratio > 0.6:
        risk_score += 40
        reasons.append(
            f"Education costs consume {ratio*100:.0f}% of annual income — "
            f"extremely high financial burden"
        )
    elif ratio > 0.4:
        risk_score += 25
        reasons.append(
            f"Education costs consume {ratio*100:.0f}% of annual income — "
            f"significant financial pressure"
        )
    elif ratio > 0.25:
        risk_score += 12
        reasons.append(
            f"Education costs at {ratio*100:.0f}% of income — manageable "
            f"but budget carefully"
        )
    else:
        reasons.append("Education costs are within comfortable affordability range")

    # Loan risk
    if loan_required:
        risk_score += 15
        reasons.append("Education loan adds future EMI pressure on student/family")

    # Scholarship benefit
    if has_scholarship:
        risk_score -= 20
        reasons.append("✅ Scholarship reduces financial burden significantly")

    # Budget constraint
    if budget and total_annual_cost > budget * 100000:
        risk_score += 15
        reasons.append(
            f"Annual cost (₹{total_annual_cost:,}) exceeds stated budget "
            f"(₹{budget*100000:,.0f})"
        )

    # Low income alert
    if income_lakhs < 2.5:
        risk_score += 15
        reasons.append(
            "Low income bracket — ensure government fee concessions "
            "(SNQ/SC-ST/Category-1) are applied"
        )

    risk_score = max(0.0, min(100.0, risk_score))

    if risk_score > 65:
        level = "High"
    elif risk_score > 35:
        level = "Medium"
    else:
        level = "Low"

    reason = " | ".join(reasons)
    return level, risk_score, reason, details


# ============================================================================
# 4. PLACEMENT RISK ANALYSIS (Low/Medium/High + score 0-100)
# ============================================================================
def calculate_placement_risk(branch: str, college_tier: int,
                              career_goals: str) -> Tuple[str, float, str, dict]:
    """
    Analyze employability based on branch demand, tier, and career alignment.
    Returns: (level, score, reason, details)
    """
    family = get_branch_family(branch)
    demand_data = PLACEMENT_DEMAND.get(family, {"demand": 0.5, "avg_salary_lpa": 3.5, "growth": "Low"})

    risk_score = 30.0
    reasons = []

    # Branch demand
    demand = demand_data["demand"]
    if demand < 0.5:
        risk_score += 25
        reasons.append(f"{branch} has lower industry demand ({demand*100:.0f}%)")
    elif demand > 0.8:
        risk_score -= 15
        reasons.append(f"{branch} has strong industry demand ({demand*100:.0f}%)")

    # Tier impact
    if college_tier == 1:
        risk_score -= 20
        reasons.append("Tier-1 colleges have excellent placement records")
    elif college_tier == 3:
        risk_score += 20
        reasons.append("Tier-3 colleges may have limited placement opportunities")

    # Salary expectations
    salary = SALARY_MAP.get(college_tier, SALARY_MAP[3]).get(family, 3.0)

    # Career alignment check
    goals_lower = career_goals.lower().strip()
    goal_families = []
    for goal_key, families in CAREER_ALIGNMENT_MAP.items():
        if goal_key in goals_lower:
            goal_families.extend(families)

    if goal_families and family not in goal_families:
        risk_score += 15
        reasons.append(
            f"Your career goal '{career_goals}' may not directly align "
            f"with {branch} placements"
        )

    risk_score = max(0.0, min(100.0, risk_score))

    if risk_score > 65:
        level = "High"
    elif risk_score > 35:
        level = "Medium"
    else:
        level = "Low"

    details = {
        "expected_salary_lpa": salary,
        "demand_percent": demand * 100,
        "growth_trend": demand_data["growth"],
        "salary_range": f"₹{salary*0.6:.1f}L - ₹{salary*1.8:.1f}L",
    }

    reason = " | ".join(reasons) if reasons else "Branch has solid placement outlook."
    return level, risk_score, reason, details


# ============================================================================
# 5. CAREER ALIGNMENT SCORE (0-100)
# ============================================================================
def calculate_career_alignment(branch: str, career_goals: str,
                                interests: List[str]) -> Tuple[float, str]:
    """
    How well does the chosen branch lead to the student's career goals?
    Returns: (score, explanation)
    """
    family = get_branch_family(branch)
    goals_lower = career_goals.lower().strip()

    score = 50.0  # Base
    explanations = []

    # Direct career-branch mapping
    matched = False
    for goal_key, families in CAREER_ALIGNMENT_MAP.items():
        if goal_key in goals_lower and family in families:
            score += 30
            explanations.append(
                f"'{career_goals}' directly aligns with {branch}"
            )
            matched = True
            break

    if not matched and goals_lower:
        # Check partial matches
        for goal_key, families in CAREER_ALIGNMENT_MAP.items():
            if goal_key in goals_lower:
                if family not in families:
                    score -= 10
                    suggested = ", ".join(f.capitalize() for f in families[:2])
                    explanations.append(
                        f"'{career_goals}' typically suits {suggested} branches"
                    )
                break

    # Interest reinforcement
    interest_family = None
    for fam, keywords in INTEREST_ALIGNMENT.items():
        match_count = sum(1 for i in interests
                          if any(kw in i.lower() for kw in keywords))
        if match_count >= 2:
            interest_family = fam
            break

    if interest_family and interest_family == family:
        score += 15
        explanations.append("Your interests reinforce your career-branch choice")
    elif interest_family and interest_family != family:
        score -= 10
        explanations.append(
            f"Your interests lean toward {interest_family.capitalize()}, "
            f"creating a potential career friction"
        )

    score = max(0.0, min(100.0, score))
    explanation = " | ".join(explanations) if explanations else "Moderate career alignment."
    return score, explanation


# ============================================================================
# 6. SCHOLARSHIP OPPORTUNITY SCORE (0-100)
# ============================================================================
def calculate_scholarship_opportunity(category: str, income_lakhs: float,
                                       gender: str, rank: int,
                                       marks: float) -> Tuple[float, str, list]:
    """
    Estimate scholarship eligibility and opportunity.
    Returns: (score, reasoning, eligible_schemes)
    """
    score = 20.0  # Base
    schemes = []
    reasons = []

    # Category-based schemes
    category_upper = category.upper()
    if category_upper in ["SC", "ST"]:
        score += 30
        schemes.append("Post-Matric Scholarship for SC/ST Students")
        schemes.append("Dr. Ambedkar Foundation Scholarship")
        reasons.append("SC/ST category qualifies for multiple government scholarships")
    elif category_upper in ["OBC", "CAT1", "CAT-1", "CATEGORY-1"]:
        score += 20
        schemes.append("OBC Pre-Matric & Post-Matric Scholarship")
        reasons.append("OBC/Category-1 eligible for state and central scholarships")

    # Income-based schemes
    if income_lakhs <= 2.5:
        score += 25
        schemes.append("Vidyasiri Scholarship (income < 2.5L)")
        schemes.append("Central Sector Scholarship")
        reasons.append("Low income bracket qualifies for need-based scholarships")
    elif income_lakhs <= 6.0:
        score += 15
        schemes.append("Fee Concession Scheme")
        reasons.append("Middle-income eligible for partial fee concessions")

    # Merit-based
    if rank <= 5000:
        score += 15
        schemes.append("KEA Merit Scholarship (Top 5000)")
        reasons.append("Excellent rank qualifies for merit scholarships")
    elif rank <= 20000:
        score += 8
        schemes.append("Institutional Merit Award")
        reasons.append("Good rank may qualify for college-level merit awards")

    # Marks-based
    if marks >= 90:
        score += 10
        schemes.append("Academic Excellence Scholarship")
        reasons.append("Outstanding marks qualify for academic excellence awards")

    # Gender-based
    if gender and gender.lower() == "female":
        score += 10
        schemes.append("Pragati Scholarship (Female Engineering Students)")
        reasons.append("Female students eligible for Pragati and similar schemes")

    score = max(0.0, min(100.0, score))
    reasoning = " | ".join(reasons) if reasons else "Standard scholarship eligibility."
    return score, reasoning, schemes


# ============================================================================
# 7. COLLEGE ROI ENGINE (0-100)
# ============================================================================
def calculate_roi(branch: str, college_tier: int, total_cost: int,
                  has_scholarship: bool) -> Tuple[float, str, dict]:
    """
    Calculate Return on Investment for the education choice.
    ROI = Expected Salary / Total Educational Cost
    Returns: (score, label, details)
    """
    family = get_branch_family(branch)
    expected_salary = SALARY_MAP.get(college_tier, SALARY_MAP[3]).get(family, 3.0)
    expected_salary_inr = expected_salary * 100000  # Convert LPA to INR

    # Adjust cost if scholarship
    effective_cost = total_cost * 0.6 if has_scholarship else total_cost

    # ROI ratio
    roi_ratio = expected_salary_inr / max(effective_cost, 1)

    # 5-year cumulative
    five_year_earnings = expected_salary_inr * 5 * 1.08  # 8% annual growth
    net_value = five_year_earnings - effective_cost

    # Score: 3x+ ROI = 100, 1x = 50, <0.5x = 15
    roi_score = min(100.0, max(10.0, roi_ratio * 35))

    if roi_ratio > 2.5:
        label = "Excellent ROI"
    elif roi_ratio > 1.5:
        label = "High ROI"
    elif roi_ratio > 1.0:
        label = "Medium ROI"
    else:
        label = "Low ROI"

    details = {
        "roi_ratio": round(roi_ratio, 2),
        "expected_salary_lpa": expected_salary,
        "total_education_cost": effective_cost,
        "five_year_net_value": round(net_value),
        "breakeven_months": round((effective_cost / (expected_salary_inr / 12)), 1)
            if expected_salary_inr > 0 else 999,
    }

    return roi_score, label, details


# ============================================================================
# 8. STUDENT REGRET PREDICTOR (0-100%)
# ============================================================================
def predict_regret(academic_risk_score: float, financial_risk_score: float,
                   branch_compat_score: float, career_alignment_score: float,
                   placement_risk_score: float) -> Tuple[float, List[str]]:
    """
    Predict probability that the student may regret this decision.
    Uses Bayesian-style weighted heuristic.
    Returns: (regret_probability, reasons)
    """
    reasons = []

    # Weighted regret components
    regret = 5.0  # Base minimum

    # Branch mismatch is the #1 regret driver
    branch_mismatch_factor = (100 - branch_compat_score) * 0.35
    regret += branch_mismatch_factor
    if branch_compat_score < 40:
        reasons.append("Branch mismatch with interests (high regret driver)")

    # Financial burden
    financial_factor = financial_risk_score * 0.25
    regret += financial_factor
    if financial_risk_score > 60:
        reasons.append("High financial burden creates long-term stress")

    # Career misalignment
    career_factor = (100 - career_alignment_score) * 0.15
    regret += career_factor
    if career_alignment_score < 40:
        reasons.append("Career goals don't align with chosen branch")

    # Academic risk
    academic_factor = academic_risk_score * 0.15
    regret += academic_factor
    if academic_risk_score > 60:
        reasons.append("Academic risk may lead to performance anxiety")

    # Placement uncertainty
    placement_factor = placement_risk_score * 0.10
    regret += placement_factor
    if placement_risk_score > 60:
        reasons.append("Weak placement prospects may cause future dissatisfaction")

    regret = max(0.0, min(100.0, regret))

    if not reasons:
        reasons.append("Low regret probability — your choices are well-aligned")

    return regret, reasons


# ============================================================================
# 9. SUCCESS SCORE ENGINE (0-100)
# ============================================================================
def calculate_success_score(
    rank_match: float,
    branch_compat: float,
    career_alignment: float,
    financial_fit: float,
    placement_potential: float,
    scholarship_opportunity: float,
    location_score: float
) -> float:
    """
    Weighted composite success score.
    25% Rank Match + 20% Branch Compatibility + 15% Career Alignment +
    15% Financial Fit + 10% Placement Potential + 10% Scholarship + 5% Location
    """
    score = (
        rank_match * 0.25 +
        branch_compat * 0.20 +
        career_alignment * 0.15 +
        financial_fit * 0.15 +
        placement_potential * 0.10 +
        scholarship_opportunity * 0.10 +
        location_score * 0.05
    )
    return max(0.0, min(100.0, score))


# ============================================================================
# 10. COUNSELING RISK SCORE (0-100)
# ============================================================================
def calculate_counseling_risk(academic_risk_score: float,
                               financial_risk_score: float,
                               placement_risk_score: float,
                               regret_probability: float) -> float:
    """Aggregate counseling risk — how risky is this admission choice overall?"""
    score = (
        academic_risk_score * 0.30 +
        financial_risk_score * 0.30 +
        placement_risk_score * 0.20 +
        regret_probability * 0.20
    )
    return max(0.0, min(100.0, score))


# ============================================================================
# 11. RANK MATCH SCORE (0-100)
# ============================================================================
def calculate_rank_match(rank: int, branch: str, category: str) -> float:
    """Estimate how competitive the rank is for the branch."""
    family = get_branch_family(branch)

    # Approximate cutoff ranges for Karnataka KCET
    cutoff_ranges = {
        "tech": {"GM": 30000, "OBC": 45000, "SC": 80000, "ST": 100000},
        "electronics": {"GM": 50000, "OBC": 65000, "SC": 100000, "ST": 120000},
        "core": {"GM": 80000, "OBC": 100000, "SC": 130000, "ST": 150000},
        "medical": {"GM": 20000, "OBC": 35000, "SC": 60000, "ST": 80000},
        "business": {"GM": 60000, "OBC": 80000, "SC": 110000, "ST": 130000},
    }

    cat = category.upper()
    if cat in ["SC/ST", "SC", "ST"]:
        cat_key = cat if cat in ["SC", "ST"] else "SC"
    elif cat in ["OBC", "CAT1", "CAT-1", "2A", "2B", "3A", "3B"]:
        cat_key = "OBC"
    else:
        cat_key = "GM"

    range_map = cutoff_ranges.get(family, cutoff_ranges["core"])
    max_cutoff = range_map.get(cat_key, 80000)

    if rank <= max_cutoff * 0.3:
        return 95.0  # Very strong match
    elif rank <= max_cutoff * 0.6:
        return 80.0
    elif rank <= max_cutoff:
        return 60.0
    elif rank <= max_cutoff * 1.3:
        return 40.0
    else:
        return 20.0


# ============================================================================
# 12. LOCATION PREFERENCE SCORE (0-100)
# ============================================================================
def calculate_location_score(home_location: str, preferred_colleges: List[str]) -> float:
    """Simple location preference heuristic."""
    if not home_location:
        return 75.0  # No strong preference
    home = home_location.lower()
    if any("bangalore" in c.lower() or "bengaluru" in c.lower()
           for c in preferred_colleges):
        if "bangalore" in home or "bengaluru" in home:
            return 95.0
        return 70.0
    return 75.0  # Neutral


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================
def analyze_risk(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete risk analysis pipeline.

    profile expects:
    {
        "rank": int,
        "category": str (GM, OBC, SC, ST),
        "gender": str (Male, Female),
        "income": float (in lakhs or INR — auto-detected),
        "home_location": str,
        "preferred_colleges": list[str],
        "branch": str,
        "marks": float (PUC/entrance percentage),
        "entrance_marks": float,
        "interests": list[str] or comma-separated str,
        "skills": list[str] or comma-separated str,
        "career_goals": str,
        "budget": float (in lakhs),
        "has_scholarship": bool,
        "loan_required": bool,
        "hostel_required": bool,
        "college_tier": int (1,2,3),
        "fees": int (annual),
        "hostel_fees": int (annual),
    }
    """
    # --- Extract and normalize inputs ---
    rank = int(profile.get("rank", 50000))
    category = profile.get("category", "GM")
    gender = profile.get("gender", "")
    income_raw = float(profile.get("income", 5.0))
    # Auto-detect: if income > 100, it's in INR not lakhs
    income_lakhs = income_raw / 100000 if income_raw > 100 else income_raw

    home_location = profile.get("home_location", "")
    preferred_colleges = _normalize_list(profile.get("preferred_colleges", []))
    branch = profile.get("branch", "CSE")
    marks = float(profile.get("marks", 70.0))
    entrance_marks = float(profile.get("entrance_marks", marks))
    interests = _normalize_list(profile.get("interests", []))
    skills = _normalize_list(profile.get("skills", []))
    career_goals = profile.get("career_goals", "")
    budget = float(profile.get("budget", 0)) if profile.get("budget") else None
    has_scholarship = bool(profile.get("has_scholarship", False))
    loan_required = bool(profile.get("loan_required", False))
    hostel_required = bool(profile.get("hostel_required", False))
    college_tier = int(profile.get("college_tier", 2))
    fees = int(profile.get("fees", 100000))
    hostel_fees = int(profile.get("hostel_fees", 50000)) if hostel_required else 0

    # --- Run all engines ---

    # 1. Branch Compatibility
    branch_compat_score, branch_reasoning, branch_mismatches = \
        calculate_branch_compatibility(skills, interests, branch)

    # 2. Academic Risk
    acad_level, acad_score, acad_reason = \
        calculate_academic_risk(rank, marks, branch, interests)

    # 3. Financial Risk
    fin_level, fin_score, fin_reason, fin_details = \
        calculate_financial_risk(income_lakhs, fees, hostel_fees,
                                 loan_required, has_scholarship, budget)

    # 4. Placement Risk
    place_level, place_score, place_reason, place_details = \
        calculate_placement_risk(branch, college_tier, career_goals)

    # 5. Career Alignment
    career_score, career_explanation = \
        calculate_career_alignment(branch, career_goals, interests)

    # 6. Scholarship Opportunity
    scholarship_score, scholarship_reason, eligible_schemes = \
        calculate_scholarship_opportunity(category, income_lakhs, gender,
                                           rank, marks)

    # 7. College ROI
    total_cost = (fees + hostel_fees) * 4  # 4-year program
    roi_score, roi_label, roi_details = \
        calculate_roi(branch, college_tier, total_cost, has_scholarship)

    # 8. Rank Match
    rank_match_score = calculate_rank_match(rank, branch, category)

    # 9. Location Score
    location_score = calculate_location_score(home_location, preferred_colleges)

    # 10. Success Score
    financial_fit = 100 - fin_score  # Invert: low risk = high fit
    placement_potential = 100 - place_score
    success_score = calculate_success_score(
        rank_match_score, branch_compat_score, career_score,
        financial_fit, placement_potential, scholarship_score, location_score
    )

    # 11. Regret Probability
    regret_prob, regret_reasons = predict_regret(
        acad_score, fin_score, branch_compat_score,
        career_score, place_score
    )

    # 12. Counseling Risk Score
    counseling_risk = calculate_counseling_risk(
        acad_score, fin_score, place_score, regret_prob
    )

    # --- Compile Final Report ---
    return {
        "success_score": round(success_score, 1),
        "counseling_risk_score": round(counseling_risk, 1),

        "academic_risk": acad_level,
        "academic_risk_score": round(acad_score, 1),
        "academic_risk_reason": acad_reason,

        "financial_risk": fin_level,
        "financial_risk_score": round(fin_score, 1),
        "financial_risk_reason": fin_reason,
        "financial_details": fin_details,

        "placement_risk": place_level,
        "placement_risk_score": round(place_score, 1),
        "placement_risk_reason": place_reason,
        "placement_details": place_details,

        "career_alignment_score": round(career_score, 1),
        "career_alignment_reason": career_explanation,

        "branch_compatibility_score": round(branch_compat_score, 1),
        "branch_compatibility_reason": branch_reasoning,
        "branch_mismatches": branch_mismatches,

        "scholarship_opportunity_score": round(scholarship_score, 1),
        "scholarship_reason": scholarship_reason,
        "eligible_scholarships": eligible_schemes,

        "college_roi_score": round(roi_score, 1),
        "roi_label": roi_label,
        "roi_details": roi_details,

        "rank_match_score": round(rank_match_score, 1),
        "regret_probability": round(regret_prob, 1),
        "regret_reasons": regret_reasons,
    }


# ============================================================================
# AI EXPLANATION GENERATOR
# ============================================================================
def generate_ai_explanation(profile: Dict[str, Any],
                             risk_data: Dict[str, Any]) -> str:
    """
    Generate a human-like AI counselor explanation.
    Falls back to rule-based if LLM is unavailable.
    """
    # Try LLM-based explanation first
    try:
        from llm_service import get_llm_service
        llm = get_llm_service()

        prompt = f"""You are the InsightRural AI Admission Counselor — an experienced, caring mentor.
Analyze this student's risk profile and give a clear, human-like counseling response.

Student Profile:
- Target Branch: {profile.get('branch')}
- Rank: {profile.get('rank')}
- Category: {profile.get('category', 'GM')}
- Family Income: ₹{float(profile.get('income', 5))} Lakhs/year
- Interests: {', '.join(profile.get('interests', []) if isinstance(profile.get('interests'), list) else [profile.get('interests', '')])}
- Skills: {', '.join(profile.get('skills', []) if isinstance(profile.get('skills'), list) else [profile.get('skills', '')])}
- Career Goals: {profile.get('career_goals', 'Not specified')}

Analysis Results:
- Success Score: {risk_data['success_score']}/100
- Regret Probability: {risk_data['regret_probability']}%
- Branch Compatibility: {risk_data['branch_compatibility_score']}/100
- Career Alignment: {risk_data['career_alignment_score']}/100
- Academic Risk: {risk_data['academic_risk']} ({risk_data['academic_risk_reason']})
- Financial Risk: {risk_data['financial_risk']} ({risk_data['financial_risk_reason']})
- Placement Risk: {risk_data['placement_risk']}
- College ROI: {risk_data['roi_label']} ({risk_data['college_roi_score']}/100)
- Scholarship Score: {risk_data['scholarship_opportunity_score']}/100

Rules:
1. Address the student directly and compassionately
2. Explain the Success Score meaning
3. Highlight risks and strengths
4. Give a clear final recommendation
5. If regret > 40%, strongly suggest alternatives
6. Keep it under 200 words
7. Don't use markdown formatting"""

        system_prompt = (
            "You are an Elite AI Career Counselor specializing in Indian "
            "engineering admissions. Be encouraging but realistic. "
            "Speak simply and directly."
        )
        response = llm.generate(prompt=prompt, system_prompt=system_prompt,
                                 max_tokens=300)
        return response
    except Exception:
        pass

    # Fallback: rule-based explanation
    ss = risk_data["success_score"]
    rp = risk_data["regret_probability"]
    branch = profile.get("branch", "your chosen branch")
    bc = risk_data["branch_compatibility_score"]
    ca = risk_data["career_alignment_score"]
    fr = risk_data["financial_risk"]
    ar = risk_data["academic_risk"]
    roi = risk_data["roi_label"]

    explanation = f"Your Student Success Score is {ss}/100. "

    if ss >= 75:
        explanation += f"This is an excellent score, indicating strong alignment between your profile and {branch}. "
    elif ss >= 55:
        explanation += f"This is a decent score, but there are areas where your fit with {branch} could be improved. "
    else:
        explanation += f"This score suggests significant mismatches that could affect your academic journey in {branch}. "

    explanation += f"Your Branch Compatibility is {bc}%, and Career Alignment is {ca}%. "

    if bc < 50:
        explanation += f"⚠️ Your interests don't strongly match {branch}. Consider exploring branches that better align with your passions. "

    if fr == "High":
        explanation += "Your financial risk is high — explore scholarship options and fee concessions to reduce burden. "
    elif fr == "Low":
        explanation += "Financially, this choice appears sustainable for your family. "

    if ar == "High":
        explanation += "Academic risk is elevated — ensure you're prepared for the coursework demands. "

    explanation += f"Your Regret Probability is {rp}%. "

    if rp > 40:
        explanation += "This is concerning — students with similar profiles often express regret. Consider reviewing your branch selection carefully. "
    elif rp < 20:
        explanation += "This is very low, indicating your choices are well-aligned with your goals. "

    explanation += f"College ROI is rated '{roi}'. "
    explanation += "Based on this analysis, I recommend reviewing all risk factors before finalizing your admission choice."

    return explanation
