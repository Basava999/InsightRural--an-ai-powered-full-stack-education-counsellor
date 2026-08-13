"""Counselling chatbot — LLM explains, engine decides."""

from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.core.audit import log_request
from app.schemas.student import ChatRequest, ChatResponse
from app.engines.recommendation_orchestrator import RecommendationOrchestrator
from app.llm.response_generator import ResponseGenerator
from app.rag.chroma_client import ChromaRAGClient
from app.web_intel.official_sources import WebIntelligenceLayer

router = APIRouter()
settings = get_settings()
_orchestrator = RecommendationOrchestrator()
_response_gen = ResponseGenerator()
_rag = ChromaRAGClient(settings.CHROMA_DIR)
_web_intel = WebIntelligenceLayer()


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request):
    log_request("chat", "/chat", ip=request.client.host if request.client else None)

    sanitized = ResponseGenerator.sanitize_user_input(body.message)
    result, error = _orchestrator.recommend_from_query(sanitized, body.profile)

    if error and not result:
        official = _web_intel.get_official_links(sanitized)
        return ChatResponse(
            answer=f"{error} Visit official sources: {official[0]['url'] if official else 'https://cetonline.karnataka.gov.in'}",
            engine_used="deterministic",
        )

    rag_docs = _rag.search_multi_collection(sanitized) if _rag.available else []
    answer = _response_gen.generate_with_llm(sanitized, result, rag_docs)

    sources = [d.get("metadata", {}).get("source", "database") for d in rag_docs]
    sources.extend(s["url"] for s in _web_intel.get_official_links(sanitized))

    return ChatResponse(
        answer=answer,
        recommendations=result,
        sources=list(set(sources)),
        engine_used="deterministic+llm_explain",
    )
