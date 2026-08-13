# Production Roadmap

## Phase 1: Foundation (Complete)

- [x] 8-layer deterministic engine architecture
- [x] FastAPI backend with all core endpoints
- [x] PostgreSQL schema design
- [x] JSON data adapter (backward compatible)
- [x] ML training pipeline (RF, XGBoost, LightGBM)
- [x] Hard constraint filtering (city, budget, hostel)
- [x] React frontend dashboard skeleton
- [x] Docker Compose setup
- [x] Unit + integration tests
- [x] Security (rate limit, audit, JWT, prompt sanitization)

## Phase 2: Data Migration (Week 1-2)

- [ ] Seed PostgreSQL from JSON datasets
- [ ] ETL pipeline: KEA PDF → PostgreSQL + ChromaDB
- [ ] Switch `USE_JSON_DATA=false` in staging
- [ ] Data validation against official KEA cutoffs
- [ ] Automated nightly data refresh

## Phase 3: ML Accuracy (Week 2-3)

- [ ] Expand training data to 10 years of cutoffs
- [ ] Cross-validation benchmark (target 95%+ MAE accuracy)
- [ ] A/B test rule-based vs ML-blended probability
- [ ] Model registry in PostgreSQL
- [ ] Automated retraining on new cutoff data

## Phase 4: Frontend Polish (Week 3-4)

- [ ] Cutoff trend charts (Recharts)
- [ ] Admission probability visualization
- [ ] One-click PDF report generation
- [ ] Counselling simulator UI
- [ ] Mobile-responsive design
- [ ] Preference order drag-and-drop

## Phase 5: Production Hardening (Week 4-5)

- [ ] Redis-backed rate limiting
- [ ] Kubernetes deployment
- [ ] HTTPS + WAF
- [ ] Prometheus metrics + alerting
- [ ] Load testing (1000 concurrent users)
- [ ] Disaster recovery plan

## Phase 6: Advanced Features (Week 5-8)

- [ ] WhatsApp bot integration (reuse existing)
- [ ] Real-time KEA cutoff updates via web scraper
- [ ] Multi-exam support (JEE, NEET via same engine)
- [ ] Counselling session recording
- [ ] Parent/guardian dashboard
- [ ] Offline mode for rural students

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Recommendation accuracy | 95%+ | ~85% (rule-based) |
| City filter compliance | 100% | 100% (hard filter) |
| Budget filter compliance | 100% | 100% (hard filter) |
| Hostel hallucination rate | 0% | 0% (DB only) |
| API response time (p95) | < 500ms | ~200ms (JSON) |
| Uptime | 99.9% | N/A (dev) |

## Deprecation Plan

| Component | Status | Replacement |
|-----------|--------|-------------|
| Flask `app.py` monolith | Legacy | FastAPI platform |
| LLM-driven recommendations | Deprecated | Deterministic engine |
| SQLite | Legacy | PostgreSQL |
| Dual FastAPI backend | Deprecated | Unified platform |

Timeline: Flask remains as fallback for 4 weeks, then deprecated.
