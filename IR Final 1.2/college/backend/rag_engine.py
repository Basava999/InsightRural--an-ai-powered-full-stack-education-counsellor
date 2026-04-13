# InsightRural RAG Engine with ChromaDB
# This module handles vector database operations and semantic search

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not installed. Run: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Run: pip install sentence-transformers")


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine for InsightRural.
    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    """
    
    def __init__(self, data_dir: str = None, persist_dir: str = None):
        """
        Initialize the RAG Engine.
        
        Args:
            data_dir: Directory containing JSON data files
            persist_dir: Directory to persist ChromaDB data
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.persist_dir = persist_dir or os.path.join(os.path.dirname(__file__), 'vector_db')
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            print("[*] Loading embedding model (all-MiniLM-L6-v2)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[OK] Embedding model loaded!")
        else:
            self.embedding_model = None
            
        # Initialize ChromaDB with new v1.4 API
        if CHROMADB_AVAILABLE:
            try:
                # Use persistent client if directory is writable
                os.makedirs(self.persist_dir, exist_ok=True)
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                print(f"[OK] ChromaDB initialized (persistent: {self.persist_dir})")
            except Exception as e:
                # Fallback to ephemeral client
                self.client = chromadb.EphemeralClient()
                print(f"[*] ChromaDB using ephemeral storage: {e}")
        else:
            self.client = None
            
        # Collections for different data types
        self.collections = {}
        
    def _embedding_function(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for texts using SentenceTransformer (required by ChromaDB)."""
        if self.embedding_model is None:
            return [[0.0] * 384 for _ in texts]
        emb = self.embedding_model.encode(texts)
        if hasattr(emb, "tolist"):
            return emb.tolist()
        return list(emb)

    def _get_embedding_fn(self):
        """Create a ChromaDB-compatible embedding function wrapper."""
        engine = self
        try:
            # ChromaDB v1.4+ expects EmbeddingFunction with __call__ and name()
            from chromadb.api.types import EmbeddingFunction as ChromaEF
            class InsightRuralEmbedding(ChromaEF):
                def __call__(self, input):
                    return engine._embedding_function(input)
                def name(self):
                    return "insightrural-minilm"
            return InsightRuralEmbedding()
        except (ImportError, TypeError):
            # Older ChromaDB versions - just use lambda
            return lambda texts: engine._embedding_function(texts)

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection with our embedding function."""
        if not CHROMADB_AVAILABLE:
            return None
        if name not in self.collections:
            try:
                # Try with our custom embedding function first
                self.collections[name] = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=self._get_embedding_fn(),
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                # Conflict with persisted embedding - get without specifying one
                try:
                    self.collections[name] = self.client.get_or_create_collection(
                        name=name,
                        metadata={"hnsw:space": "cosine"}
                    )
                except Exception:
                    self.collections[name] = self.client.get_collection(name=name)
        return self.collections[name]
    
    def load_and_index_colleges(self) -> int:
        """Load and index all 228 colleges from college_master.json for semantic search."""
        collection = self._get_or_create_collection("colleges")
        if not collection:
            return 0

        # Try college_master.json first (228 colleges merged), fall back to kea_colleges_complete.json
        master_file   = os.path.join(self.data_dir, 'college_master.json')
        fallback_file = os.path.join(self.data_dir, 'kea_colleges_complete.json')
        college_file  = master_file if os.path.exists(master_file) else fallback_file

        if not os.path.exists(college_file):
            print(f"College data file not found: {college_file}")
            return 0

        with open(college_file, 'r', encoding='utf-8') as f:
            colleges = json.load(f)

        documents = []
        ids       = []
        metadatas = []

        for college in colleges:
            branches     = ', '.join(college.get('branches', []))
            cutoffs_text = self._format_cutoffs(college.get('cutoff_2024', {}))
            fees         = college.get('annual_fee', {})
            fee_label    = college.get('fee_type_label', '')

            # Rich document text — enables semantic search across ALL fields
            doc_text = f"""College: {college['name']}
Location: {college.get('location', 'N/A')}, {college.get('district', '')}
Type: {college.get('type', 'N/A')} | {fee_label}
Affiliation: {college.get('affiliation', 'VTU')}
NAAC Grade: {college.get('naac_grade', 'Not Available')}
Established: {college.get('established', 'N/A')}
Total Seats: {college.get('total_seats', 'N/A')}
NBA Accredited: {'Yes' if college.get('nba_accredited') else 'No'}
Branches Available: {branches}
Annual Fees — GM: ₹{fees.get('gm', 'N/A')}, OBC: ₹{fees.get('obc', 'N/A')}, SC/ST: ₹{fees.get('sc_st', 'N/A')}
2024 KCET Cutoffs: {cutoffs_text}
Average Placement: {college.get('placement_avg_lpa', 'N/A')} LPA | Highest: {college.get('placement_highest_lpa', 'N/A')} LPA
Top Recruiters: {', '.join(college.get('top_recruiters', []))}
Hostel: {'Available' if college.get('hostel_available') else 'Not Available'}
Website: {college.get('website', 'N/A')}
Phone: {college.get('phone', 'N/A')}
Email: {college.get('email', 'N/A')}
Google Maps: {college.get('google_maps_link', 'N/A')}
Highlights: {', '.join(college.get('highlights', []))}"""

            documents.append(doc_text.strip())
            ids.append(college['college_id'])
            metadatas.append({
                "name":       college['name'],
                "location":   college.get('location', ''),
                "type":       college.get('type', ''),
                "branches":   branches[:500],   # ChromaDB metadata has 512 char limit
                "has_hostel": college.get('hostel_available', False),
                "website":    college.get('website', ''),
                "naac":       college.get('naac_grade', ''),
            })

        # Batch insert (ChromaDB handles deduplication)
        collection.add(documents=documents, ids=ids, metadatas=metadatas)

        print(f"Indexed {len(documents)} colleges from {os.path.basename(college_file)}")
        return len(documents)
    
    def _format_cutoffs(self, cutoffs: Dict) -> str:
        """Format cutoff data into readable text."""
        if not cutoffs:
            return "Not available"
        
        parts = []
        for branch, ranks in cutoffs.items():
            if isinstance(ranks, dict):
                gm_rank = ranks.get('GM', 'N/A')
                parts.append(f"{branch}: GM-{gm_rank}")
        return '; '.join(parts[:5])  # Limit to top 5 branches
    
    def load_and_index_scholarships(self) -> int:
        """Load and index scholarship data."""
        collection = self._get_or_create_collection("scholarships")
        if not collection:
            return 0
            
        scholarship_file = os.path.join(self.data_dir, 'scholarships.json')
        if not os.path.exists(scholarship_file):
            return 0
            
        with open(scholarship_file, 'r', encoding='utf-8') as f:
            scholarships = json.load(f)
        
        documents = []
        ids = []
        metadatas = []
        
        for sch in scholarships:
            eligibility = sch.get('eligibility', {})
            benefits = sch.get('benefits', {})
            
            doc_text = f"""
            Scholarship: {sch['name']}
            Department: {sch.get('department', '')}
            For Category: {sch['category']}
            Income Limit: ₹{eligibility.get('income_limit', 'N/A')} per year
            Eligible Categories: {', '.join(eligibility.get('category', []))}
            Benefits: Fee Reimbursement: {benefits.get('full_fee_reimbursement', benefits.get('fee_reimbursement', 'N/A'))}
            Maintenance Allowance: Hosteller ₹{benefits.get('maintenance_allowance', {}).get('hosteller', 'N/A')}/month, Day Scholar ₹{benefits.get('maintenance_allowance', {}).get('day_scholar', 'N/A')}/month
            Application Portal: {sch.get('application_portal', '')}
            Deadline: {sch.get('deadline', 'Check portal')}
            Documents Required: {', '.join(sch.get('documents_required', [])[:5])}
            """
            
            documents.append(doc_text.strip())
            ids.append(sch['scholarship_id'])
            metadatas.append({
                "name": sch['name'],
                "category": sch['category'],
                "income_limit": eligibility.get('income_limit', 0)
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"Indexed {len(documents)} scholarships")
        return len(documents)
    
    def load_and_index_loans(self) -> int:
        """Load and index education loan data."""
        collection = self._get_or_create_collection("loans")
        if not collection:
            return 0
            
        loan_file = os.path.join(self.data_dir, 'education_loans.json')
        if not os.path.exists(loan_file):
            return 0
            
        with open(loan_file, 'r', encoding='utf-8') as f:
            loans = json.load(f)
        
        documents = []
        ids = []
        metadatas = []
        
        for loan in loans:
            interest = loan.get('interest_rate', {})
            amount = loan.get('loan_amount', {})
            
            doc_text = f"""
            Bank: {loan['bank']}
            Scheme: {loan['scheme_name']}
            Type: {loan['type']}
            Maximum Loan Amount: India ₹{amount.get('india_max', amount.get('max', 'N/A'))}, Abroad ₹{amount.get('abroad_max', 'N/A')}
            Interest Rate: Base {interest.get('base_rate', interest.get('range', 'N/A'))}%, Female Discount: {interest.get('female_discount', 'N/A')}%
            Collateral: {loan.get('collateral', {}).get('upto_7_5_lakhs', 'Check with bank')}
            Repayment: Moratorium {loan.get('repayment', {}).get('moratorium', 'N/A')}, Tenure: {loan.get('repayment', {}).get('tenure', 'N/A')}
            Subsidy: {loan.get('subsidy', {}).get('benefit', 'N/A')}
            Apply at: {loan.get('apply_at', '')}
            """
            
            documents.append(doc_text.strip())
            ids.append(loan['loan_id'])
            metadatas.append({
                "bank": loan['bank'],
                "scheme": loan['scheme_name'],
                "type": loan['type']
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"Indexed {len(documents)} loan schemes")
        return len(documents)
    
    def load_and_index_hostels(self) -> int:
        """Load and index hostel data."""
        collection = self._get_or_create_collection("hostels")
        if not collection:
            return 0
            
        hostel_file = os.path.join(self.data_dir, 'hostels.json')
        if not os.path.exists(hostel_file):
            return 0
            
        with open(hostel_file, 'r', encoding='utf-8') as f:
            hostels = json.load(f)
        
        documents = []
        ids = []
        metadatas = []
        
        for hostel in hostels:
            facilities = hostel.get('facilities', {})
            fees = hostel.get('fees', {})
            hostel_name = hostel.get('college', hostel.get('name', 'Unknown Hostel'))
            categories = ', '.join(hostel.get('category', [])) if isinstance(hostel.get('category'), list) else ''
            
            doc_text = f"""
            Hostel/College: {hostel_name}
            Location: {hostel.get('location', 'N/A')}
            Type: {hostel.get('type', 'N/A')}
            {f'For Categories: {categories}' if categories else ''}
            {f'Department: {hostel.get("department", "")}' if hostel.get('department') else ''}
            Boys Hostel: {'Yes' if facilities.get('boys_hostel') else 'No'}
            Girls Hostel: {'Yes' if facilities.get('girls_hostel') else 'No'}
            Room Types: {', '.join(facilities.get('rooms', facilities.get('typical_options', [])))}
            Amenities: {', '.join(facilities.get('amenities', []))}
            Annual Hostel Fee: ₹{fees.get('annual_hostel_fee', fees.get('total_yearly', 'Free' if 'BCM' in hostel.get('hostel_id', '') or 'SC' in hostel.get('hostel_id', '') else 'Varies'))}
            Monthly Mess Fee: ₹{fees.get('mess_fee_monthly', 'Included' if fees.get('food_included') else 'Varies')}
            Total Yearly Cost: ₹{fees.get('total_yearly', 'Free for eligible students' if 'BCM' in hostel.get('hostel_id', '') else 'Calculate based on room type')}
            Highlights: {', '.join(hostel.get('highlights', []))}
            """
            
            documents.append(doc_text.strip())
            ids.append(hostel['hostel_id'])
            metadatas.append({
                "college": hostel_name,
                "location": hostel.get('location', 'N/A'),
                "type": hostel.get('type', 'N/A')
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"Indexed {len(documents)} hostels")
        return len(documents)
    
    def load_and_index_counseling_guide(self) -> int:
        """Load and index counseling guide — steps, documents, FAQs."""
        collection = self._get_or_create_collection("counseling")
        if not collection:
            return 0

        guide_file = os.path.join(self.data_dir, 'counseling_guide.json')
        if not os.path.exists(guide_file):
            return 0

        with open(guide_file, 'r', encoding='utf-8') as f:
            guide = json.load(f)

        documents = []
        ids = []
        metadatas = []

        # Index engineering counseling steps
        eng = guide.get('engineering', {})
        for step in eng.get('steps', []):
            doc_text = f"""KEA Engineering Counseling Step {step['id']}: {step['title']}
{step['description']}
This is step {step['id']} of {len(eng.get('steps', []))} in the KCET engineering counseling process."""
            documents.append(doc_text)
            ids.append(f"eng_step_{step['id']}")
            metadatas.append({"type": "engineering_counseling", "step": step['id']})

        # Index medical counseling steps
        med = guide.get('medical', {})
        for step in med.get('steps', []):
            doc_text = f"""Medical (NEET) Counseling Step {step['id']}: {step['title']}
{step['description']}
This is step {step['id']} of {len(med.get('steps', []))} in the medical counseling process."""
            documents.append(doc_text)
            ids.append(f"med_step_{step['id']}")
            metadatas.append({"type": "medical_counseling", "step": step['id']})

        # Index all required documents
        for doc in guide.get('documents', []):
            doc_text = f"""Document for KEA Counseling: {doc['name']}
Details: {doc['details']}
Required: {'Yes - Mandatory' if doc['required'] else 'Conditional - Only if applicable'}"""
            documents.append(doc_text)
            ids.append(doc['id'])
            metadatas.append({"type": "document", "required": doc['required']})

        # Index FAQs
        for i, faq in enumerate(guide.get('faq', [])):
            doc_text = f"""KEA Counseling FAQ: {faq['q']}
Answer: {faq['a']}"""
            documents.append(doc_text)
            ids.append(f"faq_{i}")
            metadatas.append({"type": "faq"})

        if documents:
            collection.add(documents=documents, ids=ids, metadatas=metadatas)

        print(f"Indexed {len(documents)} counseling guide items")
        return len(documents)

    def load_and_index_cutoff_trends(self) -> int:
        """Load and index multi-year cutoff data (2022-2024) as trend documents."""
        collection = self._get_or_create_collection("cutoffs")
        if not collection:
            return 0

        cutoff_file = os.path.join(self.data_dir, 'cutoff_dataset.json')
        if not os.path.exists(cutoff_file):
            return 0

        with open(cutoff_file, 'r', encoding='utf-8') as f:
            colleges = json.load(f)

        documents = []
        ids = []
        metadatas = []

        for college in colleges:
            cutoffs = college.get('cutoffs', {})
            if not cutoffs:
                continue

            # Create one doc per college with all years of cutoff data
            years = sorted(cutoffs.keys(), reverse=True)
            cutoff_lines = []
            for year in years:
                for branch, cats in cutoffs[year].items():
                    if isinstance(cats, dict):
                        cat_str = ', '.join([f"{cat}: {rank}" for cat, rank in cats.items()])
                        cutoff_lines.append(f"  {year} {branch}: {cat_str}")

            if cutoff_lines:
                doc_text = f"""Cutoff Trends for {college['name']} ({college.get('location', '')})
Type: {college.get('type', '')}
{chr(10).join(cutoff_lines)}"""
                documents.append(doc_text)
                ids.append(f"cutoff_{college['college_id']}")
                metadatas.append({
                    "name": college['name'],
                    "location": college.get('location', ''),
                    "type": college.get('type', '')
                })

        if documents:
            collection.add(documents=documents, ids=ids, metadatas=metadatas)

        print(f"Indexed {len(documents)} cutoff trend documents")
        return len(documents)

    def load_and_index_fees(self) -> int:
        """Load and index fee structure data."""
        collection = self._get_or_create_collection("fees")
        if not collection:
            return 0

        fee_file = os.path.join(self.data_dir, 'Fee.json')
        if not os.path.exists(fee_file):
            return 0

        with open(fee_file, 'r', encoding='utf-8') as f:
            fees = json.load(f)

        documents = []
        ids = []
        metadatas = []

        for i, fee in enumerate(fees):
            doc_text = f"""Fee Structure: {fee['category']}
General Merit (GM) & Others above income limit: ₹{fee.get('gm_and_others_above_income_limit', 'N/A')}/year
SNQ Quota: ₹{fee.get('snq_quota', 'N/A')}/year
SC/ST Concession: ₹{fee.get('sc_st_concession', 0)}/year (Free for SC/ST)
Category-1 up to 2.5 Lakhs income: ₹{fee.get('cat1_upto_2_5_lakhs', 0)}/year (Free)
Others up to 10 Lakhs income: ₹{fee.get('others_upto_10_lakhs', 'N/A')}/year
Category-1 above 2.5 Lakhs income: ₹{fee.get('cat1_above_2_5_lakhs', 0)}/year"""
            documents.append(doc_text)
            ids.append(f"fee_{i}")
            metadatas.append({"category": fee['category']})

        if documents:
            collection.add(documents=documents, ids=ids, metadatas=metadatas)

        print(f"Indexed {len(documents)} fee structures")
        return len(documents)

    def index_all(self) -> Dict[str, int]:
        """Index all data sources."""
        results = {
            "colleges": self.load_and_index_colleges(),
            "scholarships": self.load_and_index_scholarships(),
            "loans": self.load_and_index_loans(),
            "hostels": self.load_and_index_hostels(),
            "counseling": self.load_and_index_counseling_guide(),
            "cutoffs": self.load_and_index_cutoff_trends(),
            "fees": self.load_and_index_fees()
        }
        print(f"\n[OK] Total indexed: {sum(results.values())} documents across {len(results)} collections")
        return results
    
    def search(self, query: str, collection_name: str = None, n_results: int = 8) -> List[Dict]:
        """
        Search across all collections for relevant information.
        Uses ChromaDB semantic search when available, falls back to TF-IDF.
        """
        if not CHROMADB_AVAILABLE:
            return self._fallback_search(query, collection_name)
        
        results = []
        all_collections = ["colleges", "scholarships", "loans", "hostels", "counseling", "cutoffs", "fees"]
        collections_to_search = [collection_name] if collection_name else all_collections
        
        for coll_name in collections_to_search:
            collection = self._get_or_create_collection(coll_name)
            if collection:
                try:
                    try:
                        search_results = collection.query(
                            query_texts=[query],
                            n_results=min(n_results, 3)  # 3 per collection max
                        )
                    except Exception:
                        query_emb = self._embedding_function([query])
                        search_results = collection.query(
                            query_embeddings=query_emb,
                            n_results=min(n_results, 3)
                        )
                    
                    if search_results and search_results.get('documents') and search_results['documents'][0]:
                        for i, doc in enumerate(search_results['documents'][0]):
                            dist = search_results.get('distances', [[]])[0][i] if search_results.get('distances') else 999
                            results.append({
                                "collection": coll_name,
                                "content": doc,
                                "metadata": search_results['metadatas'][0][i] if search_results.get('metadatas') else {},
                                "id": search_results['ids'][0][i] if search_results.get('ids') else None,
                                "distance": dist
                            })
                except Exception as e:
                    print(f"Error searching {coll_name}: {e}")
        
        # Sort by relevance (lower distance = more relevant)
        results.sort(key=lambda x: x.get('distance', 999))
        return results[:n_results]
    
    def _fallback_search(self, query: str, collection_name: str = None) -> List[Dict]:
        """Smart fallback with TF-IDF scoring when ChromaDB is not available."""
        results = []
        query_words = set(query.lower().split())
        # Remove common stop words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'in', 'for', 'to', 'of', 'and', 'or', 'can', 'i', 'how', 'my', 'me', 'are', 'at', 'with', 'do', 'get', 'about'}
        query_words = query_words - stop_words
        if not query_words:
            query_words = set(query.lower().split())  # Use all if only stop words

        def score_text(text):
            """Score text by keyword match count."""
            text_lower = text.lower()
            score = sum(2 if word in text_lower else 0 for word in query_words)
            # Bonus for exact phrase match
            if query.lower() in text_lower:
                score += 5
            return score

        # Search colleges
        if not collection_name or collection_name in ("colleges", None):
            college_file = os.path.join(self.data_dir, 'kea_colleges_complete.json')
            if os.path.exists(college_file):
                with open(college_file, 'r', encoding='utf-8') as f:
                    colleges = json.load(f)
                for college in colleges:
                    text = self._college_to_text(college)
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "colleges", "content": text, "metadata": {"name": college['name']}, "score": s})

        # Search scholarships
        if not collection_name or collection_name in ("scholarships", None):
            sch_file = os.path.join(self.data_dir, 'scholarships.json')
            if os.path.exists(sch_file):
                with open(sch_file, 'r', encoding='utf-8') as f:
                    scholarships = json.load(f)
                for sch in scholarships:
                    elig = sch.get('eligibility', {})
                    benefits = sch.get('benefits', {})
                    text = f"Scholarship: {sch['name']} | Department: {sch.get('department','')} | Category: {sch['category']} | Income Limit: ₹{elig.get('income_limit','N/A')} | Deadline: {sch.get('deadline','')} | Portal: {sch.get('application_portal','')} | Benefits: Fee Reimbursement={benefits.get('full_fee_reimbursement', benefits.get('fee_reimbursement','N/A'))} | Documents: {', '.join(sch.get('documents_required', [])[:5])}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "scholarships", "content": text, "metadata": {"name": sch['name']}, "score": s})

        # Search loans
        if not collection_name or collection_name in ("loans", None):
            loan_file = os.path.join(self.data_dir, 'education_loans.json')
            if os.path.exists(loan_file):
                with open(loan_file, 'r', encoding='utf-8') as f:
                    loans = json.load(f)
                for loan in loans:
                    amount = loan.get('loan_amount', {})
                    interest = loan.get('interest_rate', {})
                    text = f"Bank: {loan['bank']} | Scheme: {loan['scheme_name']} | Type: {loan['type']} | Max: ₹{amount.get('india_max', amount.get('max','N/A'))} | Rate: {interest.get('base_rate', interest.get('range','N/A'))}% | Collateral: {loan.get('collateral', {}).get('upto_7_5_lakhs', 'Check')} | Repayment: {loan.get('repayment', {}).get('tenure', 'N/A')} | Apply: {loan.get('apply_at','')}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "loans", "content": text, "metadata": {"bank": loan['bank']}, "score": s})

        # Search hostels
        if not collection_name or collection_name in ("hostels", None):
            hostel_file = os.path.join(self.data_dir, 'hostels.json')
            if os.path.exists(hostel_file):
                with open(hostel_file, 'r', encoding='utf-8') as f:
                    hostels = json.load(f)
                for hostel in hostels:
                    fees = hostel.get('fees', {})
                    hostel_name = hostel.get('college', hostel.get('name', 'Unknown'))
                    text = f"Hostel: {hostel_name} ({hostel.get('location', 'N/A')}) | Type: {hostel.get('type', 'N/A')} | Annual Fee: ₹{fees.get('annual_hostel_fee', fees.get('total_yearly', 'Varies'))} | Mess: ₹{fees.get('mess_fee_monthly', 'N/A')}/month"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "hostels", "content": text, "metadata": {"college": hostel_name}, "score": s})

        # Search counseling guide
        if not collection_name or collection_name in ("counseling", None):
            guide_file = os.path.join(self.data_dir, 'counseling_guide.json')
            if os.path.exists(guide_file):
                with open(guide_file, 'r', encoding='utf-8') as f:
                    guide = json.load(f)
                for step in guide.get('engineering', {}).get('steps', []):
                    text = f"KEA Engineering Counseling Step {step['id']}: {step['title']} - {step['description']}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "counseling", "content": text, "metadata": {"step": step['id']}, "score": s})
                for step in guide.get('medical', {}).get('steps', []):
                    text = f"Medical Counseling Step {step['id']}: {step['title']} - {step['description']}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "counseling", "content": text, "metadata": {"step": step['id']}, "score": s})
                for doc in guide.get('documents', []):
                    text = f"KEA Document: {doc['name']} - {doc['details']} | Required: {'Yes' if doc['required'] else 'If applicable'}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "counseling", "content": text, "metadata": {"type": "document"}, "score": s})
                for faq in guide.get('faq', []):
                    text = f"FAQ: {faq['q']} Answer: {faq['a']}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "counseling", "content": text, "metadata": {"type": "faq"}, "score": s})

        # Search fees
        if not collection_name or collection_name in ("fees", None):
            fee_file = os.path.join(self.data_dir, 'Fee.json')
            if os.path.exists(fee_file):
                with open(fee_file, 'r', encoding='utf-8') as f:
                    fees = json.load(f)
                for fee in fees:
                    text = f"Fee Structure: {fee['category']} | GM: ₹{fee.get('gm_and_others_above_income_limit', 'N/A')} | SC/ST: ₹{fee.get('sc_st_concession', 0)} | OBC <10L: ₹{fee.get('others_upto_10_lakhs', 'N/A')}"
                    s = score_text(text)
                    if s > 0:
                        results.append({"collection": "fees", "content": text, "metadata": {"category": fee['category']}, "score": s})

        # Sort by score descending, return top 8
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:8]
    
    def _college_to_text(self, college: Dict) -> str:
        """Convert college dict to rich searchable text."""
        branches = ', '.join(college.get('branches', []))
        cutoffs = college.get('cutoff_2024', {})
        cutoff_parts = []
        for branch, cats in cutoffs.items():
            if isinstance(cats, dict):
                cat_str = ', '.join([f"{c}: {r}" for c, r in cats.items()])
                cutoff_parts.append(f"{branch} ({cat_str})")
        cutoff_text = ' | '.join(cutoff_parts) if cutoff_parts else 'N/A'
        fees = college.get('annual_fee', {})
        fee_text = f"GM: ₹{fees.get('gm', 'N/A')}, OBC: ₹{fees.get('obc', 'N/A')}, SC/ST: ₹{fees.get('sc_st', 'N/A')}" if fees else 'N/A'
        highlights = ', '.join(college.get('highlights', []))
        return f"""College: {college['name']} | Location: {college['location']} | Type: {college['type']} | NAAC: {college.get('naac_grade', 'N/A')} | Branches: {branches} | Fees: {fee_text} | Cutoffs 2024: {cutoff_text} | Hostel: {'Yes' if college.get('hostel_available') else 'No'} | Highlights: {highlights}"""
    
    def get_colleges_by_rank(self, rank: int, branch: str, category: str = "GM") -> List[Dict]:
        """
        Get colleges where a student with given rank can get admission.
        
        Args:
            rank: Student's KCET rank
            branch: Preferred branch (CSE, ECE, etc.)
            category: Category (GM, OBC, SC, ST)
            
        Returns:
            List of eligible colleges sorted by cutoff
        """
        college_file = os.path.join(self.data_dir, 'kea_colleges_complete.json')
        if not os.path.exists(college_file):
            return []
            
        with open(college_file, 'r', encoding='utf-8') as f:
            colleges = json.load(f)
        
        eligible = []
        for college in colleges:
            cutoffs = college.get('cutoff_2024', {})
            branch_cutoff = cutoffs.get(branch, {})
            
            if isinstance(branch_cutoff, dict):
                category_cutoff = branch_cutoff.get(category, branch_cutoff.get('GM', float('inf')))
                if rank <= category_cutoff:
                    eligible.append({
                        "college": college['name'],
                        "location": college['location'],
                        "type": college['type'],
                        "cutoff": category_cutoff,
                        "fee": college.get('annual_fee', {}),
                        "branch": branch
                    })
        
        # Sort by cutoff (lower is more competitive)
        eligible.sort(key=lambda x: x['cutoff'])
        return eligible
    
    def get_eligible_scholarships(self, category: str, income: int) -> List[Dict]:
        """
        Get scholarships a student is eligible for.
        
        Args:
            category: Student's category (SC, ST, OBC, General)
            income: Annual family income
            
        Returns:
            List of eligible scholarships
        """
        sch_file = os.path.join(self.data_dir, 'scholarships.json')
        if not os.path.exists(sch_file):
            return []
            
        with open(sch_file, 'r', encoding='utf-8') as f:
            scholarships = json.load(f)
        
        eligible = []
        category_lower = category.lower()
        
        for sch in scholarships:
            eligibility = sch.get('eligibility', {})
            sch_categories = [c.lower() for c in eligibility.get('category', [])]
            income_limit = eligibility.get('income_limit', float('inf'))
            
            # Check category match
            category_match = False
            if category_lower in ['sc', 'scheduled caste']:
                category_match = 'sc' in sch_categories or 'scheduled caste' in sch_categories
            elif category_lower in ['st', 'scheduled tribe']:
                category_match = 'st' in sch_categories or 'scheduled tribe' in sch_categories
            elif category_lower in ['obc', 'category-1', 'category-2a', 'category-3a', 'category-3b']:
                category_match = any('obc' in c or 'category' in c for c in sch_categories)
            elif 'general' in category_lower or 'ews' in category_lower:
                category_match = 'general' in sch_categories or 'ews' in sch_categories
            elif 'minority' in category_lower:
                category_match = any('muslim' in c or 'christian' in c or 'minority' in category_lower for c in sch_categories)
            
            # Check income
            if category_match and income <= income_limit:
                eligible.append({
                    "name": sch['name'],
                    "category": sch['category'],
                    "benefits": sch.get('benefits', {}),
                    "deadline": sch.get('deadline', 'Check portal'),
                    "portal": sch.get('application_portal', '')
                })
        
        return eligible


# Singleton instance
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """Get or create the RAG engine singleton."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine


if __name__ == "__main__":
    # Comprehensive RAG engine test
    engine = RAGEngine()
    
    print("="*60)
    print("INSIGHTRURAL RAG ENGINE — FULL INDEX + SEARCH TEST")
    print("="*60)
    
    print("\n[1] Indexing ALL data...")
    results = engine.index_all()
    for collection, count in results.items():
        status = "OK" if count > 0 else "EMPTY"
        print(f"  [{status}] {collection}: {count} documents")
    
    print("\n[2] Testing college search for rank 5000, CSE, OBC...")
    colleges = engine.get_colleges_by_rank(5000, "CSE", "OBC")
    for c in colleges[:5]:
        print(f"  - {c['college']} (Cutoff: {c['cutoff']})")
    print(f"  Total eligible: {len(colleges)}")
    
    print("\n[3] Testing scholarship search for SC, income 2 lakhs...")
    scholarships = engine.get_eligible_scholarships("SC", 200000)
    for s in scholarships[:5]:
        print(f"  - {s['name']}")
    print(f"  Total eligible: {len(scholarships)}")
    
    print("\n[4] Testing semantic search queries...")
    test_queries = [
        "best college for CSE near Bangalore",
        "scholarships for SC students with low income",
        "education loan without collateral",
        "hostel near RVCE",
        "KEA counseling process steps",
        "fee structure for government colleges",
        "cutoff trends for UVCE CSE"
    ]
    for q in test_queries:
        results = engine.search(q, n_results=3)
        print(f"\n  Q: '{q}'")
        for r in results:
            content_preview = r['content'][:100].replace('\n', ' ').replace('₹', 'Rs.').strip()
            print(f"    [{r['collection']}] {content_preview}...")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)