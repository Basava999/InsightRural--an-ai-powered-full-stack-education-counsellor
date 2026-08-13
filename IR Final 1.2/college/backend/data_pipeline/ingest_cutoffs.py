import os
import sys
import logging
from kea_scraper import KEAPDFScraper
from pdf_parser import KEAPDFParser
from document_etl import DocumentETLPipeline

# Adjust path to import FastAPI database models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Move up one more level to get to 'college' then into 'fastapi-backend'
college_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(college_dir, "fastapi-backend"))

try:
    from database import SessionLocal, Institution, Program, HistoricalCutoff
    from rag_engine import get_rag_engine
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Ingestion Pipeline - %(levelname)s - %(message)s')

class CutoffIngestionPipeline:
    """
    Orchestrator that ties the Scraper, Parser, and Database insertion together.
    """
    def __init__(self):
        self.scraper = KEAPDFScraper(download_dir="../data/raw")
        self.parser = KEAPDFParser()
        self.rag_engine = get_rag_engine()
        self.doc_etl = DocumentETLPipeline(self.rag_engine)
        self.db = SessionLocal()

    def run(self, year: int = 2024, round_no: int = 1):
        logging.info("--- Starting KEA Web Scraping & Ingestion Pipeline ---")
        
        # 1. Scrape and Download PDFs
        links = self.scraper.get_latest_cutoff_links()
        if not links:
            logging.warning("Could not automatically find cutoff links. Relying on manually downloaded PDFs in raw directory.")
            downloaded_files = [os.path.join("../data/raw", f) for f in os.listdir("../data/raw") if f.endswith('.pdf')]
        else:
            downloaded_files = self.scraper.download_pdfs(links)

        if not downloaded_files:
            logging.error("No PDFs available to process.")
            return

        for pdf_path in downloaded_files:
            logging.info(f"Processing {pdf_path}...")
            
            # 2. Unstructured Ingestion to ChromaDB (for AI Chat RAG)
            logging.info("Extracting raw text to ChromaDB for RAG...")
            self.doc_etl.process_and_ingest(
                file_path=pdf_path,
                authority="KEA",
                year=str(year),
                doc_type="seat_matrix_documents" # Usually Cutoff docs are searched similarly to seat matrices
            )
            
            # 3. Structured Parsing (for Math Engine)
            df = self.parser.parse_pdf(pdf_path)
            
            if df.empty:
                logging.warning(f"No structured table data found in {pdf_path}")
                continue

            # 4. Insert into PostgreSQL / SQLite
            self._insert_to_db(df, year, round_no)

        self.db.close()
        logging.info("--- Pipeline Complete ---")

    def _insert_to_db(self, df, year: int, round_no: int):
        """Bulk inserts the pandas DataFrame into the structured relational database."""
        logging.info(f"Inserting {len(df)} records into the database...")
        
        # In a real startup scenario, we map College Names to Institute IDs 
        # using fuzzy matching or pre-existing mapping tables.
        # For simplicity here, we ensure colleges and programs exist first.
        
        records_added = 0
        
        for index, row in df.iterrows():
            college_name = row['college_name']
            branch_code = row['branch_code']
            category = row['category_standardized']
            closing_rank = row['closing_rank']
            
            # Ensure Institution exists
            inst = self.db.query(Institution).filter(Institution.name == college_name).first()
            if not inst:
                inst = Institution(name=college_name, type="Unknown", tier=3)
                self.db.add(inst)
                self.db.flush() # Get the ID
                
            # Ensure Program exists
            prog = self.db.query(Program).filter(
                Program.institute_id == inst.id,
                Program.branch_code == branch_code
            ).first()
            
            if not prog:
                prog = Program(institute_id=inst.id, branch_code=branch_code, branch_name=branch_code) # Name default to code
                self.db.add(prog)
                self.db.flush()
                
            # Check if cutoff already exists to avoid duplicates
            existing_cutoff = self.db.query(HistoricalCutoff).filter(
                HistoricalCutoff.program_id == prog.id,
                HistoricalCutoff.year == year,
                HistoricalCutoff.round_no == round_no,
                HistoricalCutoff.category == category
            ).first()
            
            if not existing_cutoff:
                cutoff_record = HistoricalCutoff(
                    program_id=prog.id,
                    year=year,
                    round_no=round_no,
                    category=category,
                    closing_rank=closing_rank
                )
                self.db.add(cutoff_record)
                records_added += 1
                
        # Commit the transaction
        try:
            self.db.commit()
            logging.info(f"Successfully committed {records_added} new cutoff records.")
        except Exception as e:
            self.db.rollback()
            logging.error(f"Database insertion failed: {e}")

if __name__ == "__main__":
    pipeline = CutoffIngestionPipeline()
    pipeline.run()
