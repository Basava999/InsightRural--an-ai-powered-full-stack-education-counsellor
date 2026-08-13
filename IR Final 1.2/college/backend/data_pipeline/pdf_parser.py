import pdfplumber
import pandas as pd
import logging
import re
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - PDF Parser - %(message)s')

class KEAPDFParser:
    """
    Parses complex tabular KEA Cutoff PDFs into a clean structured Pandas DataFrame.
    """
    def __init__(self):
        # KEA's standard naming convention for category mapping
        self.category_map = {
            "1G": "1G", "1K": "1K_Kannada", "1R": "1R_Rural",
            "2AG": "2A", "2AK": "2AK_Kannada", "2AR": "2AR_Rural",
            "2BG": "2B", "2BK": "2BK_Kannada", "2BR": "2BR_Rural",
            "3AG": "3A", "3AK": "3AK_Kannada", "3AR": "3AR_Rural",
            "3BG": "3B", "3BK": "3BK_Kannada", "3BR": "3BR_Rural",
            "GM": "GM", "GMK": "GM_Kannada", "GMR": "GM_Rural",
            "SCG": "SC", "SCK": "SC_Kannada", "SCR": "SC_Rural",
            "STG": "ST", "STK": "ST_Kannada", "STR": "ST_Rural",
            "SNQ": "SNQ"
        }

    def clean_rank(self, rank_str: str) -> int:
        """Cleans dirty rank strings (e.g. '15400 *' or '12K') into integers."""
        if not rank_str or pd.isna(rank_str) or str(rank_str).strip() == '-':
            return 999999 # Max rank representing 'No Seat'
        
        # Remove non-numeric characters except 'G' which denotes General sometimes
        clean_str = re.sub(r'[^0-9]', '', str(rank_str))
        try:
            return int(clean_str)
        except ValueError:
            return 999999

    def parse_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Extracts tables from the PDF using pdfplumber and returns a cleaned DataFrame.
        """
        if not os.path.exists(pdf_path):
            logging.error(f"File not found: {pdf_path}")
            return pd.DataFrame()

        logging.info(f"Extracting tables from {pdf_path}...")
        
        all_data = []
        current_college = "Unknown"
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # KEA PDFs are highly variable, use visual table extraction
                    tables = page.extract_tables()
                    
                    for table in tables:
                        # Skip empty tables
                        if not table:
                            continue
                            
                        # Normally the first row is headers (Categories)
                        headers = [str(h).replace('\n', '').strip() if h else '' for h in table[0]]
                        
                        # Find indices of categories we care about
                        cat_indices = {}
                        for i, h in enumerate(headers):
                            if h in self.category_map:
                                cat_indices[h] = i

                        # Iterate through rows
                        for row in table[1:]:
                            if not row:
                                continue
                                
                            # KEA often puts the College Name in a merged row that spans columns
                            row_text = " ".join([str(c) for c in row if c])
                            if "ENGINEERING" in row_text.upper() or "INSTITUTE" in row_text.upper():
                                current_college = row_text.split('-')[-1].strip() if '-' in row_text else row_text.strip()
                                continue
                                
                            branch_code = str(row[0]).strip() if row[0] else ""
                            
                            # If it looks like a valid branch row
                            if len(branch_code) > 1 and len(branch_code) <= 4:
                                
                                for cat_code, idx in cat_indices.items():
                                    if idx < len(row):
                                        rank_val = self.clean_rank(row[idx])
                                        
                                        if rank_val != 999999: # Only append actual cutoffs
                                            standardized_cat = self.category_map[cat_code]
                                            all_data.append({
                                                "college_name": current_college,
                                                "branch_code": branch_code,
                                                "category_raw": cat_code,
                                                "category_standardized": standardized_cat,
                                                "closing_rank": rank_val
                                            })
                                            
            df = pd.DataFrame(all_data)
            logging.info(f"Extracted {len(df)} cutoff records successfully.")
            return df
            
        except Exception as e:
            logging.error(f"Failed to parse PDF {pdf_path}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    parser = KEAPDFParser()
    # Assume the scraper downloaded a file named sample_cutoff.pdf
    sample_path = "../data/raw/sample_cutoff.pdf"
    
    # We create a dummy test if file doesn't exist to ensure code is structurally sound
    if not os.path.exists(sample_path):
        logging.warning("No sample PDF found. Scraper needs to run first.")
    else:
        df = parser.parse_pdf(sample_path)
        print(df.head(15))
