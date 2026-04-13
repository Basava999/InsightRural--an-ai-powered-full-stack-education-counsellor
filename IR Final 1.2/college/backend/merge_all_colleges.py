"""
merge_all_colleges.py
=====================
Merges College.json (228 colleges, master KEA list) with:
  - kea_colleges_complete.json  (enriched data: cutoffs, fees, website, placements)
  - cutoff_dataset.json         (multi-year cutoffs 2022-2024)
  - Fee.json                    (fee structure by category)

Produces: college_master.json  — the single unified dataset for RAG indexing.

Run: python merge_all_colleges.py
"""
import json, os, re
from difflib import SequenceMatcher

DATA_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data')

def load(fn):
    fp = os.path.join(DATA_DIR, fn)
    if not os.path.exists(fp):
        print(f"  [WARN] {fn} not found, skipping")
        return []
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)

def norm(s):
    """Normalise college name for fuzzy matching."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\b(of|and|the|college|engineering|technology|institute|&)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()

def similarity(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

# ── Fee structure by category ─────────────────────────────────────────────────
FEE_MAP = {
    "Government colleges":      {"gm": 44200,  "obc": 23590,  "sc_st": 0},
    "UVCE":                     {"gm": 49600,  "obc": 28990,  "sc_st": 0},
    "For Aided courses In Aided colleges": {"gm": 44200, "obc": 23590, "sc_st": 0},
    "Type-1 - Un-aided colleges including Minority & Un-Aided courses In Aided colleges":
                                {"gm": 112410, "obc": 88820,  "sc_st": 0},
    "Type-2 - Un-aided colleges including Minority & Un-Aided courses In Aided colleges":
                                {"gm": 121610, "obc": 98020,  "sc_st": 0},
    "Deemed / Private Universities": {"gm": 250000, "obc": 200000, "sc_st": 120000},
    "Type-1 - Un-aided colleges": {"gm": 112410, "obc": 88820, "sc_st": 0},
    "Type-2 - Un-aided colleges": {"gm": 121610, "obc": 98020, "sc_st": 0},
}

# ── Website lookup (name → website) for common colleges ─────────────────────
WEBSITE_LOOKUP = {
    "b m s college of engineering":         "https://bmsce.ac.in",
    "b.m.s. college of engineering":        "https://bmsce.ac.in",
    "r. v. college of engineering":         "https://rvce.edu.in",
    "r.v. college of engineering":          "https://rvce.edu.in",
    "m s ramaiah institute of technology":  "https://msrit.edu",
    "m.s. ramaiah institute of technology": "https://msrit.edu",
    "pes university":                       "https://pes.edu",
    "dayananda sagar college of engineering": "https://dayanandasagar.edu",
    "siddaganga institute of technology":   "https://sit.ac.in",
    "univesity of visvesvaraya college of engineering": "https://uvce.ac.in",
    "university visvesvaraya college of engineering":   "https://uvce.ac.in",
    "bangalore institute of technology":    "https://bit-bangalore.edu.in",
    "national institute of engineering":    "https://nie.ac.in",
    "the national institute of engineering":"https://nie.ac.in",
    "sdm college of engineering":           "https://sdmcet.ac.in",
    "malnad college of engineering":        "https://mcehassan.ac.in",
    "p e s college of engineering":         "https://pesce.ac.in",
    "k l e technological univeristy":       "https://kletech.ac.in",
    "k.l.e. technological university":      "https://kletech.ac.in",
    "k.l.s. gogte institute of technology": "https://git.edu",
    "sri jayachamarajendra college of engineering": "https://sjce.ac.in",
    "rns institute of technology":          "https://rnsit.ac.in",
    "new horizon college of engineering":   "https://newhorizonindia.edu",
    "m v j college of engineering":         "https://mvjce.edu.in",
    "nitte meenakshi institute of technology": "https://nmit.ac.in",
    "cmr institute of technology":          "https://cmrit.ac.in",
    "jss science and technology university":"https://jssstuniv.in",
    "dr. ambedkar institute of technology": "https://drait.edu",
    "dr.ambedkar institute of technology":  "https://drait.edu",
    "presidency university":                "https://presidencyuniversity.in",
    "sapthagiri college of engineering":    "https://sapthagiri.edu.in",
    "east west institute of technology":    "https://eastwestce.ac.in",
    "bms institute of technology":          "https://bmsit.ac.in",
    "oxford college of engineering":        "https://oxfordcollege.edu.in",
    "manipal institute of technology":      "https://manipal.edu/mit",
    "sir m.visvesvaraya institute of technology": "https://smvitm.ac.in",
    "dayananda sagar university":           "https://dsu.edu.in",
    "reva university":                      "https://reva.edu.in",
    "alliance university":                  "https://alliance.edu.in",
    "acharya institute of technology":      "https://acharya.ac.in",
    "kle dr. m.s. sheshgiri college":       "https://klescet.ac.in",
    "jain university":                      "https://jainuniversity.ac.in",
    "impact college of engineering":        "https://impact-education.in",
    "vidyavardhaka college of engineering": "https://vvce.ac.in",
    "p d a college of engineering":         "https://pdaengg.com",
    "basaveshwara engineering college":     "https://bec.ac.in",
    "b v v sangha basaveshwara engineering college": "https://bec.ac.in",
    "maratha mandal engineering college":   "https://mmec.ac.in",
    "tontadarya college of engineering":    "https://tontadarya.edu.in",
    "gogte institute of technology":        "https://git.edu",
    "bldeas vp dr.p.g. hallakatti college": "https://bldeacet.ac.in",
    "s j c institute of technology":        "https://sjcit.ac.in",
    "dr.t.thimmaiah institute of technology": "https://thimmaiah.edu.in",
    "kalpatharu institute of technology":   "https://kit.ac.in",
    "sri siddhartha institute of technology": "https://ssit.edu.in",
    "anjuman institute of technology":      "https://aitmbhatkal.ac.in",
    "r.t.e. soceity rural engineering college": "https://recgadag.ac.in",
    "sri taralabalu jagadguru institute":   "https://sjit.ac.in",
    "gurunanak dev engineering college":    "https://gndeckalburagi.ac.in",
    "bheemanna khandre institute of technology": "https://bkit.ac.in",
    "rao bahadur y.mahabaleswarappa engineering college": "https://rymec.ac.in",
    "hke society sir m visvesvaraya college": "https://hkescemsr.ac.in",
    "khaja bandanawaz university":          "https://kbnuniversity.edu.in",
    "tontadarya college of engineering":    "https://tontadarya.edu.in",
    "ghousia engineering college":          "https://ghousiaengg.ac.in",
    "hira sugar institute of technology":   "https://histmundargi.com",
}

# ── Load all source data ──────────────────────────────────────────────────────
print("[1] Loading source files...")
master_list   = load('College.json')           # 228 colleges (primary)
enriched_list = load('kea_colleges_complete.json')  # 40 enriched
cutoff_list   = load('cutoff_dataset.json')    # multi-year cutoffs

print(f"    College.json:              {len(master_list)} colleges")
print(f"    kea_colleges_complete.json:{len(enriched_list)} colleges")
print(f"    cutoff_dataset.json:       {len(cutoff_list)} colleges")

# Build lookup: normalised name → enriched record
enriched_by_name  = {norm(c['name']): c for c in enriched_list}
cutoff_by_name    = {norm(c['name']): c for c in cutoff_list}

def find_best_match(name, lookup, threshold=0.72):
    """Find best fuzzy match in lookup dict."""
    n = norm(name)
    if n in lookup:
        return lookup[n]
    best_score, best_key = 0, None
    for key in lookup:
        s = similarity(name, key)
        if s > best_score:
            best_score, best_key = s, key
    if best_score >= threshold and best_key:
        return lookup[best_key]
    return None

# ── Merge ────────────────────────────────────────────────────────────────────
print("\n[2] Merging records...")
merged = []
match_count = 0

for college in master_list:
    name    = college.get('correct_name') or college['name']
    cat     = college.get('fee_category', '')
    ctype   = college.get('type', '')

    # Base record from College.json
    rec = {
        "college_id":      college['college_id'],
        "name":            name,
        "type":            ctype,
        "location":        college.get('location', ''),
        "district":        college.get('district', ''),
        "affiliation":     college.get('affiliation', 'VTU'),
        "hostel_available":college.get('hostel_available', False),
        "branches":        college.get('branches', []),
        "fee_category":    cat,
        "annual_fee":      FEE_MAP.get(cat, {"gm": 112410, "obc": 88820, "sc_st": 0}),
    }

    # Merge enriched data (cutoffs, website, placements, etc.)
    enriched = find_best_match(name, enriched_by_name)
    if enriched:
        match_count += 1
        for key in ['cutoff_2024','website','phone','email','established','total_seats',
                    'nba_accredited','placement_avg_lpa','placement_highest_lpa',
                    'top_recruiters','google_maps_link','highlights','naac_grade']:
            if key in enriched:
                rec[key] = enriched[key]
        # Override annual_fee from enriched if available
        if 'annual_fee' in enriched:
            rec['annual_fee'] = enriched['annual_fee']

    # Merge cutoff dataset
    cutoff_match = find_best_match(name, cutoff_by_name)
    if cutoff_match:
        rec['cutoff_trends'] = cutoff_match.get('cutoffs', {})
        # If no cutoff_2024 from enriched, pull from cutoff dataset 2024
        if 'cutoff_2024' not in rec:
            c2024 = cutoff_match.get('cutoffs', {}).get('2024', {})
            if c2024:
                rec['cutoff_2024'] = c2024

    # Website from static lookup if not already set
    if 'website' not in rec:
        ws = WEBSITE_LOOKUP.get(norm(name))
        if ws:
            rec['website'] = ws

    # Ensure fee type label is readable
    rec['fee_type_label'] = (
        "Government" if "Government" in ctype else
        "Type-1 Unaided (~₹1.1L/year)" if "Type1" in ctype else
        "Type-2 Unaided (~₹1.2L/year)" if "Type2" in ctype else
        "Deemed/Private University"     if "Deemed" in ctype else
        "Aided (~₹44K/year)"
    )

    merged.append(rec)

print(f"    Merged: {len(merged)} colleges")
print(f"    Enriched match rate: {match_count}/{len(merged)} ({100*match_count//len(merged)}%)")

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(DATA_DIR, 'college_master.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)
print(f"\n[OK] Saved college_master.json ({len(merged)} colleges) → {out_path}")

# Quick stats
has_cutoff   = sum(1 for c in merged if c.get('cutoff_2024'))
has_website  = sum(1 for c in merged if c.get('website'))
has_placemnt = sum(1 for c in merged if c.get('placement_avg_lpa'))
print(f"     With cutoff data:     {has_cutoff}/{len(merged)}")
print(f"     With website:         {has_website}/{len(merged)}")  
print(f"     With placement data:  {has_placemnt}/{len(merged)}")
