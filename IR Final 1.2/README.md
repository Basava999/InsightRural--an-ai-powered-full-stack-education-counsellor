# InsightRural — AI-Powered College Admission Platform 🎓

![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)
![Python](https://img.shields.io/badge/Backend-Python%203.10%2B%20%7C%20Flask-blue)
![ML](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20RandomForest-orange)
![AI](https://img.shields.io/badge/AI-ChromaDB%20%7C%20LLaMA3%20%7C%20Groq-purple)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

> **InsightRural** is a Generative AI + Machine Learning platform for KCET/KEA, JEE, and NEET college admission counseling. It bridges the educational guidance gap for engineering and medical aspirants across India, with a focus on rural and underrepresented students.

---

## 🚀 Quick Start (Any Laptop — Windows / macOS / Linux)

### Prerequisites
- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- A terminal (PowerShell, CMD, bash, zsh)

### One-Command Setup

```bash
# 1. Clone the repo
git clone https://github.com/Basava999/final-year-genai-platform.git
cd final-year-genai-platform

# 2. Run setup (creates venv, installs all dependencies, copies .env)
python setup.py

# 3. (First time only) Add your free Groq API key to college/backend/.env
#    Get key at: https://console.groq.com → Free tier available
#    Set: GROQ_API_KEY=your_key_here

# 4. Start both backend + frontend
python setup.py --start
```

**App opens automatically at: http://localhost:8000**  
Backend API at: http://127.0.0.1:5000

---

### Manual Setup (Alternative)

```bash
# Backend
cd college/backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env         # then edit .env with your API keys
python app.py                # starts on http://127.0.0.1:5000

# Frontend (new terminal)
cd insightrural-frontend
python -m http.server 8000   # opens http://localhost:8000
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **ML College Predictor** | RandomForest + GradientBoosting trained on 15,000+ KEA cutoff records |
| 📋 **KEA Seat Simulation** | Full Karnataka reservation matrix: GM, SC, ST, 2A/2B/3A/3B, Rural 15%, KM 5%, 371-J |
| 🧠 **Risk & Regret Analyzer** | 11-dimensional profile analysis with 5-year ROI projections |
| 💬 **GenAI RAG Counselor** | ChromaDB + BM25 hybrid retrieval, LLaMA3 / Groq LLM, real-time SSE streaming |
| 🌏 **Multilingual** | Kannada, Hindi, English support via Sarvam AI |
| 📄 **PDF Auto-Pilot** | Scholarship essay generation + downloadable PDF report |
| 🏛️ **Counseling Suite** | KEA option entry generator, document checklist, round predictions |

---

## 🏗️ Architecture

```
insightrural-frontend/          ← Vanilla JS frontend (served on port 8000)
college/
  backend/
    app.py                      ← Flask gateway (60+ API routes, port 5000)
    ml_predictor.py             ← Hybrid ML prediction engine
    kea_allotment_engine.py     ← KEA seat allotment simulator
    rag_engine.py               ← BM25 + ChromaDB hybrid RAG
    llm_service.py              ← Ollama / Groq / OpenAI multi-LLM
    json_data_service.py        ← JSON-first data layer (222 colleges)
    engines/
      ranking_engine.py         ← Multi-criteria scoring
      constraint_filter.py      ← Branch/location filtering
    models/
      schemas.py                ← Pydantic v2 validation
    data/
      okf/colleges/             ← College JSON data (222 colleges)
      *.json                    ← Cutoffs, fees, scholarships, hostels
setup.py                        ← Cross-platform setup & launcher
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 2.3, FastAPI 0.104, Pydantic v2 |
| **ML** | Scikit-learn (RandomForest, GradientBoosting), NumPy, Pandas, Joblib |
| **AI / RAG** | ChromaDB, Sentence-Transformers, BM25, Ollama LLaMA3, Groq API |
| **Database** | SQLite (SQLAlchemy ORM), JSON file-based data service |
| **Frontend** | Vanilla JS/HTML/CSS, Progressive Web App (PWA) |
| **PDF** | FPDF2 |

---

## 📌 Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check |
| `GET` | `/api/colleges` | Searchable college directory |
| `POST` | `/api/predict/college` | ML-driven KCET predictions (Safe/Moderate/Dream) |
| `POST` | `/api/recommend/colleges` | Personalized college recommendations |
| `POST` | `/api/recommend/scholarships` | Scholarship matching |
| `POST` | `/api/chat` | RAG AI counselor chat |
| `POST` | `/api/chat/stream` | Streaming SSE chat |
| `POST` | `/api/documents/scan` | Document scanner (marksheet, caste cert) |
| `POST` | `/api/scholarships/generate-essay` | AI scholarship essay generator |
| `POST` | `/api/counseling/generate-options` | KEA option entry list |
| `POST` | `/api/auth/signup` | User registration |
| `POST` | `/api/auth/login` | User login (JWT) |

---

## ⚙️ Configuration (.env)

Copy `college/backend/.env.example` to `college/backend/.env` and fill in:

```env
# Required for AI chat features (free tier at console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# Optional — for offline AI (install Ollama + pull llama3)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Security key — change this in production!
JWT_SECRET_KEY=change_this_to_a_secure_random_secret
```

> **Without any API keys**: College recommendations, ML predictions, risk analysis, and the KEA simulator all work offline. Only the AI chat feature requires Groq or Ollama.

---

## 🔒 Security

- `.env` is gitignored — no secrets in the repo
- JWT-based auth for protected endpoints
- Pydantic v2 schemas validate all API inputs
- Multi-level fallback: ML Model → Rule Engine → Data Service

---

## 📄 License

Developed for final-year academic research and production demonstration (MSRIT Pradarshana 2026).
