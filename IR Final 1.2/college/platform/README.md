# KCET Counselling Platform v3.0

Production-ready AI counselling platform for KCET students.

## Architecture

```
User Query → Layer 1 (Query Understanding)
          → Layer 2 (Counselling Engine) — KEA rules, quotas
          → Layer 3 (Admission Probability) — ML + rule blend
          → Layer 4 (Constraint Filter) — HARD filters, never relaxed
          → Layer 5 (Ranking Engine) — weighted composite score
          → Layer 6 (RAG) — ChromaDB semantic search
          → Layer 7 (Web Intel) — official sources only
          → Layer 8 (Response Gen) — LLM explains ONLY
```

**Critical principle**: The algorithm selects colleges. The LLM never does.

## Folder Structure

```
platform/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry
│   │   ├── config.py
│   │   ├── api/v1/                 # REST endpoints
│   │   ├── core/                   # Security, rate limit, audit
│   │   ├── engines/                # Layers 1-5 (deterministic)
│   │   ├── ml/                     # Training pipeline
│   │   ├── rag/                    # ChromaDB (Layer 6)
│   │   ├── llm/                    # Response gen (Layer 8)
│   │   ├── web_intel/              # Official sources (Layer 7)
│   │   ├── schemas/                # Pydantic models
│   │   └── services/               # Data service adapter
│   ├── tests/
│   └── requirements.txt
├── database/
│   └── schema.sql                  # PostgreSQL schema
├── frontend/                       # React + Vite dashboard
├── docs/
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
```

## Quick Start

### Backend (local)

```bash
cd platform/backend
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd platform/frontend
npm install
npm run dev
```

### Docker

```bash
cd platform
docker-compose up --build
```

### Train ML Models

```bash
cd platform/backend
python -m app.ml.train
```

### Run Tests

```bash
cd platform/backend
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/predict/recommend` | Deterministic recommendations |
| POST | `/api/v1/predict/preference-order` | KEA option entry list |
| POST | `/api/v1/predict/compare` | Compare colleges |
| POST | `/api/v1/predict/strategy` | Counselling strategy |
| GET | `/api/v1/colleges/search` | College explorer |
| GET | `/api/v1/colleges/{id}/cutoff-trends` | Historical cutoffs |
| POST | `/api/v1/chat/` | Chatbot (engine + LLM explain) |
| POST | `/api/v1/hostels/for-recommendations` | Verified hostels only |
| GET | `/api/v1/scholarships/eligible` | Scholarship checker |
| GET | `/api/v1/analytics/overview` | Dashboard stats |

## Issues Fixed

| Problem | Solution |
|---------|----------|
| LLM generates recommendations | Moved to Python engines (Layers 2-5) |
| City filter ignored | Hard constraint in Layer 4 |
| Budget ignored | Hard filter, never relaxed |
| Hostel mismatch | Hostels only for recommended colleges |
| Hallucinated hostel info | Database-only, never invented |
| Confidence always high | Based on data completeness + match count |

## Data Sources

- JSON: `college/data/Production_Ready_Colleges.json` (primary)
- ChromaDB: `college/backend/chroma_db/` (RAG only)
- PostgreSQL: schema ready, migration pending

## Legacy Integration

The existing Flask backend (`college/backend/app.py`) remains functional.
This platform is the new production path. Migrate endpoints gradually.
