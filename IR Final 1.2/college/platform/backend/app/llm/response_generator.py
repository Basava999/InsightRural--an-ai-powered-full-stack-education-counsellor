"""
Layer 8: Response Generation
LLM ONLY explains deterministic results — never selects colleges.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from app.schemas.student import RecommendationResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a KCET counselling assistant for Karnataka engineering admissions.
CRITICAL RULES:
1. NEVER recommend or select colleges yourself.
2. ONLY explain the recommendations provided in the context.
3. NEVER invent cutoff ranks, fees, or hostel details.
4. If data is missing, say "verified data not available".
5. Reference KEA official counselling process when relevant.
6. Be concise, factual, and supportive."""


class ResponseGenerator:
    """Generate human-readable explanations from deterministic engine output."""

    def explain_recommendations(self, result: RecommendationResponse) -> str:
        parts = [
            f"## KCET Counselling Analysis (Rank {result.profile.rank}, {result.profile.branch}, {result.profile.category})",
            f"**Confidence**: {result.confidence * 100:.0f}% | **Data completeness**: {result.data_completeness * 100:.0f}%",
            "",
        ]

        if result.profile.city:
            parts.append(f"**Location filter**: {result.profile.city} (hard constraint applied)")
        if result.profile.budget:
            parts.append(f"**Budget filter**: ₹{result.profile.budget:,}/year (colleges above budget excluded)")
        if result.profile.hostel_required:
            parts.append("**Hostel filter**: Only colleges with hostel facilities included")

        parts.append(f"\nFound {result.total_after_filters} colleges matching all constraints "
                      f"(from {result.total_eligible} eligible).")

        for tier, label, emoji in [
            ("safe", "SAFE (>80% probability)", "🟢"),
            ("moderate", "MODERATE (50-80%)", "🟡"),
            ("ambitious", "AMBITIOUS (<50%)", "🔴"),
        ]:
            recs = getattr(result, tier)
            if not recs:
                continue
            parts.append(f"\n### {emoji} {label}")
            for r in recs[:5]:
                fee_str = f"₹{r.annual_fee:,.0f}/yr" if r.annual_fee else "N/A"
                parts.append(
                    f"- **{r.college_name}** ({r.location}) — {r.branch}\n"
                    f"  Probability: {r.admission_probability}% | Cutoff: {r.cutoff_rank} | Fee: {fee_str}"
                )
                if r.explanation:
                    parts.append(f"  _{r.explanation[0]}_")

        if result.hostels:
            parts.append(f"\n### Hostel Information ({len(result.hostels)} verified records)")
            for h in result.hostels[:3]:
                parts.append(f"- {h.get('college_name', 'Unknown')}: verified database record")

        return "\n".join(parts)

    def generate_with_llm(
        self,
        user_query: str,
        result: RecommendationResponse,
        rag_context: Optional[List[Dict]] = None,
        llm_client=None,
    ) -> str:
        deterministic = self.explain_recommendations(result)
        if not llm_client:
            return deterministic

        context = deterministic
        if rag_context:
            context += "\n\n### Reference Documents\n"
            for doc in rag_context[:3]:
                context += f"- {doc.get('content', '')[:300]}\n"

        prompt = f"{SYSTEM_PROMPT}\n\nUser question: {user_query}\n\nDeterministic results:\n{context}\n\nProvide a helpful explanation based ONLY on the above data."

        try:
            return llm_client.generate(prompt)
        except Exception as e:
            logger.warning("LLM generation failed: %s", e)
            return deterministic

    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Basic prompt injection protection."""
        cleaned = text[:4000]
        patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"you\s+are\s+now",
            r"system\s*:",
            r"<\s*script",
        ]
        for p in patterns:
            cleaned = re.sub(p, "[filtered]", cleaned, flags=re.I)
        return cleaned.strip()
