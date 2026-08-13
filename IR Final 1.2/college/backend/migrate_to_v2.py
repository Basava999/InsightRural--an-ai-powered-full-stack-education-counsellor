#!/usr/bin/env python3
# ==============================================================================
# InsightRural — Migrate Existing JSON Data → V2 Unified Schema
# ==============================================================================
# Reads: Production_Ready_Colleges.json, cutoff_dataset.json, hostels.json,
#         Fee.json, scholarships.json, education_loans.json
# Writes: colleges_v2.json (single unified file)
#
# Usage:  python migrate_to_v2.py
# ==============================================================================

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add backend to path for schema import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "colleges_v2.json")

SOURCE = "InsightRural Database"
NOW = datetime.now().isoformat()


def load(filename: str) -> Any:
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] {filename} not found, skipping")
        return []


def sourced(value, source=SOURCE):
    """Wrap a value with provenance."""
    if value is None:
        return None
    return {"value": value, "source": source, "scraped_at": NOW}


def migrate_college(college: Dict, cutoff_map: Dict, hostel_map: Dict, fee_data: List) -> Dict:
    """Convert a single college record from V1 → V2 schema."""
    cid = college.get("college_id", "")
    name = college.get("name", "")

    # ── Location ──────────────────────────────────────────────────────────
    location = {
        "district": college.get("district") or college.get("location"),
        "state": "Karnataka",
        "google_maps_link": college.get("google_maps_link"),
    }

    # Merge coordinates from cutoff_dataset if available
    cutoff_entry = cutoff_map.get(cid, {})
    coords = cutoff_entry.get("coordinates", {})
    if coords:
        location["latitude"] = coords.get("lat")
        location["longitude"] = coords.get("lng")

    # ── Branches ──────────────────────────────────────────────────────────
    branch_names = college.get("branches", [])
    branches = [
        {"branch_name": b, "branch_code": b, "degree": "B.E.", "duration": 4}
        for b in branch_names
    ]

    # ── Cutoffs (restructured: year → round → branch → category) ─────────
    cutoffs = {}

    # From Production_Ready_Colleges.json: cutoff_2024, cutoff_trends
    cutoff_2024 = college.get("cutoff_2024", {})
    if cutoff_2024:
        cutoffs["2024"] = {"Round1": {}}
        for branch, cats in cutoff_2024.items():
            if isinstance(cats, dict):
                cutoffs["2024"]["Round1"][branch] = {}
                for cat, rank in cats.items():
                    cutoffs["2024"]["Round1"][branch][cat] = {
                        "closing_rank": sourced(rank, "KEA Official / InsightRural DB")
                    }

    cutoff_trends = college.get("cutoff_trends", {})
    for year, year_data in cutoff_trends.items():
        if year not in cutoffs:
            cutoffs[year] = {"Round1": {}}
        if isinstance(year_data, dict):
            for branch, cats in year_data.items():
                if isinstance(cats, dict):
                    if branch not in cutoffs[year]["Round1"]:
                        cutoffs[year]["Round1"][branch] = {}
                    for cat, rank in cats.items():
                        cutoffs[year]["Round1"][branch][cat] = {
                            "closing_rank": sourced(rank, "KEA Official / InsightRural DB")
                        }

    # Also merge from cutoff_dataset.json (may have more years)
    cutoff_ds = cutoff_map.get(cid, {}).get("cutoffs", {})
    for year, year_data in cutoff_ds.items():
        if year not in cutoffs:
            cutoffs[year] = {"Round1": {}}
        if isinstance(year_data, dict):
            for branch, cats in year_data.items():
                if isinstance(cats, dict):
                    if branch not in cutoffs[year].get("Round1", {}):
                        if "Round1" not in cutoffs[year]:
                            cutoffs[year]["Round1"] = {}
                        cutoffs[year]["Round1"][branch] = {}
                    for cat, rank in cats.items():
                        if branch not in cutoffs[year]["Round1"]:
                            cutoffs[year]["Round1"][branch] = {}
                        if cat not in cutoffs[year]["Round1"][branch]:
                            cutoffs[year]["Round1"][branch][cat] = {
                                "closing_rank": sourced(rank, "KEA Official / InsightRural DB")
                            }

    # ── Fees ──────────────────────────────────────────────────────────────
    annual_fee = college.get("annual_fee", {})
    if isinstance(annual_fee, (int, float)):
        fees = {
            "kcet_fee_gm": sourced(annual_fee, "InsightRural Fee Database"),
            "kcet_fee_obc": sourced(annual_fee, "InsightRural Fee Database"),
            "kcet_fee_sc_st": sourced(annual_fee, "InsightRural Fee Database"),
        }
    else:
        fees = {
            "kcet_fee_gm": sourced(annual_fee.get("gm"), "InsightRural Fee Database"),
            "kcet_fee_obc": sourced(annual_fee.get("obc"), "InsightRural Fee Database"),
            "kcet_fee_sc_st": sourced(annual_fee.get("sc_st"), "InsightRural Fee Database"),
        }

    # ── Placements ────────────────────────────────────────────────────────
    placements = {
        "average_package": sourced(
            f"{college.get('placement_avg_lpa')} LPA" if college.get('placement_avg_lpa') else None,
            "InsightRural Placement Database"
        ),
        "highest_package": sourced(
            f"{college.get('placement_highest_lpa')} LPA" if college.get('placement_highest_lpa') else None,
            "InsightRural Placement Database"
        ),
        "top_recruiters": college.get("top_recruiters"),
    }

    # ── Hostel ────────────────────────────────────────────────────────────
    hostel_entry = hostel_map.get(name.lower().strip(), {})
    hostel = {"boys_hostel": None, "girls_hostel": None}

    if hostel_entry:
        fac = hostel_entry.get("facilities", {})
        hostel_fees = hostel_entry.get("fees", {})
        
        boys = None
        if fac.get("boys_hostel"):
            boys = {
                "available": True,
                "capacity": fac.get("capacity_boys"),
                "room_types": fac.get("rooms"),
                "annual_fee": sourced(hostel_fees.get("annual_hostel_fee"), "InsightRural Hostel Database"),
                "mess_fee_monthly": sourced(hostel_fees.get("mess_fee_monthly"), "InsightRural Hostel Database"),
                "amenities": fac.get("amenities"),
                "food_type": hostel_entry.get("food"),
                "rules": hostel_entry.get("rules"),
            }

        girls = None
        if fac.get("girls_hostel"):
            girls = {
                "available": True,
                "capacity": fac.get("capacity_girls"),
                "room_types": fac.get("rooms"),
                "annual_fee": sourced(hostel_fees.get("annual_hostel_fee"), "InsightRural Hostel Database"),
                "mess_fee_monthly": sourced(hostel_fees.get("mess_fee_monthly"), "InsightRural Hostel Database"),
                "amenities": fac.get("amenities"),
                "food_type": hostel_entry.get("food"),
                "rules": hostel_entry.get("rules"),
            }

        hostel = {"boys_hostel": boys, "girls_hostel": girls}
    elif college.get("hostel_available"):
        hostel = {
            "boys_hostel": {"available": True},
            "girls_hostel": {"available": True},
        }

    # ── Approval ──────────────────────────────────────────────────────────
    approval = {
        "naac_grade": college.get("naac_grade"),
        "nba_accredited": college.get("nba_accredited"),
        "nba_accredited_branches": None,
        "aicte": True,  # All KEA colleges are AICTE approved
        "ugc": None,
    }

    # ── Assemble V2 record ────────────────────────────────────────────────
    v2 = {
        # Basic info
        "college_id": cid,
        "college_name": name,
        "short_name": None,
        "college_code": None,
        "established": college.get("established"),
        "ownership": college.get("type"),
        "autonomous": None,
        "affiliated_university": college.get("affiliation"),
        "website": college.get("website"),
        "email": college.get("email"),
        "phone": college.get("phone"),
        "principal_name": None,
        "highlights": college.get("highlights"),

        # Structured sub-models
        "approval": approval,
        "nirf": {"rank": None, "year": None, "source": None},
        "location": location,
        "branches": branches,
        "cutoffs": cutoffs,
        "fees": fees,
        "placements": placements,
        "hostel": hostel,
        "facilities": {
            "campus_area_acres": None,
            "library": None,
            "labs": None,
            "innovation_centre": None,
            "incubation_centre": None,
            "sports": None,
            "medical_facility": None,
            "auditorium": None,
            "transportation": None,
            "cafeteria": None,
            "wifi_campus": None,
        },
        "faculty": {
            "total_faculty": None,
            "phd_faculty": None,
            "student_faculty_ratio": None,
        },
        "admission": {
            "kcet": True,
            "comedk": None,
            "jee": None,
            "management_quota": None,
            "lateral_entry": None,
            "eligibility": None,
            "documents_required": None,
            "counselling_process": None,
        },
        "nearby": {
            "nearest_railway_station": None,
            "nearest_airport": None,
            "nearest_bus_stand": None,
        },
        "scholarship_ids": [],
        "sources": ["InsightRural Database"],
        "last_updated": NOW,

        # ── Legacy compatibility fields (used by existing recommend_colleges) ──
        "name": name,
        "type": college.get("type"),
        "location_legacy": college.get("location"),
        "district": college.get("district") or college.get("location"),
        "affiliation": college.get("affiliation"),
        "annual_fee": annual_fee,
        "fee_category": college.get("fee_category"),
        "total_seats": college.get("total_seats"),
        "hostel_available": college.get("hostel_available"),
        "cutoff_2024": cutoff_2024,
        "cutoff_trends": cutoff_trends,
        "placement_avg_lpa": college.get("placement_avg_lpa"),
        "placement_highest_lpa": college.get("placement_highest_lpa"),
        "top_recruiters": college.get("top_recruiters"),
        "naac_grade": college.get("naac_grade"),
        "nba_accredited": college.get("nba_accredited"),
        "google_maps_link": college.get("google_maps_link"),
    }

    return v2


def main():
    print("=" * 60)
    print("InsightRural - V1 -> V2 College Schema Migration")
    print("=" * 60)

    # Load all source files
    colleges = load("Production_Ready_Colleges.json")
    cutoffs = load("cutoff_dataset.json")
    hostels = load("hostels.json")
    fees = load("Fee.json")
    scholarships = load("scholarships.json")

    print(f"\n[INPUT]")
    print(f"  Colleges:      {len(colleges)}")
    print(f"  Cutoff entries: {len(cutoffs)}")
    print(f"  Hostels:       {len(hostels)}")
    print(f"  Fee categories: {len(fees)}")
    print(f"  Scholarships:  {len(scholarships)}")

    # Build lookup maps
    cutoff_map: Dict[str, Dict] = {}
    for c in cutoffs:
        cutoff_map[c.get("college_id", "")] = c

    hostel_map: Dict[str, Dict] = {}
    for h in hostels:
        key = (h.get("college", "") or h.get("name", "")).lower().strip()
        hostel_map[key] = h

    # Migrate each college
    v2_colleges = []
    for college in colleges:
        v2 = migrate_college(college, cutoff_map, hostel_map, fees)
        v2_colleges.append(v2)

    # Count field coverage
    filled = 0
    total = 0
    key_fields = [
        "established", "ownership", "website", "email", "phone",
    ]
    for c in v2_colleges:
        for f in key_fields:
            total += 1
            if c.get(f) is not None:
                filled += 1

    cutoff_years = set()
    for c in v2_colleges:
        cutoff_years.update(c.get("cutoffs", {}).keys())

    hostel_count = sum(1 for c in v2_colleges if c.get("hostel", {}).get("boys_hostel"))

    print(f"\n[OUTPUT]")
    print(f"  V2 colleges:   {len(v2_colleges)}")
    print(f"  Cutoff years:  {sorted(cutoff_years)}")
    print(f"  With hostel:   {hostel_count}")
    print(f"  Field coverage: {filled}/{total} basic fields ({100*filled//total}%)")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(v2_colleges, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Written to {OUTPUT_FILE}")
    print(f"     File size: {os.path.getsize(OUTPUT_FILE):,} bytes")
    print("=" * 60)


if __name__ == "__main__":
    main()
