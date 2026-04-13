"""
InsightRural — Sarvam AI + RAG Integration Test
================================================
Tests the full pipeline: RAG search → Prompt building → Sarvam generation
Run: python test_sarvam_rag.py
"""
import os, sys, json, time

# ── Setup path ────────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

# Load .env
from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND_DIR, '.env'))

print("=" * 65)
print("  INSIGHTRURAL — SARVAM AI + RAG INTEGRATION TEST")
print("=" * 65)

# ── Step 1: Verify env vars ───────────────────────────────────────────────────
print("\n[1] Environment Check")
api_key = os.environ.get("SARVAM_API_KEY", "")
if api_key:
    print(f"  ✅ SARVAM_API_KEY set ({api_key[:10]}...)")
else:
    print("  ❌ SARVAM_API_KEY not set! Add it to .env")
    sys.exit(1)

# ── Step 2: Sarvam AI connection ──────────────────────────────────────────────
print("\n[2] Sarvam AI Connection")
from llm_service import get_llm_service

llm = get_llm_service()
if llm.client:
    print("  ✅ Sarvam AI client initialized")
else:
    print("  ❌ Sarvam AI client FAILED to initialize")
    sys.exit(1)

# Quick ping test
print("  ⏳ Testing API call (simple ping)...")
t0 = time.time()
ping_response = llm.generate(
    prompt="Reply with ONLY the word PONG",
    system_prompt="You are a test bot. Reply only with the single word PONG.",
    temperature=0.0,
    max_tokens=10
)
elapsed = time.time() - t0
ping_ok = "pong" in ping_response.lower() or len(ping_response.strip()) < 20
print(f"  {'✅' if ping_ok else '⚠️'} Ping response: '{ping_response.strip()}' ({elapsed:.1f}s)")

# ── Step 3: RAG Engine ────────────────────────────────────────────────────────
print("\n[3] RAG Engine Check")
try:
    from rag_engine import get_rag_engine
    rag = get_rag_engine()
    print("  ✅ RAG engine loaded")
except Exception as e:
    print(f"  ❌ RAG engine failed: {e}")
    sys.exit(1)

# ── Step 4: RAG Search Quality Tests ─────────────────────────────────────────
print("\n[4] RAG Search Quality")

test_queries = [
    ("College query", "Which college can I get with rank 5000 in CSE?", "colleges"),
    ("Scholarship query", "What scholarships are available for SC students?", "scholarships"),
    ("Loan query", "Tell me about education loans for engineering students", "loans"),
    ("Hostel query", "What are the hostel options at RVCE?", "hostels"),
    ("Counseling query", "Explain the KEA KCET counseling process steps", "counseling"),
    ("Fee query", "What is the fee structure for SC/ST students?", "fees"),
]

search_results_ok = True
for label, query, expected_collection in test_queries:
    results = rag.search(query, collection_name=expected_collection, n_results=3)
    if results:
        top = results[0]
        snippet = top['content'][:80].replace('\n', ' ')
        dist = top.get('distance', 'N/A')
        print(f"  ✅ {label}: {len(results)} results | top: '{snippet}...' | dist={dist:.3f}" if isinstance(dist, float) else f"  ✅ {label}: {len(results)} results | '{snippet}...'")
    else:
        print(f"  ❌ {label}: NO RESULTS RETURNED!")
        search_results_ok = False

# ── Step 5: Rank-based college lookup ─────────────────────────────────────────
print("\n[5] Rank-based College Lookup (rank=5000, CSE, OBC)")
colleges = rag.get_colleges_by_rank(5000, "CSE", "OBC")
if colleges:
    print(f"  ✅ Found {len(colleges)} eligible colleges")
    for c in colleges[:3]:
        print(f"    • {c['college']} ({c['location']}) — Cutoff: {c['cutoff']}, Fee: {c['fee']}")
else:
    print("  ❌ No colleges returned for rank 5000, CSE, OBC!")
    search_results_ok = False

# ── Step 6: Scholarship eligibility lookup ────────────────────────────────────
print("\n[6] Scholarship Lookup (SC, income=2L)")
scholarships = rag.get_eligible_scholarships("SC", 200000)
if scholarships:
    print(f"  ✅ Found {len(scholarships)} eligible scholarships")
    for s in scholarships[:3]:
        print(f"    • {s['name']} | Deadline: {s['deadline']}")
else:
    print("  ❌ No scholarships found for SC, income=2L!")
    search_results_ok = False

# ── Step 7: Full RAG → Prompt → Sarvam Pipeline ───────────────────────────────
print("\n[7] Full Pipeline: RAG + Sarvam (most important test)")
from prompt_templates import (
    build_contextual_prompt, detect_query_type, COUNSELOR_SYSTEM_PROMPT
)

TEST_CASES = [
    {
        "label": "College recommendation",
        "message": "Which college can I get with rank 5000 in CSE as OBC student?",
        "profile": {"kcet_rank": 5000, "branch": "CSE", "category": "OBC"},
    },
    {
        "label": "Scholarship query",
        "message": "What Karnataka scholarships are available for SC students with income under 2 lakhs?",
        "profile": {"category": "SC", "income": 200000},
    },
    {
        "label": "General query",
        "message": "Hello! How does InsightRural help students?",
        "profile": {},
    },
]

all_good = True
for tc in TEST_CASES:
    print(f"\n  ── {tc['label']} ──")
    try:
        # Step A: RAG search
        q_type = detect_query_type(tc["message"])
        collection_map = {
            'college': 'colleges', 'scholarship': 'scholarships',
            'loan': 'loans', 'hostel': 'hostels', 'counseling': 'counseling',
            'fee': 'fees'
        }
        target = collection_map.get(q_type)
        context_results = rag.search(tc["message"], collection_name=target, n_results=5)
        context = "\n\n".join([r.get("content", "") for r in context_results])
        
        # Enrich college queries
        if q_type == 'college' and tc["profile"].get("kcet_rank"):
            eligible = rag.get_colleges_by_rank(
                int(tc["profile"]["kcet_rank"]),
                tc["profile"].get("branch", "CSE"),
                tc["profile"].get("category", "GM")
            )
            if eligible:
                context += "\n\n## Eligible Colleges:\n"
                for c in eligible[:5]:
                    context += f"- {c['college']} ({c['location']}) — Cutoff: {c['cutoff']}\n"

        print(f"  RAG: query_type={q_type}, context={len(context)} chars, docs={len(context_results)}")
        
        # Step B: Build prompt
        prompt = build_contextual_prompt(tc["message"], tc["profile"], context, q_type)
        
        # Step C: Sarvam generate
        t0 = time.time()
        response = llm.generate(
            prompt=prompt,
            system_prompt=COUNSELOR_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=500
        )
        elapsed = time.time() - t0

        if response and len(response) > 20:
            snippet = response[:150].replace('\n', ' ')
            print(f"  ✅ Response ({len(response)} chars, {elapsed:.1f}s): '{snippet}...'")
        else:
            print(f"  ❌ Response too short or empty: '{response}'")
            all_good = False

    except Exception as e:
        print(f"  ❌ Pipeline error: {e}")
        import traceback; traceback.print_exc()
        all_good = False

# ── Step 8: Streaming test ────────────────────────────────────────────────────
print("\n[8] Streaming Test (generate_stream)")
try:
    stream_chunks = []
    t0 = time.time()
    for chunk in llm.generate_stream(
        prompt="List 3 top engineering colleges in Bangalore in one sentence each.",
        system_prompt=COUNSELOR_SYSTEM_PROMPT,
        temperature=0.5
    ):
        stream_chunks.append(chunk)
        sys.stdout.write(chunk)
        sys.stdout.flush()
    elapsed = time.time() - t0
    full_text = "".join(stream_chunks)
    print(f"\n  ✅ Streaming OK: {len(stream_chunks)} chunks, {len(full_text)} chars, {elapsed:.1f}s total")
except Exception as e:
    print(f"\n  ❌ Streaming FAILED: {e}")
    all_good = False

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
if all_good and search_results_ok:
    print("  ✅ ALL TESTS PASSED — Sarvam AI + RAG pipeline is HEALTHY")
else:
    print("  ⚠️  SOME TESTS FAILED — check the output above for details")
print("=" * 65)
print()
