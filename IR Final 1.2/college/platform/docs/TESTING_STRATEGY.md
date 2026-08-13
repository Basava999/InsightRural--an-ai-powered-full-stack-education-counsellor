# Testing Strategy

## Test Pyramid

```
        /  E2E  \          ← Playwright (future)
       / Integration \     ← test_api.py
      /    Unit Tests  \   ← test_engines.py
```

## Current Test Coverage

### Unit Tests (`tests/test_engines.py`)

| Test | Validates |
|------|-----------|
| `test_city_filter_never_relaxes` | Bangalore filter excludes Haveri |
| `test_budget_filter` | Colleges above budget removed |
| `test_safe_tier` | Probability > 80% for good ranks |
| `test_ambitious_tier` | Probability < 50% for bad ranks |
| `test_bangalore_filter_no_haveri` | End-to-end city constraint |
| `test_budget_respected` | End-to-end budget constraint |
| `test_confidence_not_always_high` | Confidence varies with data |
| `test_hostels_only_for_recommended` | Hostel scope enforcement |

### Integration Tests (`tests/test_api.py`)

| Test | Validates |
|------|-----------|
| `test_health` | Service availability |
| `test_recommend_endpoint` | API contract |
| `test_city_constraint` | Filter via HTTP |
| `test_chat_endpoint` | Chat uses deterministic engine |

## Running Tests

```bash
cd platform/backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v --tb=short
```

## Future Tests

- [ ] ML pipeline accuracy benchmarks (target 95%+)
- [ ] RAG retrieval precision tests
- [ ] Load testing (locust, 100 concurrent users)
- [ ] Prompt injection regression tests
- [ ] PostgreSQL migration tests
- [ ] Frontend component tests (Vitest)
- [ ] E2E flows (Playwright)

## Accuracy Validation

Compare engine output against known KEA 2024 cutoff data:

```bash
python -m app.ml.train  # Train models
pytest tests/test_engines.py -k "bangalore" -v
```

Target: 95%+ recommendation accuracy on held-out cutoff data.
