"""
Seed PostgreSQL from existing JSON datasets.
Run after applying database/schema.sql.

Usage:
  python database/seed/load_json_to_postgres.py
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT.parent / "data"
sys.path.insert(0, str(ROOT / "backend"))


def load_colleges():
    path = DATA_DIR / "Production_Ready_Colleges.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_sql_seed(output_path: Path):
    """Generate SQL INSERT statements from JSON (for manual migration)."""
    colleges = load_colleges()
    lines = ["-- Auto-generated seed from Production_Ready_Colleges.json", "BEGIN;", ""]

    for c in colleges:
        code = c.get("college_id", "").replace("'", "''")
        name = c.get("name", "").replace("'", "''")
        ctype = c.get("type", "Type1_Unaided")
        city = (c.get("location") or "").replace("'", "''")
        district = (c.get("district") or city).replace("'", "''")
        naac = c.get("naac_grade", "N/A")
        hostel = "TRUE" if c.get("hostel_available") else "FALSE"
        avg_lpa = c.get("placement_avg_lpa") or "NULL"
        seats = c.get("total_seats") or 0

        lines.append(
            f"INSERT INTO colleges (code, name, type, city, district, naac_grade, "
            f"hostel_available, placement_avg_lpa, total_seats) VALUES "
            f"('{code}', '{name}', '{ctype}', '{city}', '{district}', '{naac}', "
            f"{hostel}, {avg_lpa}, {seats}) ON CONFLICT (code) DO NOTHING;"
        )

    lines.extend(["", "COMMIT;"])
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(colleges)} college inserts → {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent / "seed_colleges.sql"
    generate_sql_seed(out)
