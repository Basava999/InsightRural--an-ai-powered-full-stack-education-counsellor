import os
import re
import logging
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
# Requires PyMuPDF (fitz) and LangChain text splitters for robust chunking
try:
    import fitz  # PyMuPDF
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    logging.warning("Please install PyMuPDF and langchain: pip install PyMuPDF langchain")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ETL Pipeline - %(levelname)s - %(message)s')

class DocumentETLPipeline:
    """
    Robust ETL Pipeline to ingest official admissions PDFs, circulars, and notifications
    into the StrictRAGEngine (ChromaDB) with rich semantic metadata.
    """
    
    def __init__(self, rag_engine):
        """
        Takes an instance of StrictRAGEngine.
        """
        self.rag_engine = rag_engine
        # The semantic chunker ensures paragraphs/tables aren't awkwardly broken
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def generate_document_id(self, content: str, source: str, index: int = 0) -> str:
        """Generates a stable, reproducible UUID based on content, source, and index."""
        unique_string = f"{source}-{index}-{content[:100]}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

    def clean_text(self, text: str) -> str:
        """Cleans extracted PDF text."""
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove weird characters but keep rupees and percentages
        text = re.sub(r'[^\x00-\x7F₹%–-]', ' ', text)
        return text.strip()

    def parse_pdf(self, file_path: str) -> str:
        """Extracts text from a PDF document robustly using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            full_text = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text.append(page.get_text("text"))
            return "\n\n".join(full_text)
        except Exception as e:
            logging.error(f"Failed to parse PDF {file_path}: {e}")
            return ""

    def determine_collection(self, content: str, filename: str) -> str:
        """Auto-routes the document to the correct ChromaDB collection based on keywords."""
        text = (content[:1000] + " " + filename).lower()
        
        if any(w in text for w in ["scholarship", "snq", "ssp", "waiver"]):
            return "scholarship_documents"
        elif any(w in text for w in ["hostel", "accommodation", "pg"]):
            return "hostel_documents"
        elif any(w in text for w in ["fee structure", "tuition", "cost", "concession"]):
            return "fee_circulars"
        elif any(w in text for w in ["placement", "highest package", "lpa"]):
            return "placement_reports"
        elif any(w in text for w in ["loan", "bank", "interest", "vidyalakshmi"]):
            return "loan_documents"
        elif any(w in text for w in ["seat matrix", "intake"]):
            return "seat_matrix_documents"
        elif any(w in text for w in ["counseling", "counselling", "allotment", "option entry"]):
            return "counseling_rules"
        else:
            return "official_brochures"

    def process_and_ingest(
        self, 
        file_path: str, 
        authority: str = "KEA", 
        year: str = "2024",
        doc_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        The core ETL function: Download -> Parse -> Chunk -> Tag -> Embed -> Store.
        """
        logging.info(f"Processing document: {file_path}")
        
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return {"success": False, "error": "File not found"}

        # 1. Parse
        if file_path.endswith('.pdf'):
            raw_text = self.parse_pdf(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()

        clean_content = self.clean_text(raw_text)
        if not clean_content:
            return {"success": False, "error": "No text extracted"}

        # 2. Determine target collection
        collection_name = doc_type if doc_type else self.determine_collection(clean_content, file_path)
        
        # 3. Chunking
        chunks = self.text_splitter.split_text(clean_content)
        logging.info(f"Split {file_path} into {len(chunks)} semantic chunks.")

        # 4. Tagging (Metadata)
        documents = []
        metadatas = []
        ids = []

        filename = os.path.basename(file_path)
        upload_date = datetime.now().isoformat()

        for idx, chunk in enumerate(chunks):
            chunk_id = self.generate_document_id(chunk, filename, idx)
            
            metadata = {
                "source_file": filename,
                "authority": authority,
                "year": year,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "ingested_at": upload_date,
                "collection_route": collection_name,
                "validity": "verified_official"
            }
            
            documents.append(chunk)
            metadatas.append(metadata)
            ids.append(chunk_id)

        # 5. Store / Embed via ChromaDB Engine
        if not self.rag_engine or not self.rag_engine.client:
            logging.error("RAG Engine client not initialized. Cannot ingest.")
            return {"success": False, "error": "DB Client Offline"}

        try:
            collection = self.rag_engine.collections.get(collection_name)
            if not collection:
                # Fallback
                collection = self.rag_engine.collections.get("official_brochures")
                
            # Upsert into ChromaDB
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Successfully ingested {len(chunks)} chunks into {collection.name}")
            return {"success": True, "chunks_processed": len(chunks), "collection": collection.name}
            
        except Exception as e:
            logging.error(f"Failed to upsert to ChromaDB: {e}")
            return {"success": False, "error": str(e)}

# Example Usage:
# if __name__ == "__main__":
#     from rag_engine import get_rag_engine
#     engine = get_rag_engine()
#     etl = DocumentETLPipeline(engine)
#     etl.process_and_ingest("./data/raw/KEA_Fee_Structure_2024.pdf", authority="KEA", year="2024")
