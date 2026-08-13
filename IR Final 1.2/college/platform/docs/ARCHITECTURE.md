# Architecture — KCET Counselling Platform v3.0

## System Overview

```mermaid
flowchart TB
    subgraph client [React Frontend]
        UI[Dashboard Pages]
    end

    subgraph api [FastAPI Backend :8000]
        L1[Layer 1: Query Understanding]
        L2[Layer 2: Counselling Engine]
        L3[Layer 3: Admission Probability]
        L4[Layer 4: Constraint Filter]
        L5[Layer 5: Ranking Engine]
        L6[Layer 6: RAG / ChromaDB]
        L7[Layer 7: Web Intelligence]
        L8[Layer 8: Response Generator]
        ORCH[Recommendation Orchestrator]
    end

    subgraph data [Data Layer]
        JSON[(JSON Data Files)]
        PG[(PostgreSQL)]
        CHROMA[(ChromaDB)]
    end

    UI --> ORCH
    ORCH --> L1 --> L2 --> L3 --> L4 --> L5
    L2 --> JSON
    L2 -.-> PG
    L6 --> CHROMA
    L8 --> L6
    L8 --> L7
    L5 --> L8
```

## Layer Responsibilities

| Layer | Module | LLM? | Purpose |
|-------|--------|------|---------|
| 1 | `query_understanding.py` | No | Extract rank, city, budget, quotas |
| 2 | `counselling_engine.py` | No | KEA eligibility, reservation rules |
| 3 | `admission_probability.py` | No | RF/XGB/LGBM + rule-based probability |
| 4 | `constraint_filter.py` | No | Hard filters — never relaxed |
| 5 | `ranking_engine.py` | No | Weighted composite scoring |
| 6 | `rag/chroma_client.py` | No | Semantic document search |
| 7 | `web_intel/official_sources.py` | No | Official source URLs only |
| 8 | `llm/response_generator.py` | Yes | Explain only — never select |

## Ranking Weights

- 40% admission probability
- 20% placements
- 15% accreditation (NAAC)
- 10% hostel quality
- 10% fees (budget fit)
- 5% location preference

## Tier Classification

| Tier | Probability | Label |
|------|-------------|-------|
| SAFE | > 80% | High confidence admission |
| MODERATE | 50-80% | Realistic target |
| AMBITIOUS | < 50% | Stretch goal |

## Confidence Score

Calculated from:
- Profile completeness (rank present)
- Number of matching colleges after filters
- Average data completeness across results

Never defaults to 95%+ without sufficient data.

## Security

- Input validation (Pydantic)
- Rate limiting (60 req/min)
- Audit logging
- Prompt injection sanitization
- JWT RBAC for admin endpoints

## Deployment

See `DEPLOYMENT.md` for Docker, Kubernetes, and CI/CD setup.
