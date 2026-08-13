# ==============================================================================
# InsightRural — Chat API Router
# ==============================================================================
# Replaces the old Flask /chat endpoint. The critical architectural change:
#   OLD: Query → LLM picks colleges → Response
#   NEW: Query → QueryParser → RecommendationService → LLM explains results
#
# The LLM NEVER selects, filters, or ranks colleges.
# It receives pre-computed results and generates human-friendly explanations.
# ==============================================================================

import os
import json
import logging
import time
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest, ChatResponse

logger = logging.getLogger("ChatAPI")
router = APIRouter()


# ── LLM Configuration ────────────────────────────────────────────────────────

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI-powered counselling chat.

    Pipeline:
    1. Parse query intent
    2. If recommendation intent → run deterministic pipeline first
    3. Build context from pipeline results + RAG + JSON data
    4. Send to LLM for explanation ONLY
    5. Return response with structured data
    """
    from main import get_recommendation_service, get_query_parser, get_json_data

    start_time = time.time()
    query = request.message.strip()
    profile_data = request.profile or {}

    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # ── Step 1: Detect intent ─────────────────────────────────────────
    parser = get_query_parser()
    intent = parser.detect_intent(query)
    logger.info(f"Chat intent: {intent} | Query: {query[:80]}...")

    # ── Step 2: Build context based on intent ─────────────────────────
    context_parts = []
    recommendation_result = None

    if intent == "recommendation":
        # Run the DETERMINISTIC pipeline — LLM does NOT make this decision
        service = get_recommendation_service()
        recommendation_result, parse_meta = service.recommend_from_chat(
            query, profile_data
        )

        # Format recommendations as context for the LLM explainer
        context_parts.append(_format_recommendations_for_llm(recommendation_result))

    elif intent == "scholarship":
        data = get_json_data()
        category = profile_data.get("category")
        income = profile_data.get("income")
        gender = profile_data.get("gender")
        context_parts.append(data.get_scholarships(
            category=category, income=income, gender=gender
        ))

    elif intent == "loan":
        data = get_json_data()
        income = profile_data.get("income")
        context_parts.append(data.get_loans(income=income))

    elif intent == "hostel":
        data = get_json_data()
        # Extract college name from query if present
        college_name = _extract_college_from_query(query)
        context_parts.append(data.get_hostel_info(college_name=college_name))

    elif intent == "fee":
        data = get_json_data()
        college_name = _extract_college_from_query(query)
        context_parts.append(data.get_fee_structure(college_name=college_name))

    elif intent == "counseling":
        data = get_json_data()
        context_parts.append(data.get_counseling_info())

    elif intent == "cutoff":
        data = get_json_data()
        college_name = _extract_college_from_query(query)
        if college_name:
            context_parts.append(data.get_cutoff_trends(college_name))
            context_parts.append(data.get_college_details(college_name))

    # ── Step 3: Add RAG context ───────────────────────────────────────
    try:
        from rag_engine import get_rag_engine
        rag = get_rag_engine()
        rag_results = rag.hybrid_search(query, n_results=3)
        if rag_results:
            rag_text = "\n\n".join([
                f"[RAG Source: {r.get('source', 'Database')}]\n{r.get('content', '')}"
                for r in rag_results
            ])
            context_parts.append(f"\n## PRIORITY 2: CHROMADB RETRIEVED CONTEXT\n{rag_text}")
    except Exception as e:
        logger.warning(f"RAG search failed: {e}")

    # ── Step 4: Build full context ────────────────────────────────────
    full_context = "\n\n".join([c for c in context_parts if c])

    if not full_context:
        full_context = "No specific data found in the database for this query."

    # ── Step 5: Generate LLM explanation ──────────────────────────────
    from prompt_templates import (
        COUNSELOR_SYSTEM_PROMPT,
        build_contextual_prompt,
        format_student_profile,
    )

    user_prompt = build_contextual_prompt(
        query=query,
        student_profile=profile_data,
        context=f"## PRIORITY 1: STRUCTURED DATABASE\n{full_context}",
        query_type=intent,
    )

    messages = [
        {"role": "system", "content": COUNSELOR_SYSTEM_PROMPT},
    ]

    # Add conversation history
    for msg in request.history[-6:]:  # Last 6 messages for context
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })

    messages.append({"role": "user", "content": user_prompt})

    # Call LLM
    response_text, model_used = await _call_llm(messages)

    elapsed = time.time() - start_time
    logger.info(f"Chat completed in {elapsed:.2f}s | Model: {model_used}")

    return ChatResponse(
        response=response_text,
        session_id=request.session_id,
        model_used=model_used,
        recommendations=(
            recommendation_result if recommendation_result else None
        ),
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.
    Same pipeline as /chat but streams the LLM response token by token.
    """
    from main import get_recommendation_service, get_query_parser, get_json_data

    query = request.message.strip()
    profile_data = request.profile or {}
    parser = get_query_parser()
    intent = parser.detect_intent(query)

    # Build context (same as non-streaming)
    context_parts = []

    if intent == "recommendation":
        service = get_recommendation_service()
        result, _ = service.recommend_from_chat(query, profile_data)
        context_parts.append(_format_recommendations_for_llm(result))

    elif intent == "scholarship":
        data = get_json_data()
        context_parts.append(data.get_scholarships(
            category=profile_data.get("category"),
            income=profile_data.get("income"),
        ))

    elif intent == "loan":
        data = get_json_data()
        context_parts.append(data.get_loans(income=profile_data.get("income")))

    elif intent == "hostel":
        data = get_json_data()
        context_parts.append(data.get_hostel_info(
            college_name=_extract_college_from_query(query)
        ))

    elif intent == "fee":
        data = get_json_data()
        context_parts.append(data.get_fee_structure(
            college_name=_extract_college_from_query(query)
        ))

    elif intent == "counseling":
        data = get_json_data()
        context_parts.append(data.get_counseling_info())

    # RAG
    try:
        from rag_engine import get_rag_engine
        rag = get_rag_engine()
        rag_results = rag.hybrid_search(query, n_results=3)
        if rag_results:
            rag_text = "\n\n".join([
                f"[Source: {r.get('source', 'DB')}]\n{r.get('content', '')}"
                for r in rag_results
            ])
            context_parts.append(rag_text)
    except Exception:
        pass

    full_context = "\n\n".join([c for c in context_parts if c]) or "No data found."

    from prompt_templates import (
        COUNSELOR_SYSTEM_PROMPT, build_contextual_prompt
    )

    user_prompt = build_contextual_prompt(
        query=query,
        student_profile=profile_data,
        context=f"## PRIORITY 1: STRUCTURED DATABASE\n{full_context}",
        query_type=intent,
    )

    messages = [
        {"role": "system", "content": COUNSELOR_SYSTEM_PROMPT},
    ]
    for msg in request.history[-6:]:
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        })
    messages.append({"role": "user", "content": user_prompt})

    return StreamingResponse(
        _stream_llm(messages),
        media_type="text/event-stream",
    )


# ══════════════════════════════════════════════════════════════════════════════
# LLM Calling (Groq primary, Ollama fallback)
# ══════════════════════════════════════════════════════════════════════════════

async def _call_llm(messages: list) -> tuple:
    """Call LLM — Groq primary, Ollama fallback. Returns (text, model_used)."""
    import httpx

    # Try Groq first
    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    GROQ_API_URL,
                    json={
                        "model": GROQ_MODEL,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 2048,
                    },
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]
                    return text, f"groq/{GROQ_MODEL}"
                else:
                    logger.warning(f"Groq API error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            logger.warning(f"Groq API failed: {e}")

    # Fallback to Ollama
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("message", {}).get("content", "")
                return text, f"ollama/{OLLAMA_MODEL}"
    except Exception as e:
        logger.warning(f"Ollama failed: {e}")

    # Final fallback: return context-only response
    return (
        "I apologize, but the AI language model is currently unavailable. "
        "However, I can still provide you with the database results above. "
        "Please review the structured data for your answer.",
        "fallback/none"
    )


async def _stream_llm(messages: list):
    """Stream LLM response as SSE events."""
    import httpx

    # Try Groq streaming
    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream(
                    "POST",
                    GROQ_API_URL,
                    json={
                        "model": GROQ_MODEL,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 2048,
                        "stream": True,
                    },
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                yield "data: [DONE]\n\n"
                                return
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                pass
                    yield "data: [DONE]\n\n"
                    return
        except Exception as e:
            logger.warning(f"Groq streaming failed: {e}")

    # Ollama streaming fallback
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": 0.3},
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                            if chunk.get("done"):
                                yield "data: [DONE]\n\n"
                                return
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        logger.warning(f"Ollama streaming failed: {e}")
        yield f"data: {json.dumps({'content': 'AI model unavailable. Please check database results.'})}\n\n"
        yield "data: [DONE]\n\n"


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _format_recommendations_for_llm(result) -> str:
    """
    Format recommendation results as structured context for the LLM.
    The LLM will use this to EXPLAIN the results, not to make them.
    """
    parts = ["## COLLEGE RECOMMENDATIONS (Pre-computed by deterministic engine)"]
    parts.append(f"Total eligible: {result.total_eligible} colleges")
    parts.append(f"Confidence: {result.confidence.get('overall', 'N/A')}")
    parts.append("")

    for tier_name, tier_data, emoji in [
        ("SAFE", result.safe, "✅"),
        ("MODERATE", result.moderate, "⚠️"),
        ("AMBITIOUS", result.ambitious, "🎯"),
    ]:
        if not tier_data:
            continue
        parts.append(f"\n### {emoji} {tier_name} OPTIONS ({len(tier_data)})")
        for c in tier_data[:7]:
            fee_str = f"₹{c.annual_fee:,}" if c.annual_fee else "N/A"
            parts.append(
                f"- **{c.college_name}** ({c.location})\n"
                f"  Branch: {c.branch} | Cutoff: {c.cutoff_rank} | "
                f"Fee: {fee_str}/yr | Type: {c.college_type} | "
                f"Score: {c.recommendation_score}/100 | "
                f"Avg Pkg: {c.placement_avg_lpa or 'N/A'} LPA | "
                f"NAAC: {c.naac_grade or 'N/A'} | "
                f"Hostel: {'Yes' if c.hostel_available else 'No'}"
            )
            if c.reservation.has_benefit:
                parts.append(f"  Reservation: {', '.join(c.reservation.benefits)}")

    # Add counselling guidance
    guidance = result.counselling_guidance
    if guidance:
        parts.append(f"\n### COUNSELLING GUIDANCE")
        parts.append(f"Risk Level: {guidance.get('risk_level', 'N/A')}")
        parts.append(f"Strategy: {guidance.get('strategy', '')}")
        for tip in guidance.get("tips", []):
            parts.append(f"- 💡 {tip}")

    # Add option entry sequence
    if result.option_entry_sequence:
        parts.append(f"\n### RECOMMENDED OPTION ENTRY ORDER")
        for opt in result.option_entry_sequence:
            parts.append(
                f"{opt['order']}. {opt['tier']} {opt['college_name']} - "
                f"{opt['branch']} ({opt['location']})"
            )

    parts.append(
        "\n---\n"
        "INSTRUCTION TO AI: The above recommendations were computed by the "
        "deterministic engine using exact database values. Your job is to "
        "EXPLAIN these results to the student in a helpful, encouraging way. "
        "Do NOT add, remove, or reorder any colleges. Use the exact numbers provided."
    )

    return "\n".join(parts)


def _extract_college_from_query(query: str) -> Optional[str]:
    """Try to extract a college name from a query."""
    # Common abbreviation list
    abbr_map = {
        "rvce": "R.V. College of Engineering",
        "rv college": "R.V. College of Engineering",
        "bmsce": "B.M.S. College of Engineering",
        "bms": "B.M.S. College of Engineering",
        "msrit": "M.S. Ramaiah Institute of Technology",
        "ramaiah": "M.S. Ramaiah Institute of Technology",
        "pes": "PES University",
        "pesu": "PES University",
        "sit": "Siddaganga Institute of Technology",
        "nie": "National Institute of Engineering",
        "dsce": "Dayananda Sagar College of Engineering",
        "bit": "Bangalore Institute of Technology",
        "uvce": "University Visvesvaraya College of Engineering",
        "sjce": "Sri Jayachamarajendra College of Engineering",
        "mvj": "MVJ College of Engineering",
        "ait": "Ambedkar Institute of Technology",
        "nitte": "NITTE Meenakshi Institute of Technology",
        "jss": "JSS Science and Technology University",
        "vtu": "Visvesvaraya Technological University",
    }

    query_lower = query.lower()
    for abbr, full_name in abbr_map.items():
        if abbr in query_lower:
            return full_name

    return None
