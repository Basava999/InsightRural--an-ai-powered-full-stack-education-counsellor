# ==============================================================================
# InsightRural — LLM Output Validators
# ==============================================================================
# Sentence-level validation to catch and suppress hallucinated numeric facts.
# Extracted from llm_service.py for reusability.
# ==============================================================================

import re
from typing import Generator, Optional

from core.logging import get_logger

logger = get_logger("llm.validators")


def validate_sentence(sentence: str, rag_context: str) -> str:
    """
    Validate a single sentence against the RAG context.

    Rules:
    - Numbers > 10 must appear somewhere in the context (prevents hallucinated fees/ranks).
    - Years (2000-2050) are always allowed.
    - Small numbers (<=10) are always allowed (e.g., "top 5 colleges").

    Returns:
        The original sentence if valid, or a suppression message if it contains
        unsupported numeric claims.
    """
    if len(sentence.strip()) < 5:
        return sentence

    norm_context = rag_context.replace(",", "") if rag_context else ""
    numbers = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', sentence)

    for num_str in numbers:
        try:
            val = float(num_str.replace(",", ""))
            if val <= 10:
                continue  # Small counts/lists
            if 2000 <= val <= 2050 and len(num_str.replace(",", "")) == 4:
                continue  # Recent years
        except ValueError:
            continue

        norm_num = num_str.replace(",", "")
        if norm_num not in norm_context:
            logger.debug(
                "Suppressed hallucinated number '%s' not found in context", num_str
            )
            return "Verified information is currently unavailable.\n"

    return sentence


def validated_stream(
    stream_gen: Generator[str, None, None],
    rag_context: str,
) -> Generator[str, None, None]:
    """
    Sentence-buffer a token stream and validate each sentence
    against the RAG context before yielding.

    This prevents hallucinated facts from reaching the user in streaming mode.
    """
    buffer = ""
    for token in stream_gen:
        buffer += token
        while True:
            # Find sentence boundary: ". ", "! ", "? ", or newlines
            match = re.search(r'([.!?]\s+|\n+)', buffer)
            if not match:
                break

            idx = match.end()
            sentence = buffer[:idx]
            buffer = buffer[idx:]

            yield validate_sentence(sentence, rag_context)

    if buffer:
        yield validate_sentence(buffer, rag_context)


def validate_numeric_claim(
    value: float,
    context: str,
    tolerance_pct: float = 10.0,
) -> bool:
    """
    Check if a specific numeric value appears in the context
    within a tolerance percentage.

    Used for post-hoc fact-checking of fee amounts, rank numbers, etc.
    """
    if not context:
        return False

    # Extract all numbers from context
    context_numbers = re.findall(r'\b(\d+(?:,\d+)*(?:\.\d+)?)\b', context)

    for num_str in context_numbers:
        try:
            ctx_val = float(num_str.replace(",", ""))
            if ctx_val == 0:
                continue
            diff_pct = abs(value - ctx_val) / ctx_val * 100
            if diff_pct <= tolerance_pct:
                return True
        except ValueError:
            continue

    return False


def extract_citations(
    response_text: str,
    source_count: int,
) -> dict:
    """
    Extract citation markers [1], [2], etc. from LLM response
    and map them to source indices.

    Returns:
        {"cited_sources": [0, 2], "uncited_claims": 3}
    """
    cited = set()
    pattern = re.compile(r'\[(\d+)\]')
    matches = pattern.findall(response_text)

    for m in matches:
        idx = int(m) - 1  # Convert 1-indexed to 0-indexed
        if 0 <= idx < source_count:
            cited.add(idx)

    # Count sentences without citations (potential uncited claims)
    sentences = re.split(r'[.!?]+', response_text)
    uncited_count = 0
    for s in sentences:
        s = s.strip()
        if len(s) > 30 and not pattern.search(s):
            # Long sentence without citation
            has_number = bool(re.search(r'\b\d{3,}\b', s))
            if has_number:
                uncited_count += 1

    return {
        "cited_sources": sorted(cited),
        "uncited_claims": uncited_count,
    }
