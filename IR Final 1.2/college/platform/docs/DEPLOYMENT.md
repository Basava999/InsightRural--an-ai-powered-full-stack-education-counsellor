# Deployment Architecture

## Local Development

```bash
# Terminal 1: Backend
cd platform/backend
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd platform/frontend
npm install && npm run dev
```

## Docker Compose (Recommended)

```bash
cd platform
docker-compose up --build
```

Services:
- `backend`: FastAPI on port 8000
- `frontend`: Nginx on port 3000
- `postgres`: PostgreSQL 16 on port 5432
- `redis`: Rate limit cache (future)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | PostgreSQL connection |
| `USE_JSON_DATA` | true | Use JSON files (set false for PG) |
| `JWT_SECRET` | change-me | JWT signing key |
| `CHROMA_DIR` | ../backend/chroma_db | ChromaDB path |
| `ML_MODELS_DIR` | ../backend/models | ML artifacts |
| `CORS_ORIGINS` | localhost:3000,5173 | Allowed origins |
| `OLLAMA_URL` | localhost:11434 | Local LLM |
| `GROQ_API_KEY` | (empty) | Cloud LLM fallback |

## Production Checklist

- [ ] Set strong `JWT_SECRET`
- [ ] Enable PostgreSQL (`USE_JSON_DATA=false`)
- [ ] Run database migrations
- [ ] Seed PostgreSQL from JSON (`database/seed/`)
- [ ] Train ML models (`python -m app.ml.train`)
- [ ] Index ChromaDB documents
- [ ] Configure HTTPS reverse proxy (nginx/traefik)
- [ ] Enable Redis for distributed rate limiting
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation

## Kubernetes (Future)

```
platform/
├── k8s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-statefulset.yaml
│   └── ingress.yaml
```

## CI/CD Pipeline

1. **Lint**: ruff, eslint
2. **Test**: pytest, vitest
3. **Build**: Docker images
4. **Deploy**: staging → production
