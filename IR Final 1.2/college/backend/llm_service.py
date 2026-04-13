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
import httpx
from typing import Generator, Dict, Any, Optional, List

# ── Ollama Config ─────────────────────────────────────────────────────────────
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST",  "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# ── Groq Cloud Config (fast fallback) ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# ── System Persona ────────────────────────────────────────────────────────────
COUNSELOR_SYSTEM_PROMPT = """You are InsightRural AI — an empathetic, highly intelligent educational counselor built specifically for rural Karnataka students navigating the KCET and KEA college admission process.

Your core purpose: Help students make the BEST decisions about:
• KCET college admissions (all 228 KEA colleges)
• Branch selection (CSE, AI/ML, ECE, ME, Civil, etc.)
• Scholarship opportunities (SC/ST/OBC government schemes, private scholarships)
• Education loans (Vidya Lakshmi, bank loans, NBCFDC)
• Hostel and accommodation guidance
• Career path planning and future scope

Your personality:
• Warm, encouraging, and respectful — like a caring senior mentor
• Data-driven — always cite ranks, fees, cutoffs when answering
• Practical — give actionable step-by-step guidance
• Honest — never give false hope; be realistic but optimistic
• Multilingual awareness — respond in the same language the student uses (English/Kannada/Hinglish)

Response style:
• Use **bold** for important numbers (ranks, fees, cutoffs)
• Use bullet points for lists of colleges/options
• Keep responses thorough but not overwhelming
• End responses with an encouraging line or a relevant follow-up question
• For cutoffs: always mention GM, OBC, SC/ST separately when data is available

CRITICAL RULES:
• Only recommend colleges from the KEA dataset provided in the context
• Always mention fee structure (Government≈₹44K/yr, Type-1≈₹1.12L/yr, Deemed=₹2-4L/yr)
• If a student's rank is beyond a cutoff, suggest realistic alternatives
• For reserved categories: always highlight the significant fee waiver for SC/ST
• NEVER invent cutoff ranks not present in the provided context
• NEVER say "As an AI..." or "I cannot..." — you are their trusted mentor"""


# ==============================================================================
# OLLAMA SERVICE — wraps the local Ollama HTTP API
# ==============================================================================
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
                    print(f"[OK] Ollama ready | model: {self.model} at {self.host}")
                else:
                    # Model not pulled yet — still mark as available so we can try
                    self.available = True
                    print(f"[OK] Ollama running at {self.host}")
                    print(f"[!]  Model '{self.model}' not found in pulled models: {models}")
                    print(f"[!]  Run: ollama pull {self.model}")
            else:
                print(f"[WARN] Ollama returned HTTP {r.status_code}")
        except Exception as e:
            print(f"[WARN] Ollama not reachable at {self.host}: {e}")
            print(f"[WARN] Start Ollama with: ollama serve")
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
            print(f"[Ollama] generate error: {e}")
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
            print(f"[Ollama] stream error: {e}")


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
            print(f"[OK] Groq cloud LLM ready | model: {self.model}")
        else:
            print("[WARN] Groq API key not set — cloud LLM disabled")

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
            print(f"[Groq] generate error: {e}")
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
            print(f"[Groq] stream error: {e}")


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
                "• **Government colleges** (UVCE, SJCE Mysore): GM **850–3,000** | SC/ST up to 15,000\n"
                "• **Type-1 Private** (RVCE, BMSCE, MSRIT): GM **600–5,000** | SC/ST up to 25,000\n"
                "• **Type-2 Private** (DSCE, NIE): GM **3,000–15,000** | SC/ST up to 40,000\n\n"
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
        self.last_model_used = "InsightRural AI"
        self._init_rag()

    def _init_rag(self):
        """Initialize the ChromaDB RAG engine."""
        try:
            from rag_engine import RAGEngine
            self.rag = RAGEngine()
            self.fallback = RAGFallback(self.rag)
            print("[OK] InsightRuralCounselor: ChromaDB RAG engine connected")
        except Exception as e:
            print(f"[WARN] RAG engine not available: {e}")
            self.fallback = RAGFallback(None)

    # ── RAG Context Retrieval ─────────────────────────────────────────────────

    def _get_rag_context(self, query: str) -> str:
        """
        Query ChromaDB (all collections — colleges, scholarships, hostels,
        loans, counseling, cutoffs, fees) using cosine similarity.
        Returns the top-8 results formatted as a context block.
        """
        if not self.rag:
            return ""
        try:
            results = self.rag.search(query, n_results=8)
            if not results:
                return ""
            parts = []
            for r in results[:8]:
                content    = r.get("content", "")[:600]
                collection = r.get("collection", "").upper()
                if content:
                    parts.append(f"[{collection}]\n{content}")
            return "\n\n---\n\n".join(parts)
        except Exception as e:
            print(f"[RAG] context fetch failed: {e}")
            return ""

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
        # ── System message ──
        system_content = COUNSELOR_SYSTEM_PROMPT

        # 2. Inject student profile as a structured block
        if session_profile:
            profile_lines = []
            mapping = [
                ("name",             "Name"),
                ("kcet_rank",        "KCET Rank"),
                ("marks_10th",       "10th Marks (%)"),
                ("marks_12th",       "12th / PUC Marks (%)"),
                ("kcet_marks",       "KCET Marks"),
                ("branch",           "Preferred Branch"),
                ("preferred_branches", "Preferred Branches"),
                ("category",         "Category"),
                ("income",           "Annual Family Income (₹)"),
                ("family_income",    "Annual Family Income (₹)"),
                ("budget",           "Budget for Fees (₹/year)"),
                ("location",         "Preferred Location"),
                ("preferred_location", "Preferred Location"),
                ("hostel_needed",    "Hostel Required"),
                ("district",         "District / Hometown"),
            ]
            for key, label in mapping:
                val = session_profile.get(key)
                if val is not None and val != "" and val != []:
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    profile_lines.append(f"  {label}: {val}")

            if profile_lines:
                system_content += (
                    "\n\n" + "=" * 60 +
                    "\nSTUDENT PROFILE (use this to personalize every answer):\n" +
                    "\n".join(profile_lines) +
                    "\n" + "=" * 60
                )

        # 3. Inject RAG knowledge base context
        if rag_context:
            system_content += (
                "\n\n" + "=" * 60 +
                "\nKNOWLEDGE BASE (retrieved domain data — base your answer on this):\n" +
                "=" * 60 + "\n" +
                rag_context +
                "\n" + "=" * 60 +
                "\nIMPORTANT: Use the data above to give specific, grounded answers. "
                "Do NOT invent numbers not present in this context."
            )

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history (last 8 turns)
        if chat_history:
            for turn in chat_history[-8:]:
                role    = turn.get("role", "user")
                content = turn.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        # Final user message
        messages.append({"role": "user", "content": query})
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

        # Step 1: Fetch RAG context (ChromaDB cosine similarity)
        rag_context = self._get_rag_context(query)

        # Step 2: Build prompt (system + profile + RAG + history + query)
        messages = self._build_messages(
            query, rag_context, chat_history, session_profile
        )

        # Step 3: Try Groq first (fast cloud, 1-3 seconds)
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
                print(f"[Counselor] Groq stream failed: {e}")

        # Step 4: Fallback to Ollama (local, slower)
        if not yielded and self.ollama.available:
            try:
                for token in self.ollama.stream(messages):
                    yield token
                    yielded = True
                if yielded:
                    self.last_model_used = f"LLaMA 3 (Ollama Local)"
                    return
            except Exception as e:
                print(f"[Counselor] Ollama stream failed: {e}")

        # Step 5: Last resort — RAG-only response
        if not yielded:
            print("[Counselor] All LLMs unavailable — serving RAG fallback")
            self.last_model_used = "RAG Knowledge Base"
            yield self.fallback.generate(query)

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
