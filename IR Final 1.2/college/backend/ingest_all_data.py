import os
import json
import logging
from rag_engine import get_rag_engine
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Ingestion - %(levelname)s - %(message)s')

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def convert_to_documents(data, doc_type="general"):
    docs = []
    
    if doc_type == "college_master" and isinstance(data, list):
        for item in data:
            if not isinstance(item, dict): continue
            name = item.get("name", "Unknown College")
            content = f"College Profile: {name}\n"
            for k, v in item.items():
                if isinstance(v, (str, int, float, bool)):
                    content += f"{k.replace('_', ' ').title()}: {v}\n"
                elif isinstance(v, list) and v and isinstance(v[0], str):
                    content += f"{k.replace('_', ' ').title()}: {', '.join(v)}\n"
            
            docs.append({
                "content": content,
                "metadata": {
                    "source_file": "Production_Ready_Colleges.json",
                    "type": "college_profile",
                    "college_name": name
                }
            })
            
    elif doc_type == "scholarships" and isinstance(data, list):
        for item in data:
            if not isinstance(item, dict): continue
            name = item.get("name", "Unknown Scholarship")
            content = f"Scholarship Scheme: {name}\n"
            content += f"Provider: {item.get('provider', 'Government/Private')}\n"
            content += f"Benefits: {item.get('benefits', '')}\n"
            content += f"Eligibility: {json.dumps(item.get('eligibility', {}))}\n"
            content += f"Application Process: {item.get('application_process', '')}\n"
            
            docs.append({
                "content": content,
                "metadata": {
                    "source_file": "scholarships.json",
                    "type": "scholarship",
                    "scheme_name": name
                }
            })
            
    elif doc_type == "hostels" and isinstance(data, list):
        for item in data:
            if not isinstance(item, dict): continue
            name = item.get("college_name", item.get("name", "Unknown Hostel"))
            content = f"Hostel Information for: {name}\n"
            content += f"Fees: {item.get('fees_per_year', 'N/A')}\n"
            content += f"Facilities: {', '.join(item.get('facilities', []))}\n"
            content += f"Rules: {', '.join(item.get('rules', []))}\n"
            
            docs.append({
                "content": content,
                "metadata": {
                    "source_file": "hostels.json",
                    "type": "hostel",
                    "college_name": name
                }
            })
            
    elif doc_type == "education_loans" and isinstance(data, list):
        for item in data:
            if not isinstance(item, dict): continue
            bank = item.get("bank", "Unknown Bank")
            content = f"Education Loan Scheme: {bank}\n"
            content += f"Interest Rate: {item.get('interest_rate', 'N/A')}\n"
            content += f"Max Amount: {item.get('max_amount', 'N/A')}\n"
            content += f"Collateral: {item.get('collateral_required', 'N/A')}\n"
            
            docs.append({
                "content": content,
                "metadata": {
                    "source_file": "education_loans.json",
                    "type": "loan",
                    "bank_name": bank
                }
            })

    elif doc_type == "counseling_guide" and isinstance(data, dict):
        # Could be structured differently, simple flat dump
        for category, info in data.items():
            content = f"Counseling Guide - {category}:\n"
            content += json.dumps(info, indent=2)
            docs.append({
                "content": content,
                "metadata": {
                    "source_file": "counseling_guide.json",
                    "type": "counseling",
                    "category": category
                }
            })
            
    return docs

def ingest_data():
    logging.info("Starting Master Ingestion Pipeline...")
    engine = get_rag_engine()
    if not engine.client:
        logging.error("RAG Engine client not initialized. Cannot ingest.")
        return

    files_to_process = [
        ("Production_Ready_Colleges.json", "college_master", engine.collections["official_brochures"]),
        ("scholarships.json", "scholarships", engine.collections["scholarship_documents"]),
        ("hostels.json", "hostels", engine.collections["hostel_documents"]),
        ("education_loans.json", "education_loans", engine.collections["loan_documents"]),
        ("counseling_guide.json", "counseling_guide", engine.collections["counseling_rules"])
    ]

    total_ingested = 0
    for filename, doc_type, collection in files_to_process:
        logging.info(f"Processing {filename} into {collection.name}...")
        data = load_json(filename)
        if not data:
            logging.warning(f"File {filename} not found or empty.")
            continue
            
        docs = convert_to_documents(data, doc_type)
        if not docs:
            logging.warning(f"No documents generated from {filename}.")
            continue
            
        # Batch insert into ChromaDB
        batch_size = 100
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            ids = [f"{doc_type}_{int(time.time()*1000)}_{j}" for j in range(len(batch))]
            texts = [d["content"] for d in batch]
            metadatas = [d["metadata"] for d in batch]
            
            try:
                collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                total_ingested += len(batch)
                logging.info(f"  Inserted {len(batch)} chunks...")
            except Exception as e:
                logging.error(f"  Failed to insert batch: {e}")
                
    logging.info(f"Ingestion complete. Total documents added: {total_ingested}")

if __name__ == "__main__":
    ingest_data()
