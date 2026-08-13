"""
Scholarship Engine — Pure deterministic logic.
No LLM. No AI. Rules from official Karnataka/Central govt schemes.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ScholarshipResult:
    name: str
    authority: str                  # "State Government" / "Central Government" / "Private"
    amount: str                     # Human-readable amount
    amount_inr: Optional[int]       # Annual amount in ₹ (None if variable)
    eligibility_met: bool
    eligibility_reasons: List[str]  # Why eligible
    ineligibility_reasons: List[str]  # Why NOT eligible
    application_portal: str
    official_url: str
    coverage: str                   # "Full tuition" / "Partial" / "Stipend"
    deadlines: str
    required_documents: List[str]


class ScholarshipEngine:
    """
    Deterministic scholarship eligibility engine.
    All decisions are rule-based. Zero LLM involvement.
    
    Sources:
    - Karnataka Post-Matric Scholarship: karepass.cgg.gov.in / ssp.postmatric.karnataka.gov.in
    - NSP: scholarships.gov.in
    - KEA Fee Waivers: cetonline.karnataka.gov.in
    - Vidya Samuddi: vidyasamuddi.kar.nic.in
    - PMSS: sarkarinaukriprep.com / desw.gov.in (ex-servicemen)
    """

    SCHOLARSHIP_RULES = [
        {
            "id": "sch_sc_st_fee_waiver",
            "name": "SC/ST Fee Waiver — Karnataka Government",
            "authority": "State Government",
            "coverage": "Full tuition + development fees",
            "amount": "100% Fee Waiver (Government & Aided colleges)",
            "amount_inr": None,
            "portal": "cetonline.karnataka.gov.in",
            "url": "https://cetonline.karnataka.gov.in",
            "deadlines": "Applied automatically at time of KEA counselling",
            "documents": [
                "SC/ST Caste Certificate (original)",
                "Income Certificate",
                "Aadhar Card",
                "Bank Account details",
                "KCET Admit Card"
            ],
            "conditions": {
                "categories": ["SC", "ST"],
                "college_types": ["Government", "Government_Aided"],
                "income_limit": None,  # No income limit for fee waiver
            }
        },
        {
            "id": "sch_postmatric_obc",
            "name": "Post-Matric Scholarship — OBC/2A/2B/3A/3B",
            "authority": "State Government",
            "coverage": "Partial tuition fee reimbursement",
            "amount": "₹23,590/year (Government colleges) | ₹36,300/year (Aided) | ₹74,890/year (Type-1 Private)",
            "amount_inr": 74890,
            "portal": "ssp.postmatric.karnataka.gov.in",
            "url": "https://ssp.postmatric.karnataka.gov.in",
            "deadlines": "September - November each academic year",
            "documents": [
                "Caste Certificate (OBC/2A/2B/3A/3B)",
                "Income Certificate (below ₹2.5 lakh/year)",
                "Previous year marks card",
                "Aadhar Card",
                "Bank passbook copy"
            ],
            "conditions": {
                "categories": ["OBC", "2A", "2B", "3A", "3B", "CAT1"],
                "income_limit": 250000,
            }
        },
        {
            "id": "sch_cat1_brahmin",
            "name": "Category-1 (Brahmin/Other) Fee Concession",
            "authority": "State Government",
            "coverage": "Partial fee concession at Government colleges",
            "amount": "₹23,590/year at Government & Aided colleges",
            "amount_inr": 23590,
            "portal": "cetonline.karnataka.gov.in",
            "url": "https://cetonline.karnataka.gov.in",
            "deadlines": "During KEA counselling process",
            "documents": [
                "Category-1 Certificate",
                "Income Certificate (below ₹2.5 lakh/year)",
                "Aadhar Card"
            ],
            "conditions": {
                "categories": ["CAT1"],
                "income_limit": 250000,
            }
        },
        {
            "id": "sch_nsp_central_obc",
            "name": "NSP — Central OBC Post-Matric Scholarship",
            "authority": "Central Government",
            "coverage": "Maintenance allowance + tuition fee",
            "amount": "₹3,000 - ₹10,000/year maintenance + tuition fees",
            "amount_inr": 10000,
            "portal": "scholarships.gov.in",
            "url": "https://scholarships.gov.in",
            "deadlines": "October - November each year (NSP portal)",
            "documents": [
                "OBC-NCL Certificate",
                "Income Certificate (below ₹1 lakh/year)",
                "Previous year marks card",
                "Aadhar-linked bank account",
                "Admission receipt"
            ],
            "conditions": {
                "categories": ["OBC", "2A", "2B", "3A", "3B"],
                "income_limit": 100000,
            }
        },
        {
            "id": "sch_nsp_sc_st_central",
            "name": "NSP — Central SC/ST Post-Matric Scholarship",
            "authority": "Central Government",
            "coverage": "Full tuition + maintenance allowance",
            "amount": "Full tuition fee + ₹3,800 - ₹12,000/year maintenance",
            "amount_inr": None,
            "portal": "scholarships.gov.in",
            "url": "https://scholarships.gov.in",
            "deadlines": "October - November each year",
            "documents": [
                "SC/ST Caste Certificate (verified by Revenue Officer)",
                "Income Certificate",
                "Previous year marks card",
                "Aadhar-linked bank account"
            ],
            "conditions": {
                "categories": ["SC", "ST"],
                "income_limit": 250000,
            }
        },
        {
            "id": "sch_vidya_lakshmi",
            "name": "Vidya Lakshmi — Education Loan Scheme",
            "authority": "Central Government",
            "coverage": "Education loan (not scholarship) up to ₹7.5 lakh without collateral",
            "amount": "Loan: ₹4 lakh - ₹20 lakh at 10.5-12% interest",
            "amount_inr": None,
            "portal": "vidyalakshmi.co.in",
            "url": "https://www.vidyalakshmi.co.in",
            "deadlines": "Apply anytime — loan disbursed before semester fee payment",
            "documents": [
                "Admission letter",
                "Fee structure",
                "Income proof of parents",
                "Aadhar & PAN",
                "2 passport photos"
            ],
            "conditions": {
                "categories": ["GM", "SC", "ST", "OBC", "2A", "2B", "3A", "3B", "CAT1", "EWS"],
                "income_limit": None,  # All students eligible
            }
        },
        {
            "id": "sch_ews_central",
            "name": "PM YASASVI — EWS Scholarship",
            "authority": "Central Government",
            "coverage": "₹75,000/year for professional courses",
            "amount": "₹75,000/year",
            "amount_inr": 75000,
            "portal": "yet.nta.ac.in",
            "url": "https://yet.nta.ac.in",
            "deadlines": "August-September each year",
            "documents": [
                "EWS Certificate",
                "Income Certificate (below ₹8 lakh/year)",
                "SEBC/OBC certificate",
                "Aadhar Card"
            ],
            "conditions": {
                "categories": ["EWS", "OBC", "GM"],
                "income_limit": 800000,
            }
        },
        {
            "id": "sch_pmss_exservicemen",
            "name": "PMSS — Prime Minister's Scholarship (Ex-Servicemen)",
            "authority": "Central Government",
            "coverage": "₹2,500 - ₹3,000/month stipend",
            "amount": "₹30,000 - ₹36,000/year",
            "amount_inr": 36000,
            "portal": "ksb.gov.in",
            "url": "https://ksb.gov.in/pmss.htm",
            "deadlines": "October - November (KSB portal)",
            "documents": [
                "Ex-Serviceman Certificate of parent",
                "Discharge Book copy",
                "Income Certificate",
                "Aadhar Card"
            ],
            "conditions": {
                "categories": ["GM", "SC", "ST", "OBC", "2A", "2B", "3A", "3B"],
                "snq_required": True,  # Parent must be ex-serviceman
                "income_limit": None,
            }
        },
        {
            "id": "sch_vidya_samuddi",
            "name": "Vidya Samuddi — Karnataka Rural Scholarship",
            "authority": "State Government",
            "coverage": "₹10,000 - ₹25,000/year for rural students",
            "amount": "₹10,000 - ₹25,000/year",
            "amount_inr": 25000,
            "portal": "vidyasamuddi.kar.nic.in",
            "url": "http://vidyasamuddi.kar.nic.in",
            "deadlines": "September - October each year",
            "documents": [
                "Rural area study certificate (1st-10th in rural school)",
                "Income Certificate (below ₹2 lakh)",
                "Aadhar Card",
                "KCET Rank Card"
            ],
            "conditions": {
                "categories": ["GM", "SC", "ST", "OBC", "2A", "2B", "3A", "3B", "CAT1"],
                "rural_required": True,
                "income_limit": 200000,
            }
        },
        {
            "id": "sch_hk_371j",
            "name": "371(J) Hyderabad-Karnataka Special Scholarship",
            "authority": "State Government",
            "coverage": "Additional fee concession for HK region students",
            "amount": "Reduced fees at HK-region Government colleges",
            "amount_inr": None,
            "portal": "cetonline.karnataka.gov.in",
            "url": "https://cetonline.karnataka.gov.in",
            "deadlines": "During KEA counselling",
            "documents": [
                "371(J) Domicile Certificate from HK district",
                "Category Certificate (if applicable)",
                "Income Certificate"
            ],
            "conditions": {
                "categories": ["GM", "SC", "ST", "OBC", "2A", "2B", "3A", "3B", "CAT1"],
                "hk_371j_required": True,
            }
        },
    ]

    def check_eligibility(self, profile) -> List[ScholarshipResult]:
        """
        Deterministically check eligibility for all scholarships.
        Returns sorted list with eligible scholarships first.
        """
        results = []

        for rule in self.SCHOLARSHIP_RULES:
            result = self._check_one(rule, profile)
            results.append(result)

        # Sort: eligible first, then by amount
        results.sort(key=lambda r: (not r.eligibility_met, -(r.amount_inr or 0)))
        return results

    def _check_one(self, rule: Dict, profile) -> ScholarshipResult:
        """Check eligibility for a single scholarship."""
        conditions = rule["conditions"]
        eligible_reasons = []
        ineligible_reasons = []

        # ── Category check ──────────────────────────────────────────────────
        allowed_cats = conditions.get("categories", [])
        if profile.category in allowed_cats:
            eligible_reasons.append(f"Category {profile.category} is eligible")
        else:
            ineligible_reasons.append(
                f"Requires category: {', '.join(allowed_cats)} (you are {profile.category})"
            )

        # ── Income check ────────────────────────────────────────────────────
        income_limit = conditions.get("income_limit")
        if income_limit:
            if profile.annual_income is None:
                ineligible_reasons.append(
                    f"Income limit is ₹{income_limit:,}/year — please verify your family income"
                )
            elif profile.annual_income <= income_limit:
                eligible_reasons.append(
                    f"Annual income ₹{profile.annual_income:,} is within ₹{income_limit:,} limit"
                )
            else:
                ineligible_reasons.append(
                    f"Income ₹{profile.annual_income:,} exceeds limit of ₹{income_limit:,}/year"
                )

        # ── Rural quota check ───────────────────────────────────────────────
        if conditions.get("rural_required"):
            if profile.rural_quota:
                eligible_reasons.append("Rural quota student is eligible")
            else:
                ineligible_reasons.append("Requires rural background (1st-10th in rural school)")

        # ── 371(J) check ─────────────────────────────────────────────────────
        if conditions.get("hk_371j_required"):
            if profile.hk_371j:
                eligible_reasons.append("Hyderabad-Karnataka 371(J) student is eligible")
            else:
                ineligible_reasons.append("Requires residence in HK region (Bidar, Gulbarga, Raichur, Koppal, Bellary, Yadgir)")

        # ── SNQ / Ex-serviceman check ────────────────────────────────────────
        if conditions.get("snq_required"):
            if profile.snq:
                eligible_reasons.append("Ex-serviceman parent qualifies for PMSS")
            else:
                ineligible_reasons.append("Parent must be ex-serviceman/woman of armed forces")

        # ── Final eligibility ────────────────────────────────────────────────
        is_eligible = len(ineligible_reasons) == 0

        return ScholarshipResult(
            name=rule["name"],
            authority=rule["authority"],
            amount=rule["amount"],
            amount_inr=rule.get("amount_inr"),
            eligibility_met=is_eligible,
            eligibility_reasons=eligible_reasons,
            ineligibility_reasons=ineligible_reasons,
            application_portal=rule["portal"],
            official_url=rule["url"],
            coverage=rule["coverage"],
            deadlines=rule["deadlines"],
            required_documents=rule["documents"],
        )

    def get_total_benefit(self, results: List[ScholarshipResult]) -> Dict[str, Any]:
        """Calculate total scholarship benefit for eligible schemes."""
        eligible = [r for r in results if r.eligibility_met and r.amount_inr]
        
        # Some scholarships are complementary, some are mutually exclusive
        # Use the highest single scholarship as primary estimate
        if eligible:
            best = max(eligible, key=lambda r: r.amount_inr or 0)
            total_estimate = sum(
                r.amount_inr for r in eligible
                if r.amount_inr and r.authority != best.authority  # Add schemes from different authorities
            ) + (best.amount_inr or 0)
        else:
            total_estimate = 0

        return {
            "eligible_count": len([r for r in results if r.eligibility_met]),
            "total_eligible": len(results),
            "estimated_annual_benefit_inr": total_estimate,
            "primary_recommendation": eligible[0].name if eligible else None,
            "note": "Some schemes may not be combinable. Apply for all eligible schemes and use the best one."
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
_engine: Optional[ScholarshipEngine] = None


def get_scholarship_engine() -> ScholarshipEngine:
    global _engine
    if _engine is None:
        _engine = ScholarshipEngine()
    return _engine
