import json
import os
from pathlib import Path
import yaml
import sys

# Add the current directory to path so we can import json_data_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from json_data_service import JSONDataService

def main():
    base_dir = Path(__file__).parent
    data_dir = base_dir.parent / "data"
    okf_dir = data_dir / "okf" / "colleges"
    okf_dir.mkdir(parents=True, exist_ok=True)
    
    # Load V2 json
    with open(data_dir / "colleges_v2.json", "r", encoding="utf-8") as f:
        colleges = json.load(f)
        
    print(f"Migrating {len(colleges)} colleges to OKF...")
    
    # Initialize the data service just to use its get_college_details method
    # Note: JSONDataService loads colleges_v2.json inside __init__
    jds = JSONDataService()
    
    for c in colleges:
        # We need a valid filename. Use college_id if available, else short_name, else name
        c_id = c.get("college_id") or c.get("short_name") or c.get("college_code")
        if not c_id:
            c_id = "".join(x for x in c.get("name", "unknown") if x.isalnum())
            
        filename = f"{c_id}.md".replace(" ", "_").lower()
        filepath = okf_dir / filename
        
        # 1. Generate YAML frontmatter (dump the entire college dict)
        frontmatter = yaml.dump(c, sort_keys=False, allow_unicode=True, default_flow_style=False)
        
        # 2. Generate Markdown body using our existing formatter
        # The existing formatter expects the name, so we'll pass the name
        md_body = jds.get_college_details(c.get("name", ""))
        
        # 3. Write OKF file
        content = f"---\n{frontmatter}---\n\n{md_body}\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Successfully generated {len(colleges)} OKF files in {okf_dir}")

if __name__ == "__main__":
    main()
