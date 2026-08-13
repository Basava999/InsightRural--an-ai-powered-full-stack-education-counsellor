# ==============================================================================
# InsightRural — Ollama + LLaMA 3 Local AI Pipeline
# ==============================================================================
# Architecture (as explained in project design):
#
#   Student Query
#       ↓
#   Flask fetches stored student profile (name, KCET rank, category,
#       income, branch, location, budget, hostel_needed, etc.)
#       ↓
#   RAG Engine → ChromaDB cosine similarity → top-8 relevant docs
#   (college data, cutoffs, scholarships, hostels, fees, counseling)
#       ↓
#   Prompt Builder → packages profile + RAG context + history into
#       a single structured prompt block (JSON context injection)
#       ↓
#   Ollama local server (llama3) → Transformer decoder reasoning
#       → generates personalized guidance
#       ↓
#   Token-by-token SSE stream → Frontend Chat Interface
#
# Offline-capable, private, no API keys needed.
# All student data stays on-device.
# ==============================================================================

import json
import os
import time
from core.logging import get_logger

logger = get_logger("llm_service")
import httpx
from typing import Generator, Dict, Any, Optional, List

# JSON-first data service (Priority 1 in data hierarchy)
try:
    from json_data_service import get_json_data_service, JSONDataService
    JSON_DATA_AVAILABLE = True
except ImportError as e:
    logger.warning("JSON Data Service not available: %s", e)
    JSON_DATA_AVAILABLE = False

# KEA Seat Allotment Simulation Engine (ML + Rules)
try:
    from kea_allotment_engine import get_kea_engine, KEASeatAllotmentEngine
    KEA_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning("KEA Allotment Engine not available: %s", e)
    KEA_ENGINE_AVAILABLE = False

# ── Ollama Config ─────────────────────────────────────────────────────────────
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST",  "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# ── Groq Cloud Config (fast fallback) ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# ── System Persona ────────────────────────────────────────────────────────────
# Removed: COUNSELOR_SYSTEM_PROMPT is now exclusively imported from prompt_templates.py




class OllamaService:
    """
    Communicates with a locally-running Ollama server.
    Supports both streaming and non-streaming generation via /api/chat.
    """

    def __init__(self, host: str = None, model: str = None):
        self.host  = (host or OLLAMA_HOST).rstrip("/")
        self.model = model or OLLAMA_MODEL
        self.available = False
        self._check_health()

    def _check_health(self):
        """Check if Ollama is running and the model is available."""
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Accept both "llama3" and "llama3:latest" style names
                model_base = self.model.split(":")[0]
                if any(model_base in m for m in models):
                    self.available = True
                    logger.info("Ollama ready | model: %s at %s", self.model, self.host)
                else:
                    # Model not pulled yet — still mark as available so we can try
                    self.available = True
                    logger.info("Ollama running at %s", self.host)
                    logger.warning("Model '%s' not found in pulled models: %s", self.model, models)
                    logger.info("Run: ollama pull %s", self.model)
            else:
                logger.warning("Ollama returned HTTP %s", r.status_code)
        except Exception as e:
            logger.warning("Ollama not reachable at %s: %s", self.host, e)
            logger.info("Start Ollama with: ollama serve")
            self.available = False

    def generate(self, messages: List[Dict], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Optional[str]:
        """Non-streaming generation via /api/chat."""
        if not self.available:
            return None
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            r = httpx.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=120.0
            )
            r.raise_for_status()
            data = r.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error("Ollama generate error: %s", e)
            return None

    def stream(self, messages: List[Dict], temperature: float = 0.7,
               max_tokens: int = 2048) -> Generator[str, None, None]:
        """Token-by-token streaming via /api/chat with stream=True."""
        if not self.available:
            return
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        try:
            with httpx.stream(
                "POST",
                f"{self.host}/api/chat",
                json=payload,
                timeout=120.0
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done"):
                            break
                    except (json.JSONDecodeError, KeyError):
                        pass
        except Exception as e:
            logger.error("Ollama stream error: %s", e)


# ==============================================================================
# GROQ CLOUD SERVICE — fast cloud LLM fallback
# ==============================================================================
class GroqService:
    """
    Fast cloud LLM via Groq API (OpenAI-compatible).
    Provides near-instant responses (1-3 seconds) using llama-3.3-70b-versatile.
    Used as PRIMARY LLM; Ollama is the offline fallback.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_MODEL
        self.available = bool(self.api_key)
        if self.available:
            logger.info("Groq cloud LLM ready | model: %s", self.model)
        else:
            logger.warning("Groq API key not set -- cloud LLM disabled")

    def generate(self, messages: List[Dict], temperature: float = 0.7,
                 max_tokens: int = 2048) -> Optional[str]:
        """Non-streaming generation via Groq API."""
        if not self.available:
            return None
        try:
            r = httpx.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("Groq generate error: %s", e)
            return None

    def stream(self, messages: List[Dict], temperature: float = 0.7,
               max_tokens: int = 2048) -> Generator[str, None, None]:
        """Token-by-token streaming via Groq API (SSE)."""
        if not self.available:
            return
        try:
            with httpx.stream(
                "POST",
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass
        except Exception as e:
            logger.error("Groq stream error: %s", e)


# ==============================================================================
# RAG FALLBACK — text response from ChromaDB when Ollama is offline
# ==============================================================================
class RAGFallback:
    """Generates a data-driven response using only the RAG engine (no LLM needed)."""

    def __init__(self, rag_engine=None):
        self.rag = rag_engine

    def generate(self, query: str) -> str:
        if not self.rag:
            return self._static_response(query)
        try:
            results = self.rag.search(query, n_results=5)
            if not results:
                return self._static_response(query)
            sections = []
            for r in results[:4]:
                content = r.get("content", "")[:500]
                collection = r.get("collection", "").upper()
                if content:
                    sections.append(f"**[{collection}]** {content}")
            body = "\n\n".join(sections)
            return (
                f"Based on the InsightRural database:\n\n{body}\n\n"
                "---\n💡 **Tip:** Start Ollama (`ollama serve`) for full personalized guidance. "
                "For now I've pulled the most relevant data from the knowledge base above."
            )
        except Exception:
            return self._static_response(query)

    def _static_response(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["cutoff", "rank", "seat", "college"]):
            return (
                "**KCET Cutoff Quick Reference (2024)**\n\n"
                "• **Top Government colleges**: GM **850–3,000** | SC/ST up to 15,000\n"
                "• **Top Tier-1 Private colleges**: GM **600–5,000** | SC/ST up to 25,000\n"
                "• **Mid-Tier Private colleges**: GM **3,000–15,000** | SC/ST up to 40,000\n\n"
                "📊 Use the **College Predictor** for your exact rank analysis!"
            )
        if any(w in q for w in ["scholarship", "sc", "st", "obc", "fee waiver"]):
            return (
                "**Scholarship Quick Reference**\n\n"
                "• **SC/ST Students**: Fee completely **FREE** at Government & Aided colleges\n"
                "• **Post-Matric Scholarship** covers Type-1 fees up to ₹75,000/year\n"
                "  Apply: ssp.postmatric.karnataka.gov.in\n"
                "• **OBC Students**: Fee concession ₹23,590/year at Government colleges\n"
                "• **Vidya Lakshmi** education loans: vidyalakshmi.co.in"
            )
        return (
            "Hello! I'm InsightRural AI, your Karnataka college admission guide.\n\n"
            "I can help you with:\n"
            "• 🎓 **College predictions** based on your KCET rank\n"
            "• 💰 **Scholarship information** (SC/ST/OBC/EWS schemes)\n"
            "• 🏛️ **College details** for all 228 KEA colleges\n"
            "• 📚 **Career guidance** and branch selection\n"
            "• 🏦 **Education loan** guidance\n\n"
            "⚠️ *The local AI engine (Ollama) is currently offline. "
            "Start it with `ollama serve` for full personalized responses.*"
        )


# ==============================================================================
# INSIGHT RURAL COUNSELOR — main pipeline orchestrator
# ==============================================================================
class InsightRuralCounselor:
    """
    The heart of InsightRural's AI pipeline:

    Flow for every query:
    1. Fetch student profile (stored per session)
    2. RAG → ChromaDB cosine similarity → top-8 domain-specific docs
    3. Build structured prompt: system + profile JSON + RAG context + history
    4. LLM reasons over the complete context
    5. Stream response token-by-token back to frontend

    Fallback chain: Groq (fast cloud) → Ollama (local) → RAG-only text
    """

    def __init__(self):
        self.groq   = GroqService()
        self.ollama = OllamaService()
        self.rag    = None
        self.fallback = None
        self.json_data = None
        self.kea_engine = None
        self.last_model_used = "InsightRural AI"
        self._init_json_data()
        self._init_kea_engine()
        self._init_rag()

    def _init_json_data(self):
        """Initialize the JSON-first data service (Priority 1)."""
        try:
            if JSON_DATA_AVAILABLE:
                self.json_data = get_json_data_service()
                logger.info("InsightRuralCounselor: JSON Data Service connected (Priority 1)")
            else:
                logger.warning("JSON Data Service not available")
        except Exception as e:
            logger.warning("JSON Data Service init failed: %s", e)
            self.json_data = None

    def _init_kea_engine(self):
        """Initialize the KEA Seat Allotment Simulation Engine."""
        try:
            if KEA_ENGINE_AVAILABLE:
                self.kea_engine = get_kea_engine()
                logger.info("InsightRuralCounselor: KEA Allotment Engine connected (ML + Rules)")
            else:
                logger.warning("KEA Allotment Engine not available")
        except Exception as e:
            logger.warning("KEA Engine init failed: %s", e)
            self.kea_engine = None

    def _init_rag(self):
        """Initialize the strict ChromaDB RAG engine."""
        try:
            from rag_engine import get_rag_engine
            self.rag = get_rag_engine()
            self.fallback = RAGFallback(self.rag)
            logger.info("InsightRuralCounselor: Strict ChromaDB RAG engine connected")
        except Exception as e:
            logger.warning("RAG engine not available: %s", e)
            self.fallback = RAGFallback(None)

    # ── Priority 1: JSON Data Context ────────────────────────────────────────

    def _get_json_context(self, query: str, session_profile: Optional[Dict] = None) -> str:
        """
        PRIORITY 1: Query structured JSON databases for exact data.
        Returns formatted context with verified database values.
        These values must NEVER be modified by the LLM.
        """
        if not self.json_data:
            return ""
        try:
            return self.json_data.build_context_for_query(query, session_profile or {})
        except Exception as e:
            logger.error("JSON context fetch failed: %s", e)
            return ""

    def _get_kea_simulation_context(self, query: str, session_profile: Optional[Dict] = None) -> str:
        """
        Run KEA seat allotment simulation when query involves rank-based prediction.
        Returns ML-powered prediction results formatted for LLM context.
        """
        if not self.kea_engine:
            return ""

        profile = session_profile or {}
        query_lower = query.lower()

        # Only run simulation for prediction/recommendation queries
        prediction_kw = ["predict", "chance", "college", "rank", "cutoff",
                        "recommend", "allotment", "safe", "moderate", "ambitious",
                        "which college", "get into", "option entry"]
        if not any(kw in query_lower for kw in prediction_kw):
            return ""

        # Extract rank from profile or query
        rank = profile.get("kcet_rank") or profile.get("rank")
        if rank:
            try:
                rank = int(rank)
            except (ValueError, TypeError):
                rank = None

        if not rank:
            import re
            rank_match = re.search(r'rank\s*(?:is\s*)?(?:of\s*)?(\d+)', query_lower)
            if rank_match:
                rank = int(rank_match.group(1))
            else:
                num_match = re.search(r'\b(\d{3,6})\b', query_lower)
                if num_match:
                    rank = int(num_match.group(1))

        if not rank:
            return ""

        category = profile.get("category", "GM")
        branch = profile.get("branch") or "CSE"
        if isinstance(branch, list):
            branch = branch[0] if branch else "CSE"

        try:
            return self.kea_engine.build_chat_context(
                rank=rank,
                category=category,
                branch=branch,
                rural_quota=profile.get("rural_quota", False),
                kannada_medium=profile.get("kannada_medium", False),
                hk_371j=profile.get("371j_status", False),
                hostel_required=profile.get("hostel_needed", False),
                budget=int(profile.get("budget", 0)) if profile.get("budget") else 0,
            )
        except Exception as e:
            logger.error("KEA simulation context failed: %s", e)
            return ""

    # ── Priority 2: RAG Context Retrieval ─────────────────────────────────────

    def _get_rag_context(self, query: str) -> str:
        """
        PRIORITY 2: Query ChromaDB using strict semantic hybrid search.
        Returns the top results formatted as a strict context block.
        Only used for information NOT available in the JSON database.
        """
        if not self.rag:
            return ""
        try:
            results = self.rag.hybrid_search(query, n_results=5)
            if not results:
                return ""
            parts = []
            for i, r in enumerate(results):
                content = r.get("content", "")[:800]
                source = r.get("source", "Official Source")
                if content:
                    parts.append(f"--- Source [{i+1}]: {source} ---\n{content}")
            return "\n\n".join(parts)
        except Exception as e:
            logger.error("RAG context fetch failed: %s", e)
            return ""

    # ── Response Validation Layer ─────────────────────────────────────────────

    def _validate_sentence(self, sentence: str, rag_context: str) -> str:
        """Removes sentences containing unsupported numeric values (hallucinations)."""
        import re
        if len(sentence.strip()) < 5:
            return sentence
            
        norm_context = rag_context.replace(",", "") if rag_context else ""
        numbers = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', sentence)
        
        for num_str in numbers:
            try:
                val = float(num_str.replace(",", ""))
                if val <= 10:
                    continue # Ignore small lists/counts
                if 2000 <= val <= 2050 and len(num_str.replace(",", "")) == 4:
                    continue # Ignore recent years
            except ValueError:
                continue
                
            norm_num = num_str.replace(",", "")
            if norm_num not in norm_context:
                return "Verified information is currently unavailable.\n"
                
        return sentence

    def _validated_stream(self, stream_gen, rag_context: str) -> Generator[str, None, None]:
        """Sentence-buffers a stream and validates each sentence against RAG context."""
        import re
        buffer = ""
        for token in stream_gen:
            buffer += token
            while True:
                # Find sentence boundary (. ! ? followed by space/newline, or just newline)
                match = re.search(r'([.!?]\s+|\n+)', buffer)
                if not match:
                    break
                
                idx = match.end()
                sentence = buffer[:idx]
                buffer = buffer[idx:]
                
                yield self._validate_sentence(sentence, rag_context)
                
        if buffer:
            yield self._validate_sentence(buffer, rag_context)

    # ── Prompt Builder ────────────────────────────────────────────────────────

    def _build_messages(
        self,
        query: str,
        rag_context: str,
        chat_history: Optional[List[Dict]] = None,
        session_profile: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Construct the full message list for LLaMA 3:
          [system] → [user/assistant history turns] → [user query]

        The system message contains:
          1. Counselor persona
          2. Student profile (structured JSON block)
          3. RAG knowledge base context (grounded domain data)
        """
        # We now use the specialized prompt templates for the system and user messages
        from prompt_templates import COUNSELOR_SYSTEM_PROMPT, build_contextual_prompt
        
        # ── System message ──
        system_content = COUNSELOR_SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history (last 8 turns)
        if chat_history:
            for turn in chat_history[-8:]:
                role    = turn.get("role", "user")
                content = turn.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        # Final user message built using the intent-based query router
        final_user_prompt = build_contextual_prompt(query, session_profile or {}, rag_context)
        
        messages.append({"role": "user", "content": final_user_prompt})
        return messages

    # ── Main Entry Points ─────────────────────────────────────────────────────

    def stream_response(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None,
        session_id: Optional[str] = None,
        session_profile: Optional[Dict] = None,
    ) -> Generator[str, None, None]:
        """
        THE MAIN STREAM ENTRY POINT.

        Pipeline:
          query → RAG fetch → prompt build → LLM stream → tokens
          Fallback chain: Groq (fast cloud) → Ollama (local) → RAG-only text
        """
        query = (query or "").strip()
        if not query:
            yield "Please ask me something — I'm here to help! 🎓"
            return

        # Step 1: PRIORITY 1 — Fetch JSON database context (exact values)
        json_context = self._get_json_context(query, session_profile)

        # Step 1.5: KEA Simulation context (ML + Rules predictions)
        kea_context = self._get_kea_simulation_context(query, session_profile)

        # Step 2: PRIORITY 2 — Fetch RAG context (ChromaDB cosine similarity)
        rag_context = self._get_rag_context(query)

        # Step 3: Combine contexts (JSON first, then KEA simulation, then RAG)
        combined_context = ""
        if json_context:
            combined_context = json_context
        if kea_context:
            if combined_context:
                combined_context += f"\n\n{kea_context}"
            else:
                combined_context = kea_context
        if rag_context:
            if combined_context:
                combined_context += f"\n\n=== PRIORITY 2: CHROMADB RETRIEVED CONTEXT ===\n\n{rag_context}\n\n=== END CHROMADB ==="
            else:
                combined_context = rag_context

        # Step 4: Build prompt (system + profile + combined context + history + query)
        messages = self._build_messages(
            query, combined_context, chat_history, session_profile
        )

        # Step 5: Define the raw generation stream
        def _get_raw_stream():
            yielded = False
            if self.groq.available:
                try:
                    for token in self.groq.stream(messages):
                        yield token
                        yielded = True
                    if yielded:
                        self.last_model_used = f"LLaMA 3.3 70B (Groq)"
                        return
                except Exception as e:
                    logger.error("Groq stream failed: %s", e)

            if not yielded and self.ollama.available:
                try:
                    for token in self.ollama.stream(messages):
                        yield token
                        yielded = True
                    if yielded:
                        self.last_model_used = f"LLaMA 3 (Ollama Local)"
                        return
                except Exception as e:
                    logger.error("Ollama stream failed: %s", e)

            if not yielded:
                logger.warning("All LLMs unavailable -- serving RAG fallback")
                self.last_model_used = "RAG Knowledge Base"
                yield self.fallback.generate(query)
                
        # Step 6: Validate the entire stream against combined context (JSON + RAG)
        yield from self._validated_stream(_get_raw_stream(), combined_context)

    def generate_response(
        self,
        query: str,
        chat_history: Optional[List[Dict]] = None,
        session_id: Optional[str] = None,
        session_profile: Optional[Dict] = None,
    ) -> str:
        """Non-streaming version — collects the full streamed response."""
        parts = []
        for token in self.stream_response(query, chat_history, session_id, session_profile):
            parts.append(token)
        return "".join(parts)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Simple prompt → response (used by career simulator, counseling service, etc.).
        Does NOT inject RAG — caller is responsible for providing context in prompt.
        Tries Groq first, then Ollama, then RAG fallback.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Try Groq first (fast)
        if self.groq.available:
            result = self.groq.generate(messages, temperature, max_tokens)
            if result:
                return result

        # Fallback to Ollama
        result = self.ollama.generate(messages, temperature, max_tokens)
        if result:
            return result

        # Last resort
        return self.fallback.generate(prompt)

    def _check_connection(self) -> bool:
        """Health check — is Ollama reachable?"""
        if not self.ollama.available:
            return False
        try:
            r = httpx.get(f"{self.ollama.host}/api/tags", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Health status for /api/ai/status endpoint."""
        ollama_ok = self._check_connection()
        return {
            "groq": {
                "available": self.groq.available,
                "model":     self.groq.model,
            },
            "ollama": {
                "available": ollama_ok,
                "host":      self.ollama.host,
                "model":     self.ollama.model,
            },
            "rag_engine": {
                "available": self.rag is not None,
            },
            "pipeline": "groq-cloud → ollama-local → rag-fallback",
            "last_model_used": self.last_model_used,
        }


# ==============================================================================
# SINGLETON — backward-compatible with app.py
# ==============================================================================
_counselor: Optional[InsightRuralCounselor] = None


def get_llm_service() -> InsightRuralCounselor:
    """Get or create the InsightRuralCounselor singleton (Ollama + LLaMA 3)."""
    global _counselor
    if _counselor is None:
        _counselor = InsightRuralCounselor()
    return _counselor


# Backward-compat alias (used in some tests)
MultiLLMOrchestrator = InsightRuralCounselor
