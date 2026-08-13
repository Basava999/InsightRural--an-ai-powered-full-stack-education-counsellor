# ==============================================================================
# InsightRural — JSON-First Data Lookup Service
# ==============================================================================
# PRIORITY 1 in the data hierarchy. This service loads all structured JSON
# databases at startup and provides instant, exact lookups for:
#   - College cutoffs (multi-year, by branch + category)
#   - Fee structures (by college type + student category)
#   - Hostel information (fees, amenities, eligibility)
#   - Scholarships (eligibility, amounts, deadlines)
#   - Education loans (rates, limits, collateral)
#   - Counseling process (steps, documents)
#
# The LLM pipeline uses this BEFORE ChromaDB, ensuring zero hallucination
# on factual data points.
# ==============================================================================

import json
import os
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JSONDataService")

# ── Data directory ────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def _load_json(filename: str) -> Any:
    """Load a JSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"[JSON] Loaded {filename} ({len(data) if isinstance(data, list) else 'object'} records)")
        return data
    except FileNotFoundError:
        logger.warning(f"[JSON] File not found: {filepath}")
        return [] if filename != "counseling_guide.json" else {}
    except json.JSONDecodeError as e:
        logger.error(f"[JSON] Parse error in {filename}: {e}")
        return [] if filename != "counseling_guide.json" else {}


class JSONDataService:
    """
    Priority-1 data source for the KCET College Advisor.
    
    Loads all structured JSON databases at init and provides
    typed lookup methods that return exact database values.
    Never estimates, never modifies numbers.
    """

    def __init__(self):
        # Try loading OKF files first
        self.colleges: List[Dict] = []
        okf_dir = os.path.join(DATA_DIR, "okf", "colleges")
        if os.path.exists(okf_dir):
            logger.info(f"[OKF] Loading colleges from OKF directory: {okf_dir}")
            for filename in os.listdir(okf_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(okf_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.startswith("---"):
                            parts = content.split("---", 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                body = parts[2].strip()
                                try:
                                    from yaml import CSafeLoader as SafeLoader
                                except ImportError:
                                    from yaml import SafeLoader
                                college_data = yaml.load(frontmatter, Loader=SafeLoader)
                                if college_data:
                                    college_data["_okf_body"] = body
                                    self.colleges.append(college_data)
        else:
            self.colleges = _load_json("colleges_v2.json")

        self.cutoffs: List[Dict] = _load_json("cutoff_dataset.json")
        self.fees: List[Dict] = _load_json("Fee.json")
        self.hostels: List[Dict] = _load_json("hostels.json")
        self.scholarships: List[Dict] = _load_json("scholarships.json")
        self.loans: List[Dict] = _load_json("education_loans.json")
        self.counseling: Dict = _load_json("counseling_guide.json")

        # Build lookup indexes for fast access
        self._college_by_id: Dict[str, Dict] = {}
        self._college_by_name: Dict[str, Dict] = {}
        for c in self.colleges:
            cid = c.get("college_id", "")
            self._college_by_id[cid] = c
            # Normalize name for fuzzy lookup
            name_key = c.get("name", "").lower().strip()
            self._college_by_name[name_key] = c

        # Cutoff index by college_id
        self._cutoff_by_id: Dict[str, Dict] = {}
        for c in self.cutoffs:
            self._cutoff_by_id[c.get("college_id", "")] = c

        # Fee index by category
        self._fee_by_category: Dict[str, Dict] = {}
        for f in self.fees:
            cat = f.get("category", "").strip()
            self._fee_by_category[cat] = f

        # Hostel index by college name (lowercase)
        self._hostel_by_college: Dict[str, Dict] = {}
        self._hostel_by_id: Dict[str, Dict] = {}
        for h in self.hostels:
            college_name = (h.get("college", "") or h.get("name", "")).lower().strip()
            self._hostel_by_college[college_name] = h
            self._hostel_by_id[h.get("hostel_id", "")] = h

        logger.info(
            f"[JSONDataService] Ready: {len(self.colleges)} colleges, "
            f"{len(self.cutoffs)} cutoff records, {len(self.fees)} fee categories, "
            f"{len(self.hostels)} hostels, {len(self.scholarships)} scholarships, "
            f"{len(self.loans)} loan schemes"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # COLLEGE LOOKUP
    # ══════════════════════════════════════════════════════════════════════════

    def find_college(self, query: str) -> Optional[Dict]:
        """Find a college by ID, exact name, or fuzzy partial match."""
        # Try by ID
        if query.upper() in self._college_by_id:
            return self._college_by_id[query.upper()]

        q = query.lower().strip()

        # Try exact name match
        if q in self._college_by_name:
            return self._college_by_name[q]

        # Fuzzy partial match
        best_match = None
        best_score = 0
        for name, college in self._college_by_name.items():
            # Check if query is a substring of college name
            if q in name:
                score = len(q) / len(name)
                if score > best_score:
                    best_score = score
                    best_match = college
            # Also check common abbreviations
            abbr_map = {
                "rvce": "r.v. college", "rv college": "r.v. college",
                "bmsce": "b.m.s. college", "bms": "b.m.s. college",
                "msrit": "m.s. ramaiah", "ramaiah": "m.s. ramaiah",
                "pes": "pes university", "pesu": "pes university",
                "sit": "siddaganga", "sit tumkur": "siddaganga",
                "nie": "national institute of engineering",
                "nie mysore": "national institute of engineering",
                "dsce": "dayananda sagar",
                "bit": "bangalore institute of technology",
                "uvce": "visvesvaraya college of engineering",
                "sjce": "jayachamarajendra",
                "mvj": "m v j college",
                "ait": "ambedkar institute",
            }
            if q in abbr_map:
                target = abbr_map[q]
                if target in name:
                    return college

        return best_match

    def get_college_details(self, college_name: str) -> str:
        """Get formatted college details for LLM context injection."""
        college = self.find_college(college_name)
        if not college:
            return ""

        # If loaded from OKF, just return the pre-rendered Markdown body
        if "_okf_body" in college:
            return college["_okf_body"]

        parts = [f"## {college.get('college_name', college.get('name', 'Unknown'))}"]
        parts.append(f"- **Type**: {college.get('ownership', college.get('type', 'N/A'))}")
        
        loc = college.get('location', {})
        dist = loc.get('district') if isinstance(loc, dict) else college.get('location', 'N/A')
        parts.append(f"- **Location**: {dist}")
        parts.append(f"- **Affiliation**: {college.get('affiliated_university', college.get('affiliation', 'N/A'))}")
        parts.append(f"- **Established**: {college.get('established', 'N/A')}")
        
        appr = college.get('approval', {})
        naac = appr.get('naac_grade') if isinstance(appr, dict) else college.get('naac_grade', 'N/A')
        nba = appr.get('nba_accredited') if isinstance(appr, dict) else college.get('nba_accredited', False)
        parts.append(f"- **NAAC Grade**: {naac}")
        parts.append(f"- **NBA Accredited**: {'Yes' if nba else 'No'}")

        # Branches
        branches = college.get("branches", [])
        if branches:
            if isinstance(branches[0], dict):
                b_names = [b.get("branch_name", "") for b in branches]
            else:
                b_names = branches
            parts.append(f"- **Branches**: {', '.join(b_names)}")

        # Fee (V2 Sourced)
        fees = college.get("fees", {})
        if fees and isinstance(fees, dict):
            parts.append(f"\n### Fee Structure (Annual)")
            for k, v in fees.items():
                if v and isinstance(v, dict) and "value" in v:
                    val = v["value"]
                    src = v.get("source", "")
                    if val is not None:
                        fmt_val = f"₹{val:,.0f}" if isinstance(val, (int, float)) else str(val)
                        parts.append(f"- {k.replace('_', ' ').title()}: {fmt_val} (Source: {src})")
        else:
            # Fallback for V1
            fee = college.get("annual_fee", {})
            if fee and isinstance(fee, dict):
                parts.append(f"\n### Fee Structure (Annual)")
                parts.append(f"- GM/Others: ₹{fee.get('gm', 'N/A'):,.0f}" if isinstance(fee.get('gm'), (int, float)) else f"- GM/Others: {fee.get('gm', 'N/A')}")
                parts.append(f"- OBC (income <10L): ₹{fee.get('obc', 'N/A'):,.0f}" if isinstance(fee.get('obc'), (int, float)) else f"- OBC: {fee.get('obc', 'N/A')}")
                parts.append(f"- SC/ST: ₹{fee.get('sc_st', 'N/A'):,.0f}" if isinstance(fee.get('sc_st'), (int, float)) else f"- SC/ST: {fee.get('sc_st', 'N/A')}")

        # Cutoffs (V2 Sourced)
        cutoffs = college.get("cutoffs", {})
        if cutoffs and isinstance(cutoffs, dict) and "2024" in cutoffs:
            parts.append(f"\n### 2024 KCET Cutoff Ranks")
            r1 = cutoffs["2024"].get("Round1", {})
            for branch, cats in r1.items():
                if isinstance(cats, dict):
                    cat_parts = []
                    for cat, rank_obj in cats.items():
                        if isinstance(rank_obj, dict) and "closing_rank" in rank_obj:
                            cr = rank_obj["closing_rank"]
                            if cr and isinstance(cr, dict) and cr.get("value"):
                                cat_parts.append(f"{cat}: {cr['value']} (Source: {cr.get('source', '')})")
                    if cat_parts:
                        parts.append(f"- **{branch}**: {', '.join(cat_parts)}")
        else:
            # Fallback V1
            cutoff_2024 = college.get("cutoff_2024", {})
            if cutoff_2024:
                parts.append(f"\n### 2024 KCET Cutoff Ranks")
                for branch, cats in cutoff_2024.items():
                    if isinstance(cats, dict):
                        cat_str = ", ".join(f"{k}: {v}" for k, v in cats.items())
                        parts.append(f"- **{branch}**: {cat_str}")

        # Placements (V2 Sourced)
        placements = college.get("placements", {})
        if placements and isinstance(placements, dict):
            avg = placements.get("average_package")
            high = placements.get("highest_package")
            if avg or high:
                parts.append(f"\n### Placements")
                if avg and isinstance(avg, dict) and avg.get("value"):
                    parts.append(f"- Average Package: {avg['value']} (Source: {avg.get('source', '')})")
                elif college.get("placement_avg_lpa"):
                    parts.append(f"- Average Package: ₹{college.get('placement_avg_lpa')} LPA")
                    
                if high and isinstance(high, dict) and high.get("value"):
                    parts.append(f"- Highest Package: {high['value']} (Source: {high.get('source', '')})")
                elif college.get("placement_highest_lpa"):
                    parts.append(f"- Highest Package: ₹{college.get('placement_highest_lpa')} LPA")
                    
                recruiters = placements.get("top_recruiters") or college.get("top_recruiters", [])
                if recruiters:
                    parts.append(f"- Top Recruiters: {', '.join(recruiters)}")

        # Hostel (V2 Sourced)
        hostel = college.get("hostel", {})
        if hostel and isinstance(hostel, dict):
            boys = hostel.get("boys_hostel")
            girls = hostel.get("girls_hostel")
            if boys or girls:
                parts.append(f"\n### Hostel Information")
                if boys and isinstance(boys, dict) and boys.get("available"):
                    fee = boys.get("annual_fee", {})
                    fee_val = fee.get("value") if isinstance(fee, dict) else None
                    parts.append(f"- **Boys Hostel**: Available. Annual Fee: {fee_val or 'N/A'}")
                if girls and isinstance(girls, dict) and girls.get("available"):
                    fee = girls.get("annual_fee", {})
                    fee_val = fee.get("value") if isinstance(fee, dict) else None
                    parts.append(f"- **Girls Hostel**: Available. Annual Fee: {fee_val or 'N/A'}")
        else:
            parts.append(f"- **Hostel Available**: {'Yes' if college.get('hostel_available') else 'No'}")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # CUTOFF-BASED COLLEGE RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    @lru_cache(maxsize=128)
    def recommend_colleges(
        self,
        rank: int,
        branch: str = "CSE",
        category: str = "GM",
        location: Optional[str] = None,
        hostel_needed: bool = False,
        budget: Optional[int] = None,
        government_only: bool = False,
        private_only: bool = False,
    ) -> Dict[str, List[Dict]]:
        """
        Find colleges where the student can get admission.
        Returns classified results: SAFE, MODERATE, AMBITIOUS.
        
        Uses EXACT cutoff values from the JSON database.
        Never estimates or invents cutoff numbers.
        """
        safe = []
        moderate = []
        ambitious = []

        branch_upper = branch.upper().replace(" ", "_")
        category_upper = category.upper()

        # Map common category names
        cat_map = {
            "GENERAL": "GM", "GEN": "GM", "OC": "GM",
            "OBC": "OBC", "2A": "OBC", "3A": "OBC", "3B": "OBC",
            "CAT1": "OBC", "CATEGORY-1": "OBC",
            "SC": "SC", "ST": "ST", "EWS": "GM",
        }
        category_mapped = cat_map.get(category_upper, category_upper)

        for college in self.colleges:
            # Filter by location if specified
            if location:
                col_location = (college.get("location", "") or "").lower()
                col_district = (college.get("district", "") or "").lower()
                if location.lower() not in col_location and location.lower() not in col_district:
                    continue

            # Filter by hostel
            if hostel_needed and not college.get("hostel_available"):
                continue

            # Filter by budget
            if budget:
                fee = college.get("annual_fee", {})
                fee_key = "sc_st" if category_mapped in ("SC", "ST") else "obc" if category_mapped == "OBC" else "gm"
                college_fee = fee.get(fee_key, 0)
                if isinstance(college_fee, (int, float)) and college_fee > budget:
                    continue

            # Filter by government/private
            col_type = (college.get("type", "") or "").lower()
            if government_only and "government" not in col_type:
                continue
            if private_only and "private" not in col_type and "unaided" not in col_type:
                continue

            # Check cutoff
            cutoff_2024 = college.get("cutoff_2024", {})
            branch_cutoff = cutoff_2024.get(branch_upper, {})
            if not isinstance(branch_cutoff, dict):
                continue

            cutoff_rank = branch_cutoff.get(category_mapped)
            if cutoff_rank is None:
                # Try fallback to GM
                cutoff_rank = branch_cutoff.get("GM")
            if cutoff_rank is None:
                continue

            # Build result entry
            fee = college.get("annual_fee", {})
            fee_key = "sc_st" if category_mapped in ("SC", "ST") else "obc" if category_mapped == "OBC" else "gm"

            entry = {
                "college_id": college.get("college_id"),
                "name": college.get("name"),
                "location": college.get("location"),
                "type": college.get("type"),
                "cutoff_rank": cutoff_rank,
                "branch": branch_upper,
                "category": category_mapped,
                "annual_fee": fee.get(fee_key, "N/A"),
                "hostel_available": college.get("hostel_available", False),
                "placement_avg_lpa": college.get("placement_avg_lpa"),
                "placement_highest_lpa": college.get("placement_highest_lpa"),
                "naac_grade": college.get("naac_grade"),
            }

            # Classify: SAFE / MODERATE / AMBITIOUS based on strict exact formula
            if cutoff_rank >= rank * 1.25:
                entry["classification"] = "SAFE"
                entry["margin"] = f"Safe (cutoff >= rank * 1.25)"
                safe.append(entry)
            elif cutoff_rank >= rank * 0.9 and cutoff_rank < rank * 1.25:
                entry["classification"] = "MODERATE"
                entry["margin"] = f"Moderate (cutoff between rank * 0.9 and rank * 1.25)"
                moderate.append(entry)
            elif cutoff_rank < rank * 0.9:
                entry["classification"] = "AMBITIOUS"
                entry["margin"] = f"Ambitious (cutoff < rank * 0.9)"
                ambitious.append(entry)

        # Scoring function based on KEA rules (100 point scale)
        def score_college(c):
            score = 0
            # 40% cutoff suitability
            cutoff = c["cutoff_rank"]
            if cutoff >= rank:
                score += 40
            else:
                score += max(0, 40 * (cutoff / rank))
            # 20% placement
            avg_lpa = c.get("placement_avg_lpa")
            if avg_lpa:
                try:
                    score += min(20, (float(avg_lpa) / 15.0) * 20)
                except ValueError:
                    score += 10
            else:
                score += 5
            # 15% accreditation
            naac = c.get("naac_grade", "")
            if naac == "A++": score += 15
            elif naac == "A+": score += 12
            elif naac == "A": score += 10
            elif naac == "B++": score += 8
            elif naac == "B+": score += 6
            else: score += 4
            # 10% hostel quality
            if c.get("hostel_available"): score += 10
            # 10% fees
            fee_val = c.get("annual_fee")
            if isinstance(fee_val, (int, float)):
                if budget and budget > 0:
                    score += max(0, min(10, 10 * (1 - fee_val / budget)))
                else:
                    score += 5
            # 5% location preference
            loc = (c.get("location", "")).lower()
            if location and location.lower() in loc:
                score += 5
            return score

        # Sort each tier by calculated score descending
        safe.sort(key=lambda x: score_college(x), reverse=True)
        moderate.sort(key=lambda x: score_college(x), reverse=True)
        ambitious.sort(key=lambda x: score_college(x), reverse=True)

        return {"safe": safe, "moderate": moderate, "ambitious": ambitious}

    def format_recommendations(
        self,
        rank: int,
        branch: str = "CSE",
        category: str = "GM",
        location: Optional[str] = None,
        hostel_needed: bool = False,
        budget: Optional[int] = None,
        government_only: bool = False,
        private_only: bool = False,
    ) -> str:
        """
        Format college recommendations as structured text for LLM context.
        Returns exact database values — never estimates.
        """
        results = self.recommend_colleges(rank, branch, category, location, hostel_needed, budget, government_only, private_only)

        parts = [
            f"## KCET College Recommendations (Database Values)",
            f"**Student**: Rank {rank} | Branch: {branch} | Category: {category}",
        ]
        if location:
            parts.append(f"**Location Preference**: {location}")
        if budget:
            parts.append(f"**Budget**: ₹{budget:,}/year")

        for tier, label, emoji in [
            ("safe", "🟢 SAFE", "✅"),
            ("moderate", "🟡 MODERATE", "⚠️"),
            ("ambitious", "🔴 AMBITIOUS", "🎯"),
        ]:
            colleges = results[tier]
            if not colleges:
                continue
            parts.append(f"\n### {label} ({len(colleges)} colleges)")
            for c in colleges[:7]:  # Top 7 per tier
                fee_str = f"₹{c['annual_fee']:,.0f}" if isinstance(c['annual_fee'], (int, float)) else str(c['annual_fee'])
                parts.append(
                    f"- {emoji} **{c['name']}** ({c['location']})\n"
                    f"  Cutoff: {c['cutoff_rank']} | Fee: {fee_str}/yr | "
                    f"Type: {c['type']} | "
                    f"Avg Pkg: {c.get('placement_avg_lpa', 'N/A')} LPA"
                )
                parts.append(f"  {c['margin']}")

        total = sum(len(results[t]) for t in ("safe", "moderate", "ambitious"))
        if total == 0:
            parts.append(
                f"\nNo college in the current database satisfies all specified constraints."
            )

        return "\n".join(parts), results

    # ══════════════════════════════════════════════════════════════════════════
    # FEE LOOKUP
    # ══════════════════════════════════════════════════════════════════════════
    @lru_cache(maxsize=256)
    def get_fee_structure(self, college_name: Optional[str] = None, fee_category: Optional[str] = None) -> str:
        """Get fee structure. Uses exact database values."""
        if college_name:
            college = self.find_college(college_name)
            if college:
                fee = college.get("annual_fee", {})
                fee_cat = college.get("fee_category", "")
                parts = [f"## Fee Structure: {college.get('name', college_name)}"]
                parts.append(f"**Fee Category**: {fee_cat}")
                if fee:
                    parts.append(f"- GM/Others (income >10L): ₹{fee.get('gm', 'N/A'):,.0f}" if isinstance(fee.get('gm'), (int, float)) else f"- GM: {fee.get('gm', 'N/A')}")
                    parts.append(f"- OBC/Cat-1 (income <10L): ₹{fee.get('obc', 'N/A'):,.0f}" if isinstance(fee.get('obc'), (int, float)) else f"- OBC: {fee.get('obc', 'N/A')}")
                    parts.append(f"- SC/ST: ₹{fee.get('sc_st', 'N/A'):,.0f} (Fee waiver)" if isinstance(fee.get('sc_st'), (int, float)) and fee.get('sc_st') == 0 else f"- SC/ST: ₹{fee.get('sc_st', 'N/A'):,.0f}" if isinstance(fee.get('sc_st'), (int, float)) else f"- SC/ST: {fee.get('sc_st', 'N/A')}")
                return "\n".join(parts)

        # Return all fee categories
        if fee_category:
            # Try exact match
            for f in self.fees:
                if fee_category.lower() in f.get("category", "").lower():
                    parts = [f"## Fee Structure: {f['category']}"]
                    parts.append(f"- GM/Others: ₹{f.get('gm_and_others_above_income_limit', 'N/A'):,}")
                    parts.append(f"- SNQ Quota: ₹{f.get('snq_quota', 'N/A'):,}")
                    parts.append(f"- SC/ST Concession: ₹{f.get('sc_st_concession', 0):,}")
                    parts.append(f"- Cat-1 (<2.5L): ₹{f.get('cat1_upto_2_5_lakhs', 0):,}")
                    parts.append(f"- Others (<10L): ₹{f.get('others_upto_10_lakhs', 'N/A'):,}")
                    return "\n".join(parts)

        # Return full fee table
        parts = ["## Karnataka Engineering Fee Structure (KEA 2024-25)"]
        for f in self.fees:
            cat = f.get("category", "Unknown")
            gm = f.get("gm_and_others_above_income_limit", "N/A")
            obc = f.get("others_upto_10_lakhs", "N/A")
            sc = f.get("sc_st_concession", 0)
            parts.append(f"\n**{cat}**")
            parts.append(f"  GM/Others: ₹{gm:,}" if isinstance(gm, (int, float)) else f"  GM: {gm}")
            parts.append(f"  OBC (<10L): ₹{obc:,}" if isinstance(obc, (int, float)) else f"  OBC: {obc}")
            parts.append(f"  SC/ST: ₹{sc:,} (Fee waiver)" if sc == 0 else f"  SC/ST: ₹{sc:,}")
        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # HOSTEL LOOKUP
    # ══════════════════════════════════════════════════════════════════════════
    @lru_cache(maxsize=256)
    def get_hostel_info(self, college_name: Optional[str] = None, location: Optional[str] = None, category: Optional[str] = None) -> str:
        """Get hostel information. Returns exact database values only."""
        results = []

        for h in self.hostels:
            h_college = (h.get("college", "") or h.get("name", "")).lower()
            h_location = (h.get("location", "")).lower()
            h_categories = [c.lower() for c in (h.get("category", []) if isinstance(h.get("category"), list) else [])]

            # Filter
            if college_name and college_name.lower() not in h_college:
                continue
            if location and location.lower() not in h_location:
                continue
            if category:
                if h_categories and category.lower() not in " ".join(h_categories):
                    continue

            results.append(h)

        if not results:
            return ""

        parts = ["## Hostel Information (Database Verified)"]
        for h in results:
            name = h.get("college") or h.get("name", "Unknown")
            parts.append(f"\n### {name}")
            parts.append(f"- **Location**: {h.get('location', 'N/A')}")
            parts.append(f"- **Type**: {h.get('type', 'N/A')}")

            # Facilities
            fac = h.get("facilities", {})
            if fac:
                parts.append(f"- **Boys Hostel**: {'Yes' if fac.get('boys_hostel') else 'No'}")
                parts.append(f"- **Girls Hostel**: {'Yes' if fac.get('girls_hostel') else 'No'}")
                cap_boys = fac.get("capacity_boys") or fac.get("capacity")
                cap_girls = fac.get("capacity_girls")
                if cap_boys:
                    parts.append(f"- **Capacity (Boys)**: {cap_boys}")
                if cap_girls:
                    parts.append(f"- **Capacity (Girls)**: {cap_girls}")
                rooms = fac.get("rooms", [])
                if rooms:
                    parts.append(f"- **Room Types**: {', '.join(rooms)}")
                amenities = fac.get("amenities", [])
                if amenities:
                    parts.append(f"- **Amenities**: {', '.join(amenities)}")

            # Fees
            fees = h.get("fees", {})
            if fees:
                parts.append(f"\n**Hostel Fees:**")
                for key, val in fees.items():
                    label = key.replace("_", " ").title()
                    if isinstance(val, (int, float)):
                        parts.append(f"  - {label}: ₹{val:,}")
                    else:
                        parts.append(f"  - {label}: {val}")

            # Food
            food = h.get("food")
            if food:
                parts.append(f"- **Food**: {food}")

            # Rules
            rules = h.get("rules", [])
            if rules:
                parts.append(f"- **Rules**: {'; '.join(rules)}")

            # Eligibility
            elig = h.get("eligibility", {})
            if isinstance(elig, dict):
                cats = elig.get("category", [])
                if cats:
                    parts.append(f"- **Eligible Categories**: {', '.join(cats)}")
                income = elig.get("income_limit")
                if income:
                    parts.append(f"- **Income Limit**: ₹{income:,}")
            elif isinstance(elig, str):
                parts.append(f"- **Eligibility**: {elig}")

            # How to apply
            how = h.get("how_to_apply")
            if how:
                parts.append(f"- **How to Apply**: {how}")

            # Contact
            contact = h.get("contact")
            if contact:
                parts.append(f"- **Contact**: {contact}")

            # Highlights
            highlights = h.get("highlights", [])
            if highlights:
                parts.append(f"- **Highlights**: {'; '.join(highlights)}")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # SCHOLARSHIP LOOKUP
    # ══════════════════════════════════════════════════════════════════════════

    @lru_cache(maxsize=256)
    def get_scholarships(
        self,
        category: Optional[str] = None,
        income: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> str:
        """Get eligible scholarships. Returns exact database values only."""
        results = []

        for s in self.scholarships:
            elig = s.get("eligibility", {})

            # Category filter
            if category:
                elig_cats = elig.get("category", [])
                cat_lower = category.lower()
                cats_lower = [c.lower() for c in elig_cats]

                # Check if student's category matches any eligible category
                match = False
                for ec in cats_lower:
                    if cat_lower in ec or ec in cat_lower or "all" in ec:
                        match = True
                        break
                if not match:
                    continue

            # Income filter
            if income is not None:
                income_limit = elig.get("income_limit")
                if income_limit and income > income_limit:
                    continue

            # Gender filter
            if gender:
                elig_gender = elig.get("gender")
                if elig_gender and gender.lower() != elig_gender.lower():
                    continue

            results.append(s)

        if not results:
            return ""

        parts = ["## Eligible Scholarships (Database Verified)"]
        for s in results:
            parts.append(f"\n### {s.get('name', 'Unknown')}")
            parts.append(f"- **Department**: {s.get('department', 'N/A')}")

            # Eligibility
            elig = s.get("eligibility", {})
            if elig.get("category"):
                parts.append(f"- **For**: {', '.join(elig['category'])}")
            if elig.get("income_limit"):
                parts.append(f"- **Income Limit**: ₹{elig['income_limit']:,}")
            if elig.get("marks_required"):
                parts.append(f"- **Marks Required**: {elig['marks_required']}")

            # Benefits
            benefits = s.get("benefits", {})
            if benefits:
                parts.append(f"**Benefits:**")
                if benefits.get("full_fee_reimbursement"):
                    parts.append(f"  - Full Fee Reimbursement: Yes")
                if benefits.get("fee_reimbursement"):
                    parts.append(f"  - Fee Reimbursement: {benefits['fee_reimbursement']}")
                if benefits.get("fee_concession"):
                    parts.append(f"  - Fee Concession: {benefits['fee_concession']}")
                ma = benefits.get("maintenance_allowance", {})
                if isinstance(ma, dict):
                    if ma.get("hosteller"):
                        parts.append(f"  - Maintenance (Hosteller): ₹{ma['hosteller']}/month")
                    if ma.get("day_scholar"):
                        parts.append(f"  - Maintenance (Day Scholar): ₹{ma['day_scholar']}/month")
                amt = benefits.get("amount_per_year")
                if isinstance(amt, dict):
                    for k, v in amt.items():
                        parts.append(f"  - Year {k}: ₹{v:,}")
                elif isinstance(amt, (int, float)):
                    parts.append(f"  - Amount/Year: ₹{amt:,}")

            # Application
            portal = s.get("application_portal")
            if portal:
                parts.append(f"- **Apply At**: {portal}")
            deadline = s.get("deadline")
            if deadline:
                parts.append(f"- **Deadline**: {deadline}")

            # Documents
            docs = s.get("documents_required", [])
            if docs:
                parts.append(f"- **Documents**: {', '.join(docs)}")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # EDUCATION LOAN LOOKUP
    # ══════════════════════════════════════════════════════════════════════════

    def get_loans(self, income: Optional[int] = None) -> str:
        """Get education loan options. Returns exact database values only."""
        parts = ["## Education Loan Options (Database Verified)"]

        for loan in self.loans:
            parts.append(f"\n### {loan.get('bank', 'Unknown')} — {loan.get('scheme_name', '')}")
            parts.append(f"- **Type**: {loan.get('type', 'N/A')}")

            # Loan amount
            amt = loan.get("loan_amount", {})
            if amt.get("india_max"):
                parts.append(f"- **Max (India)**: ₹{amt['india_max']:,}")
            if amt.get("abroad_max"):
                parts.append(f"- **Max (Abroad)**: ₹{amt['abroad_max']:,}")
            if amt.get("max"):
                parts.append(f"- **Max Amount**: ₹{amt['max']:,}")

            # Interest rate
            rate = loan.get("interest_rate", {})
            if rate.get("base_rate"):
                parts.append(f"- **Interest Rate**: {rate['base_rate']}%")
            if rate.get("female_discount"):
                parts.append(f"- **Female Discount**: {rate['female_discount']}%")

            # Collateral
            coll = loan.get("collateral", {})
            if coll:
                for k, v in coll.items():
                    label = k.replace("_", " ").title()
                    parts.append(f"- **{label}**: {v}")

            # Repayment
            repay = loan.get("repayment", {})
            if repay.get("moratorium"):
                parts.append(f"- **Moratorium**: {repay['moratorium']}")
            if repay.get("tenure"):
                parts.append(f"- **Tenure**: {repay['tenure']}")

            # Subsidy (important for low-income students)
            subsidy = loan.get("subsidy", {})
            if subsidy:
                parts.append(f"- **Government Subsidy**: {subsidy.get('scheme', 'N/A')}")
                parts.append(f"  Eligibility: {subsidy.get('eligibility', 'N/A')}")
                parts.append(f"  Benefit: {subsidy.get('benefit', 'N/A')}")

            # CISS highlight for low-income families
            if income and income <= 450000 and subsidy:
                parts.append(f"  ⭐ **You qualify for CISS** — government pays full interest during study period!")

            parts.append(f"- **Apply At**: {loan.get('apply_at', 'N/A')}")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # COUNSELING PROCESS
    # ══════════════════════════════════════════════════════════════════════════

    def get_counseling_info(self, exam_type: str = "engineering") -> str:
        """Get KCET counseling process info. Returns exact database values."""
        exam_data = self.counseling.get(exam_type, self.counseling.get("engineering", {}))
        if not exam_data:
            return ""

        parts = [f"## {exam_data.get('title', 'Counseling Process')}"]
        steps = exam_data.get("steps", [])
        for step in steps:
            parts.append(f"\n**Step {step.get('id', '')}: {step.get('title', '')}**")
            parts.append(f"{step.get('description', '')}")

        # Documents
        docs = self.counseling.get("documents", [])
        if docs:
            parts.append(f"\n### Required Documents")
            for doc in docs:
                req = "✅ MANDATORY" if doc.get("required") else "📋 If applicable"
                parts.append(f"- {req} **{doc.get('name', '')}**: {doc.get('details', '')}")

        # FAQ
        faq = self.counseling.get("faq", [])
        if faq:
            parts.append(f"\n### Common Questions")
            for qa in faq:
                parts.append(f"- **Q**: {qa.get('q', '')}")
                parts.append(f"  **A**: {qa.get('a', '')}")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # CUTOFF TRENDS (MULTI-YEAR)
    # ══════════════════════════════════════════════════════════════════════════
    @lru_cache(maxsize=256)
    def get_cutoff_trends(self, college_name: str, branch: str = "CSE", category: str = "GM") -> str:
        """Get multi-year cutoff trends for a specific college+branch+category."""
        college = self.find_college(college_name)
        if not college:
            return ""

        trends = college.get("cutoff_trends", {})
        if not trends:
            # Fallback to cutoff_dataset
            for c in self.cutoffs:
                if c.get("college_id") == college.get("college_id"):
                    trends = c.get("cutoffs", {})
                    break

        if not trends:
            return ""

        branch_upper = branch.upper()
        cat_upper = category.upper()

        parts = [f"## Cutoff Trends: {college.get('name', college_name)} | {branch_upper} | {cat_upper}"]
        parts.append("| Year | Cutoff Rank |")
        parts.append("|------|-----------|")

        for year in sorted(trends.keys()):
            year_data = trends[year]
            branch_data = year_data.get(branch_upper, {})
            rank = branch_data.get(cat_upper, "N/A")
            parts.append(f"| {year} | {rank} |")

        return "\n".join(parts)

    # ══════════════════════════════════════════════════════════════════════════
    # MASTER CONTEXT BUILDER — used by LLM pipeline
    # ══════════════════════════════════════════════════════════════════════════

    def build_context_for_query(self, query: str, profile: Dict[str, Any] = None) -> str:
        """
        Analyze the user query and build rich structured context from JSON databases.
        This is the main integration point with the LLM pipeline.
        
        Returns a formatted string with all relevant database information.
        """
        profile = profile or {}
        query_lower = query.lower()
        context_parts = []

        # ── Extract profile attributes ────────────────────────────────────
        rank = profile.get("kcet_rank") or profile.get("rank")
        if rank:
            try:
                rank = int(rank)
            except (ValueError, TypeError):
                rank = None

        branch = profile.get("branch") or profile.get("preferred_branches", ["CSE"])[0] if profile.get("preferred_branches") else None
        category = profile.get("category", "GM")
        income = profile.get("income") or profile.get("family_income")
        if income:
            try:
                income = int(income)
            except (ValueError, TypeError):
                income = None
        gender = profile.get("gender")
        location = profile.get("location") or profile.get("preferred_location")
        hostel_needed = profile.get("hostel_needed", False)
        budget = profile.get("budget")
        if budget:
            try:
                budget = int(budget)
            except (ValueError, TypeError):
                budget = None
                
        government_only = profile.get("government_only", False) or "government only" in query_lower or "govt only" in query_lower
        private_only = profile.get("private_only", False) or "private only" in query_lower

        # ── Detect query intent and build context ─────────────────────────

        # 1. College recommendation query
        college_kw = ["college", "rank", "cutoff", "admission", "branch", "recommend",
                      "predict", "get into", "chances", "which college", "best college",
                      "top college", "suggest", "option"]
        if any(kw in query_lower for kw in college_kw):
            # Try to extract rank from query if not in profile
            if not rank:
                import re
                rank_match = re.search(r'rank\s*(?:is\s*)?(\d+)', query_lower)
                if rank_match:
                    rank = int(rank_match.group(1))
                else:
                    num_match = re.search(r'\b(\d{3,6})\b', query_lower)
                    if num_match:
                        rank = int(num_match.group(1))

            # Try to extract branch from query
            if not branch:
                branch_map = {
                    "cse": "CSE", "computer": "CSE", "cs": "CSE",
                    "ece": "ECE", "electronics": "ECE",
                    "ise": "ISE", "information science": "ISE",
                    "eee": "EEE", "electrical": "EEE",
                    "me": "ME", "mechanical": "ME",
                    "civil": "CIVIL",
                    "ai": "AI", "artificial intelligence": "AI",
                    "ds": "DS", "data science": "DS",
                    "cyber": "CY", "cybersecurity": "CY",
                }
                for kw, br in branch_map.items():
                    if kw in query_lower:
                        branch = br
                        break
                if not branch:
                    branch = "CSE"  # default

            if rank:
                recs_str, recs_dict = self.format_recommendations(
                    rank=rank,
                    branch=branch,
                    category=category,
                    location=location,
                    hostel_needed=hostel_needed,
                    budget=budget,
                    government_only=government_only,
                    private_only=private_only,
                )
                context_parts.append(recs_str)
                recommended_college_names = [
                    c["name"] for t in ("safe", "moderate", "ambitious") for c in recs_dict[t]
                ]

        # 2. Specific college detail query
        college_names = [
            "rvce", "rv college", "bmsce", "bms", "pes", "pesu", "msrit", "ramaiah",
            "sit", "siddaganga", "nie", "dsce", "dayananda", "bit", "uvce", "sjce",
            "mvj", "ait", "nmit", "rnsit", "jss", "sdm", "malnad", "nitte",
        ]
        for cn in college_names:
            if cn in query_lower:
                detail = self.get_college_details(cn)
                if detail:
                    context_parts.append(detail)
                break

        # 3. Fee query
        fee_kw = ["fee", "fees", "tuition", "cost", "afford", "expense", "how much", "price"]
        if any(kw in query_lower for kw in fee_kw):
            # Check if asking about a specific college
            found_college_fee = False
            for cn in college_names:
                if cn in query_lower:
                    fee_info = self.get_fee_structure(college_name=cn)
                    if fee_info:
                        context_parts.append(fee_info)
                        found_college_fee = True
                    break
            if not found_college_fee:
                context_parts.append(self.get_fee_structure())

        # 4. Hostel query
        hostel_kw = ["hostel", "accommodation", "pg", "paying guest", "room", "mess",
                     "staying", "living", "dormitory", "bcm hostel", "gate timing", "food type"]
        if any(kw in query_lower for kw in hostel_kw) or hostel_needed:
            hostel_info = ""
            
            # Strict Hostel Retrieval Rule: If we just recommended colleges, ONLY fetch hostels for those colleges.
            if 'recommended_college_names' in locals() and recommended_college_names:
                h_parts = []
                for cn in recommended_college_names:
                    hi = self.get_hostel_info(college_name=cn)
                    if hi:
                        h_parts.append(hi)
                if h_parts:
                    hostel_info = "\n".join(h_parts)
                else:
                    hostel_info = "Verified hostel information is not available in the database."
            else:
                # Check for specific college hostel
                for cn in college_names:
                    if cn in query_lower:
                        hostel_info = self.get_hostel_info(college_name=cn)
                        break
                if not hostel_info and location:
                    hostel_info = self.get_hostel_info(location=location)
                if not hostel_info and category:
                    hostel_info = self.get_hostel_info(category=category)
                if not hostel_info:
                    hostel_info = self.get_hostel_info()
            if hostel_info:
                context_parts.append(hostel_info)

        # 5. Scholarship query
        schol_kw = ["scholarship", "vidyasiri", "post matric", "fee waiver", "ssp",
                    "sc scholarship", "st scholarship", "obc scholarship", "minority",
                    "free education", "stipend", "financial aid", "grant", "pragati"]
        if any(kw in query_lower for kw in schol_kw):
            schol_info = self.get_scholarships(
                category=category,
                income=income,
                gender=gender,
            )
            if schol_info:
                context_parts.append(schol_info)

        # 6. Loan query
        loan_kw = ["loan", "education loan", "bank loan", "interest", "emi",
                   "collateral", "vidyalakshmi", "repayment", "ciss", "subsidy"]
        if any(kw in query_lower for kw in loan_kw):
            context_parts.append(self.get_loans(income=income))

        # 7. Counseling process query
        counsel_kw = ["counseling", "counselling", "process", "document verification",
                      "option entry", "allotment", "choice filling", "reporting",
                      "kea process", "admission process", "how to apply", "documents needed"]
        if any(kw in query_lower for kw in counsel_kw):
            context_parts.append(self.get_counseling_info())

        # 8. Cutoff trends query
        if "trend" in query_lower or "year" in query_lower or "history" in query_lower:
            for cn in college_names:
                if cn in query_lower:
                    trend = self.get_cutoff_trends(cn, branch=branch or "CSE", category=category)
                    if trend:
                        context_parts.append(trend)
                    break

        # Join all context parts
        combined = "\n\n".join(context_parts)
        if combined:
            return f"=== PRIORITY 1: STRUCTURED DATABASE (exact values — do NOT modify) ===\n\n{combined}\n\n=== END DATABASE ==="
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ══════════════════════════════════════════════════════════════════════════════
_service_instance: Optional[JSONDataService] = None


def get_json_data_service() -> JSONDataService:
    """Get or create the JSONDataService singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = JSONDataService()
    return _service_instance
