"""
Layer 6: ChromaDB RAG integration.
Semantic search only — never used for college selection.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

COLLECTIONS = [
    "college_profiles", "cutoffs", "hostels", "scholarships",
    "placements", "counseling_rules", "official_brochures",
]


class ChromaRAGClient:
    """Wrapper around ChromaDB for semantic document search."""

    def __init__(self, chroma_dir: Path):
        self.chroma_dir = chroma_dir
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        try:
            import chromadb
            self.chroma_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.chroma_dir))
            self._available = True
            logger.info("ChromaDB initialized at %s", self.chroma_dir)
        except Exception as e:
            logger.warning("ChromaDB unavailable: %s", e)

    @property
    def available(self) -> bool:
        return self._available

    def search(
        self,
        query: str,
        collection: str = "official_brochures",
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            coll = self._client.get_or_create_collection(collection)
            kwargs = {"query_texts": [query], "n_results": n_results}
            if metadata_filter:
                kwargs["where"] = metadata_filter
            results = coll.query(**kwargs)
            docs = []
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                meta = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
                dist = results.get("distances", [[]])[0][i] if results.get("distances") else None
                docs.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "collection": collection,
                })
            return docs
        except Exception as e:
            logger.error("RAG search failed: %s", e)
            return []

    def search_multi_collection(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        n_results: int = 3,
    ) -> List[Dict[str, Any]]:
        cols = collections or ["official_brochures", "counseling_rules", "scholarship_documents"]
        all_results = []
        for col in cols:
            try:
                all_results.extend(self.search(query, col, n_results))
            except Exception:
                continue
        return sorted(all_results, key=lambda x: x.get("distance") or 999)[:n_results * 2]

    def index_document(
        self,
        collection: str,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> bool:
        if not self._available:
            return False
        try:
            coll = self._client.get_or_create_collection(collection)
            coll.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])
            return True
        except Exception as e:
            logger.error("Index failed: %s", e)
            return False
