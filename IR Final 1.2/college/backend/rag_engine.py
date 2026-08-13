# ==============================================================================
# InsightRural — Hybrid RAG Engine (BM25 + Dense + Cross-Encoder Reranking)
# ==============================================================================
# Upgraded from semantic-only search to production-grade hybrid retrieval.
#
# Pipeline:
#   1. BM25 sparse retrieval (keyword matching — catches exact terms)
#   2. Dense retrieval via ChromaDB (semantic similarity)
#   3. Reciprocal Rank Fusion (RRF) to merge both result sets
#   4. (Optional) Cross-encoder reranking for precision
#   5. Citation extraction for each result
#
# Usage:
#   engine = get_rag_engine()
#   results = engine.hybrid_search("best CSE colleges under 10000 rank")
#   prompt = engine.construct_strict_prompt(query, results)
# ==============================================================================

import os
import math
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

from core.logging import get_logger

logger = get_logger("RAG_Engine")


# ══════════════════════════════════════════════════════════════════════════════
# Search Result Model
# ══════════════════════════════════════════════════════════════════════════════

class SearchResult:
    """Structured search result with provenance tracking."""

    __slots__ = ("content", "source", "metadata", "relevance_score",
                 "bm25_rank", "dense_rank", "rerank_score")

    def __init__(
        self,
        content: str,
        source: str = "Official Database",
        metadata: Optional[Dict] = None,
        relevance_score: float = 0.0,
    ):
        self.content = content
        self.source = source
        self.metadata = metadata or {}
        self.relevance_score = relevance_score
        self.bm25_rank: Optional[int] = None
        self.dense_rank: Optional[int] = None
        self.rerank_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
            "relevance_score": round(self.relevance_score, 4),
        }


# ══════════════════════════════════════════════════════════════════════════════
# BM25 Index (Sparse Retrieval)
# ══════════════════════════════════════════════════════════════════════════════

class BM25Index:
    """
    Lightweight BM25 index built from ChromaDB collection documents.
    Catches exact keyword matches that embeddings miss (e.g., college names,
    specific fees, rank numbers).
    """

    def __init__(self):
        self.corpus: List[str] = []
        self.doc_metadata: List[Dict] = []
        self.doc_sources: List[str] = []
        self._bm25: Optional[Any] = None

    def build(self, documents: List[str], metadata: List[Dict], sources: List[str]):
        """Build BM25 index from documents."""
        if not BM25_AVAILABLE:
            logger.warning("rank_bm25 not installed — BM25 search disabled")
            return

        self.corpus = documents
        self.doc_metadata = metadata
        self.doc_sources = sources

        # Tokenize for BM25
        tokenized = [doc.lower().split() for doc in documents]
        self._bm25 = BM25Okapi(tokenized)
        logger.info("BM25 index built with %d documents", len(documents))

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search using BM25 scoring."""
        if not self._bm25 or not self.corpus:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)

        # Get top-k indices
        scored_indices = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        results = []
        for rank, (idx, score) in enumerate(scored_indices):
            if score > 0:  # Only include documents with non-zero BM25 score
                result = SearchResult(
                    content=self.corpus[idx],
                    source=self.doc_sources[idx] if idx < len(self.doc_sources) else "Official Database",
                    metadata=self.doc_metadata[idx] if idx < len(self.doc_metadata) else {},
                    relevance_score=float(score),
                )
                result.bm25_rank = rank + 1
                results.append(result)

        return results

    @property
    def is_built(self) -> bool:
        return self._bm25 is not None and len(self.corpus) > 0


# ══════════════════════════════════════════════════════════════════════════════
# Hybrid RAG Engine
# ══════════════════════════════════════════════════════════════════════════════

class StrictRAGEngine:
    """
    Production-grade Retrieval-Augmented Generation Engine.

    Combines BM25 (sparse) + ChromaDB (dense) retrieval with optional
    cross-encoder reranking for high-precision context retrieval.
    """

    # Collection names for intent-based routing
    COLLECTION_NAMES = [
        "official_brochures", "counseling_rules", "placement_reports",
        "scholarship_documents", "hostel_documents", "fee_circulars",
        "seat_matrix_documents", "loan_documents", "government_notifications",
    ]

    # Intent keywords for collection routing
    INTENT_KEYWORDS = {
        "scholarship_documents": [
            "scholarship", "snq", "ssp", "vidyasiri", "post matric", "stipend",
            "fee waiver", "free education", "minority", "sc scholarship", "st scholarship",
        ],
        "hostel_documents": [
            "hostel", "accommodation", "pg ", "paying guest", "room", "dormitory",
            "staying", "living", "bcm hostel", "mess", "food",
        ],
        "fee_circulars": [
            "fee", "cost", "tuition", "price", "afford", "expense", "how much",
            "annual fee", "semester", "fee structure", "fee concession",
        ],
        "placement_reports": [
            "placement", "salary", "package", "recruit", "job", "company",
            "campus hiring", "lpa", "crore", "average package", "highest package",
        ],
        "loan_documents": [
            "loan", "bank", "finance", "emi", "interest", "collateral", "vidyalakshmi",
            "sbi", "repayment", "subsidy", "ciss",
        ],
        "seat_matrix_documents": [
            "seat", "matrix", "intake", "vacancy", "available seat", "total seats",
        ],
        "counseling_rules": [
            "counseling", "counselling", "process", "document verification",
            "option entry", "allotment", "choice filling", "reporting",
            "kea process", "admission process", "web option",
        ],
    }

    FALLBACK_COLLECTIONS = [
        "official_brochures", "counseling_rules", "government_notifications",
    ]

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.client = None
        self.collections: Dict[str, Any] = {}
        self.embedding_fn = None
        self._bm25_index = BM25Index()
        self._cross_encoder = None

        if not CHROMADB_AVAILABLE:
            logger.error("chromadb not installed — RAG Engine disabled")
            return

        try:
            self.client = chromadb.PersistentClient(path=self.persist_dir)

            # Setup embeddings — must match what the persisted DB was built with.
            # Try the preferred function first; if the DB was built with a
            # different one ChromaDB raises an error, so fall back gracefully.
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=api_key, model_name="text-embedding-3-small"
                )
            else:
                self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )

            for name in self.COLLECTION_NAMES:
                try:
                    self.collections[name] = self.client.get_or_create_collection(
                        name, embedding_function=self.embedding_fn
                    )
                except Exception as emb_err:
                    # Embedding function conflict — the persisted collection
                    # was built with a different embedding.  Fall back to
                    # sentence_transformer (original) or no explicit fn.
                    logger.warning(
                        "Embedding conflict for %s, falling back: %s",
                        name, emb_err,
                    )
                    try:
                        fallback_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                            model_name="all-MiniLM-L6-v2"
                        )
                        self.collections[name] = self.client.get_or_create_collection(
                            name, embedding_function=fallback_fn
                        )
                        self.embedding_fn = fallback_fn
                    except Exception:
                        # Last resort: let ChromaDB use its persisted function
                        self.collections[name] = self.client.get_or_create_collection(name)

            # Build BM25 index from all collections
            self._build_bm25_index()

            # Load cross-encoder if available
            if CROSS_ENCODER_AVAILABLE:
                try:
                    self._cross_encoder = CrossEncoder(
                        "cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512
                    )
                    logger.info("Cross-encoder reranker loaded")
                except Exception as e:
                    logger.warning("Cross-encoder not loaded: %s", e)

            logger.info("StrictRAGEngine initialized (hybrid mode)")

        except Exception as e:
            logger.error("Failed to initialize ChromaDB: %s", e)
            self.client = None

    def _build_bm25_index(self):
        """Build BM25 index from all ChromaDB collection documents."""
        if not BM25_AVAILABLE or not self.client:
            return

        all_docs = []
        all_meta = []
        all_sources = []

        for name, coll in self.collections.items():
            try:
                result = coll.get(include=["documents", "metadatas"])
                if result and result.get("documents"):
                    docs = result["documents"]
                    metas = result.get("metadatas", [{}] * len(docs))
                    all_docs.extend(docs)
                    all_meta.extend(metas)
                    all_sources.extend(
                        [m.get("source_file", name) for m in metas]
                    )
            except Exception as e:
                logger.warning("Could not read collection %s for BM25: %s", name, e)

        if all_docs:
            self._bm25_index.build(all_docs, all_meta, all_sources)

    # ══════════════════════════════════════════════════════════════════════════
    # HYBRID SEARCH (BM25 + Dense + RRF + Reranking)
    # ══════════════════════════════════════════════════════════════════════════

    def hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 5,
        bm25_weight: float = 0.3,
        dense_weight: float = 0.7,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid search combining BM25 (sparse) and ChromaDB (dense).

        Pipeline:
          1. BM25 sparse search across all indexed documents
          2. Dense semantic search via ChromaDB (intent-routed)
          3. Reciprocal Rank Fusion (RRF) to merge results
          4. Cross-encoder reranking (if available and rerank=True)
          5. Return top-N with citation metadata

        Args:
            query: User search query
            filters: ChromaDB metadata filters (e.g., {"exam": "JEE"})
            n_results: Number of results to return
            bm25_weight: Weight for BM25 scores in RRF (0-1)
            dense_weight: Weight for dense scores in RRF (0-1)
            rerank: Whether to apply cross-encoder reranking

        Returns:
            List of result dicts with content, source, metadata, relevance_score
        """
        if not self.client:
            return []

        # ── Step 1: BM25 Sparse Search ────────────────────────────────────
        bm25_results = []
        if self._bm25_index.is_built:
            bm25_results = self._bm25_index.search(query, top_k=n_results * 2)

        # ── Step 2: Dense Semantic Search ─────────────────────────────────
        dense_results = self._dense_search(query, filters, n_results * 2)

        # ── Step 3: Reciprocal Rank Fusion ────────────────────────────────
        fused = self._reciprocal_rank_fusion(
            bm25_results, dense_results,
            bm25_weight=bm25_weight,
            dense_weight=dense_weight,
        )

        # ── Step 4: Cross-Encoder Reranking ───────────────────────────────
        if rerank and self._cross_encoder and fused:
            fused = self._rerank(query, fused, top_k=n_results)
        else:
            fused = fused[:n_results]

        # ── Step 5: Convert to dicts ──────────────────────────────────────
        return [r.to_dict() for r in fused]

    def _dense_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        n_results: int,
    ) -> List[SearchResult]:
        """ChromaDB dense semantic search with intent-based collection routing."""
        q_lower = query.lower()
        target_names = []

        # Intent-based collection routing
        for coll_name, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in q_lower for kw in keywords):
                target_names.append(coll_name)

        # Add fallback collections
        if not target_names:
            target_names = list(self.FALLBACK_COLLECTIONS)
        else:
            for fb in self.FALLBACK_COLLECTIONS:
                if fb not in target_names:
                    target_names.append(fb)

        seen_docs = set()
        results = []

        for name in target_names:
            coll = self.collections.get(name)
            if not coll:
                continue

            try:
                search_kwargs = {"query_texts": [query], "n_results": n_results}
                if filters:
                    search_kwargs["where"] = filters

                response = coll.query(**search_kwargs)

                if response and response.get("documents") and response["documents"][0]:
                    docs = response["documents"][0]
                    metas = response["metadatas"][0] if response.get("metadatas") else [{}] * len(docs)
                    dists = response["distances"][0] if response.get("distances") else [0] * len(docs)

                    for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
                        doc_hash = hash(doc)
                        if doc_hash in seen_docs:
                            continue

                        # Distance threshold for cosine: < 1.0 means relevant
                        if dist < 1.0:
                            seen_docs.add(doc_hash)
                            result = SearchResult(
                                content=doc,
                                source=meta.get("source_file", "Official Database"),
                                metadata=meta,
                                relevance_score=1.0 - (dist / 2.0),
                            )
                            result.dense_rank = rank + 1
                            results.append(result)

            except Exception as e:
                logger.error("Dense search error in %s: %s", name, e)

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results

    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[SearchResult],
        dense_results: List[SearchResult],
        bm25_weight: float = 0.3,
        dense_weight: float = 0.7,
        k: int = 60,
    ) -> List[SearchResult]:
        """
        Merge BM25 and dense results using Reciprocal Rank Fusion.

        RRF score = sum(weight / (k + rank)) for each retrieval system.
        k=60 is the standard RRF constant from the original paper.
        """
        doc_scores: Dict[str, float] = defaultdict(float)
        doc_objects: Dict[str, SearchResult] = {}

        # BM25 scores
        for rank, result in enumerate(bm25_results):
            doc_key = hash(result.content)
            rrf_score = bm25_weight / (k + rank + 1)
            doc_scores[doc_key] += rrf_score
            if doc_key not in doc_objects:
                doc_objects[doc_key] = result

        # Dense scores
        for rank, result in enumerate(dense_results):
            doc_key = hash(result.content)
            rrf_score = dense_weight / (k + rank + 1)
            doc_scores[doc_key] += rrf_score
            if doc_key not in doc_objects:
                doc_objects[doc_key] = result

        # Sort by fused score
        sorted_keys = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)

        fused = []
        for doc_key in sorted_keys:
            result = doc_objects[doc_key]
            result.relevance_score = doc_scores[doc_key]
            fused.append(result)

        return fused

    def _rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Rerank results using cross-encoder model."""
        if not self._cross_encoder or not results:
            return results[:top_k]

        try:
            pairs = [[query, r.content] for r in results[:20]]  # Rerank top 20
            scores = self._cross_encoder.predict(pairs)

            for result, score in zip(results[:20], scores):
                result.rerank_score = float(score)
                result.relevance_score = float(score)  # Override with rerank score

            results[:20] = sorted(
                results[:20], key=lambda x: x.relevance_score, reverse=True
            )
            return results[:top_k]

        except Exception as e:
            logger.warning("Cross-encoder reranking failed: %s", e)
            return results[:top_k]

    # ══════════════════════════════════════════════════════════════════════════
    # PROMPT CONSTRUCTION (Anti-Hallucination)
    # ══════════════════════════════════════════════════════════════════════════

    def construct_strict_prompt(
        self,
        user_query: str,
        retrieved_contexts: List[Dict[str, Any]],
    ) -> str:
        """
        Constructs the LLM prompt with strict anti-hallucination instructions
        and inline citation markers.
        """
        context_str = ""
        for i, ctx in enumerate(retrieved_contexts):
            source = ctx.get("source")
            content = ctx.get("content")
            score = ctx.get("relevance_score", 0)
            context_str += (
                f"\n--- Source [{i+1}]: {source} (relevance: {score:.2f}) ---\n"
                f"{content}\n"
            )

        prompt = f"""
You are the InsightRural AI Admission Consultant. You must act as an expert counselor for KCET, JEE, and NEET.

CRITICAL INSTRUCTIONS:
1. You MUST formulate your answer based ONLY on the provided Official Context below.
2. If the context does not contain the answer, you MUST state: "I do not have the official data to answer that specific query." Do NOT guess or make up ranks/fees.
3. You MUST cite your sources using the [Source Number] format inline when providing facts.
4. When providing numerical data (ranks, fees, percentages), verify it appears verbatim in the context.

OFFICIAL CONTEXT:
{context_str if context_str else "No official documents match this query."}

USER QUERY:
{user_query}

RESPONSE:
"""
        return prompt

    # ══════════════════════════════════════════════════════════════════════════
    # DOCUMENT INGESTION
    # ══════════════════════════════════════════════════════════════════════════

    def ingest_document(self, file_path: str, doc_type: str = "counseling_rules"):
        """Ingest a document into the appropriate ChromaDB collection."""
        if not self.client:
            logger.error("Cannot ingest — ChromaDB client not available")
            return

        coll = self.collections.get(doc_type)
        if not coll:
            logger.error("Unknown collection: %s", doc_type)
            return

        # Simple text extraction (PDF support via pdfplumber if available)
        text = ""
        if file_path.endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except ImportError:
                logger.warning("pdfplumber not available for PDF ingestion")
                return
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            logger.warning("No text extracted from %s", file_path)
            return

        # Chunk text into paragraphs
        chunks = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.strip()) > 50]
        if not chunks:
            chunks = [text[:2000]]

        # Add to collection
        ids = [f"{doc_type}_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        metadatas = [{"source_file": os.path.basename(file_path), "doc_type": doc_type}] * len(chunks)

        coll.upsert(documents=chunks, ids=ids, metadatas=metadatas)
        logger.info("Ingested %d chunks from %s into %s", len(chunks), file_path, doc_type)

        # Rebuild BM25 index
        self._build_bm25_index()

    def index_all(self):
        """Placeholder for backward compatibility."""
        return "RAG indexing must be triggered via ingest_all_data.py"


# ══════════════════════════════════════════════════════════════════════════════
# Singleton
# ══════════════════════════════════════════════════════════════════════════════

_engine_instance = None


def get_rag_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = StrictRAGEngine()
    return _engine_instance
