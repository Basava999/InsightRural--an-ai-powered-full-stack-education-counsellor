import os
import uuid
import logging
from typing import Dict, List, Any
import PyPDF2
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Ingestion - %(levelname)s - %(message)s')

class DocumentIngestionPipeline:
    """
    Handles extracting text from Official PDFs, chunking them into semantic blocks,
    and storing them in ChromaDB with dense metadata tagging to prevent hallucination.
    """
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Use OpenAI Embeddings (ensure OPENAI_API_KEY is in env)
        # Fallback to SentenceTransformers if no API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key, model_name="text-embedding-3-small"
            )
            logging.info("Initialized OpenAI Embeddings.")
        else:
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            logging.info("Initialized local SentenceTransformers Embeddings.")
            
        # Logical collections
        self.brochure_collection = self.client.get_or_create_collection(
            name="official_brochures", embedding_function=self.embedding_fn
        )
        self.counseling_collection = self.client.get_or_create_collection(
            name="counseling_rules", embedding_function=self.embedding_fn
        )
        
        # Semantic chunker
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts raw text from an official PDF document."""
        text = ""
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n\n"
        except Exception as e:
            logging.error(f"Failed to read PDF {pdf_path}: {e}")
        return text

    def ingest_document(self, pdf_path: str, collection_name: str, metadata: Dict[str, Any]):
        """
        Chunks the document and stores it in the designated collection with metadata.
        Metadata MUST include: exam, college_code (if applicable), year, doc_type.
        """
        if not os.path.exists(pdf_path):
            logging.error(f"Document not found: {pdf_path}")
            return

        logging.info(f"Ingesting {pdf_path} into {collection_name}...")
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        if not raw_text.strip():
            logging.warning(f"No text extracted from {pdf_path}. Possibly scanned image.")
            return

        chunks = self.text_splitter.split_text(raw_text)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{metadata.get('doc_type', 'doc')}_{uuid.uuid4().hex[:8]}_chunk_{i}"
            documents.append(chunk)
            
            # Embed the source URL/path into metadata for citation tracking
            chunk_metadata = metadata.copy()
            chunk_metadata["source_file"] = os.path.basename(pdf_path)
            chunk_metadata["chunk_index"] = i
            metadatas.append(chunk_metadata)
            
            ids.append(chunk_id)

        # Select target collection
        collection = self.brochure_collection if collection_name == "official_brochures" else self.counseling_collection
        
        # Batch insert
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logging.info(f"Successfully ingested {len(chunks)} chunks from {os.path.basename(pdf_path)}")

if __name__ == "__main__":
    # Example Usage
    pipeline = DocumentIngestionPipeline()
    # pipeline.ingest_document(
    #     pdf_path="data/josaa_2024_business_rules.pdf",
    #     collection_name="counseling_rules",
    #     metadata={"exam": "JEE", "year": 2024, "doc_type": "rules"}
    # )
