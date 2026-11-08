# CHAPTER 6: SYSTEM DESIGN

---

## 6.1 Introduction

The system design of **InsightRural** represents a carefully engineered, multi-tier architecture that integrates modern Generative AI capabilities with traditional web application paradigms to deliver a comprehensive educational guidance platform for rural Karnataka students navigating the KCET (Karnataka Common Entrance Test) and KEA (Karnataka Examinations Authority) college admission process.

The platform's design philosophy is rooted in three core tenets: **(i) Offline-First Resilience** — ensuring the application remains functional in low-connectivity rural environments through Progressive Web Application (PWA) technology and multi-level AI fallback chains; **(ii) Data-Grounded Intelligence** — leveraging Retrieval-Augmented Generation (RAG) over ChromaDB vector stores to ensure all AI-generated guidance is anchored to verified, domain-specific datasets encompassing 228+ KEA colleges, fee structures, scholarship schemes, hostel data, and multi-year cutoff trends; and **(iii) Accessibility-Centric Design** — providing multilingual support, WhatsApp-based access, voice interaction capabilities, and a mobile-responsive PWA interface that can be installed as a native-like application on any smartphone.

The system comprises **15+ interconnected backend modules**, a **modular single-page frontend** with 19 JavaScript components, **7 ChromaDB vector collections**, an **SQLite relational database**, and a **dual-LLM orchestration pipeline** (Groq Cloud + Ollama Local) with automatic failover — collectively delivering over **25 RESTful API endpoints** that power features ranging from ML-based college seat prediction to AI-generated scholarship essays.

This chapter provides an exhaustive examination of the system's architectural decisions, component interactions, data flows, security measures, and scalability planning.

---

## 6.2 Architecture Design

### 6.2.1 Overall System Architecture

InsightRural employs a **Three-Tier Client-Server Architecture** augmented with an AI/ML intelligence layer, decomposed as follows:

| Tier | Component | Technology | Role |
|------|-----------|------------|------|
| **Presentation Tier** | PWA Frontend | HTML5, CSS3, Vanilla JS | User interface, offline caching, service worker |
| **Application Tier** | Flask REST API | Python 3.11, Flask 2.3 | Business logic, API routing, session management |
| **Intelligence Tier** | AI/ML Pipeline | Groq API, Ollama, ChromaDB, scikit-learn | LLM orchestration, RAG retrieval, ML prediction |
| **Data Tier** | Databases | SQLite (relational), ChromaDB (vector) | Structured data storage, semantic search indices |

### 6.2.2 Backend Architecture — Modular Microkernel Design

The backend follows a **Microkernel Architecture** pattern where `app.py` (1,322 lines) serves as the central kernel, dynamically loading 8 pluggable service modules at startup through Python's `try/except` import pattern. This design ensures **graceful degradation** — if any module (e.g., WhatsApp bot, PDF generator) fails to load due to missing dependencies, the core system continues operating with reduced functionality.

**Module Loading Architecture:**

```
app.py (Kernel)
 ├── rag_engine.py        → ChromaDB RAG Engine (832 lines)
 ├── llm_service.py       → Dual-LLM Orchestrator (628 lines)
 ├── ml_predictor.py      → KEA ML College Predictor (1,028 lines)
 ├── career_engine.py     → AI Career Counselor (303 lines)
 ├── prompt_templates.py  → LLM Prompt Engineering (443 lines)
 ├── counseling_service.py → KEA Counseling Guide (120 lines)
 ├── scholarship_service.py → Scholarship Essay AI + PDF (106 lines)
 ├── document_scanner.py  → Document OCR Scanner (101 lines)
 ├── whatsapp_bot.py      → WhatsApp Bot via Twilio (349 lines)
 ├── pdf_generator.py     → PDF Report Generator (338 lines)
 ├── models.py            → SQLAlchemy ORM Models (26 lines)
 └── db.py                → Database Configuration (24 lines)
```

Each module exposes a **singleton factory function** (e.g., `get_llm_service()`, `get_rag_engine()`, `get_predictor()`) ensuring single-instance resource management and lazy initialization.

### 6.2.3 AI Pipeline Architecture — Triple-Fallback LLM Orchestration

The most architecturally significant component is the **InsightRuralCounselor** class in `llm_service.py`, which orchestrates a triple-fallback LLM pipeline:

```
Student Query
     │
     ▼
[1] Flask receives query + student profile + chat history
     │
     ▼
[2] RAG Engine → ChromaDB cosine similarity search
    across 7 collections → returns top-8 relevant documents
     │
     ▼
[3] Prompt Builder → constructs structured prompt:
    System Persona + Student Profile JSON + RAG Context + Chat History
     │
     ▼
[4] LLM Fallback Chain:
    ┌──────────────────────────────────────────────┐
    │  Priority 1: Groq Cloud (LLaMA 3.3 70B)     │
    │  ↓ (if unavailable or fails)                 │
    │  Priority 2: Ollama Local (LLaMA 3)          │
    │  ↓ (if unavailable or fails)                 │
    │  Priority 3: RAG-Only Fallback (no LLM)      │
    └──────────────────────────────────────────────┘
     │
     ▼
[5] Token-by-token SSE stream → Frontend Chat UI
```

**Key Design Decisions:**

- **Groq Cloud as Primary**: Provides near-instant responses (1–3 seconds) using the `llama-3.3-70b-versatile` model via OpenAI-compatible API, ideal for production use.
- **Ollama Local as Fallback**: Runs LLaMA 3 entirely on-device via `http://localhost:11434`, ensuring complete data privacy — all student data stays on-device. No API keys required.
- **RAG-Only as Last Resort**: When both LLMs are unavailable, the system generates responses directly from ChromaDB search results, ensuring the platform never shows a blank response.

### 6.2.4 RAG Engine Architecture

The `RAGEngine` class (832 lines) manages 7 ChromaDB vector collections:

| Collection | Source Data | Documents Indexed | Purpose |
|------------|-----------|-------------------|---------|
| `colleges` | `college_master.json` (1.38 MB) | 228 colleges | College search, recommendations |
| `scholarships` | `scholarships.json` | 10+ schemes | Scholarship eligibility matching |
| `loans` | `education_loans.json` | 8+ loan schemes | Education loan comparison |
| `hostels` | `hostels.json` | 15+ hostels | Hostel availability and fees |
| `counseling` | `counseling_guide.json` | 20+ guide items | KEA process steps and FAQs |
| `cutoffs` | `cutoff_dataset.json` | Multi-year trends | 3-year cutoff trend analysis |
| `fees` | `Fee.json` | Fee structures | Category-wise fee comparison |

**Embedding Model**: `all-MiniLM-L6-v2` from the `sentence-transformers` library — a 384-dimensional transformer model optimized for semantic similarity, producing dense vector embeddings that enable cosine similarity search across all collections simultaneously.

**Search Strategy**: Cross-collection semantic search retrieves up to 3 results per collection, sorted by cosine distance, returning the top-8 most relevant documents. A TF-IDF keyword-scoring fallback is implemented when ChromaDB is unavailable.

---

## 6.3 Graphical User Interface

### 6.3.1 Component Design

The frontend is built as a **modular Single-Page Application (SPA)** using vanilla HTML5, CSS3, and JavaScript — deliberately avoiding heavy frameworks to minimize bundle size and ensure fast load times on low-bandwidth rural connections.

**UI Architecture:**

```
index.html (Shell — 314 lines)
 ├── Landing Page (Animated intro with particle effects)
 ├── Top Navigation Bar (Brand, theme toggle)
 ├── Sidebar Navigation (12 feature modules)
 ├── Main Content Area (Dynamic section rendering)
 │    ├── Chat Interface (AI conversational UI)
 │    ├── College Predictor (Multi-tab: Predict/Analytics/Compare/Simulator/Checklist)
 │    ├── Dashboard (Live statistics)
 │    ├── Scholarships Explorer
 │    ├── Hostels Explorer
 │    ├── Document Vault
 │    ├── Career Counselor
 │    ├── Voice Counselor
 │    ├── Document Scanner
 │    ├── Career Simulator
 │    ├── Video Counselor (Avatar)
 │    └── KEA Counseling Suite
 └── Modals (Profile editor, Login)
```

**19 JavaScript Component Modules:**

| Component File | Size | Responsibility |
|----------------|------|---------------|
| `predictor.js` | 58 KB | ML college prediction form, results rendering, analytics tabs |
| `hostel_explorer.js` | 31 KB | Hostel search, filtering, AI application letter generator |
| `career_simulator.js` | 30 KB | AI career path visualization with timeline milestones |
| `chat.js` | 29 KB | SSE streaming chat, message rendering, markdown parsing |
| `video_avatar.js` | 29 KB | AI video counselor with animated avatar |
| `sidebar.js` | 27 KB | Navigation, feature switching, responsive collapse |
| `document_scanner.js` | 26 KB | Camera-based OCR document scanning UI |
| `voice_counselor.js` | 25 KB | Speech-to-text and text-to-speech counselor |
| `landing.js` | 25 KB | Animated landing page with particle effects |
| `documents.js` | 19 KB | Document vault with local storage persistence |
| `progress.js` | 17 KB | Student progress tracker and milestones |
| `scholarships.js` | 16 KB | Scholarship search and eligibility matcher |
| `counseling_component.js` | 14 KB | KEA counseling process guide with steps |
| `dashboard.js` | 14 KB | Live statistics dashboard with charts |
| `modal.js` | 13 KB | Profile editor and login modals |
| `voice.js` | 11 KB | Voice input/output utilities |
| `scholarship_writer.js` | 9 KB | AI-powered scholarship essay generator |
| `state.js` | 5 KB | Global application state management |
| `pwa.js` | 10 KB | Service worker registration, install prompt |

**Design System:**

- **Typography**: Inter font family (weights 300–800) loaded from Google Fonts
- **Color Scheme**: Primary green (#10a37f), dark mode default (#0a0a0f background)
- **Styling**: 11 CSS files totaling 151+ KB — glassmorphism effects, smooth gradient transitions, and micro-animations
- **Responsiveness**: Mobile-first design with sidebar collapse for screens < 768px

---

## 6.4 Class Diagram and Classes

### 6.4.1 Backend Class Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py (Flask Kernel)                     │
│  Routes: 25+ API endpoints                                      │
│  Methods: college_to_dict(), fee_to_dict(), chat(), predict()    │
└──────────────┬──────────────────────────────────────┬────────────┘
               │                                      │
    ┌──────────▼──────────┐              ┌────────────▼────────────┐
    │ InsightRuralCounselor│              │    CollegePredictor     │
    │   (llm_service.py)   │              │   (ml_predictor.py)     │
    │──────────────────────│              │─────────────────────────│
    │- groq: GroqService   │              │- cutoff_data: List      │
    │- ollama: OllamaService│             │- college_data: List     │
    │- rag: RAGEngine      │              │- trend_models: Dict     │
    │- fallback: RAGFallback│             │- RESERVATION_QUOTAS     │
    │──────────────────────│              │─────────────────────────│
    │+ stream_response()   │              │+ predict()              │
    │+ generate_response() │              │+ calculate_kcet_rank()  │
    │+ generate()          │              │+ _predict_cutoff()      │
    │+ get_status()        │              │+ _apply_kea_reservation()│
    │+ _get_rag_context()  │              │+ _calculate_probability()│
    │+ _build_messages()   │              │+ _calculate_college_score()│
    └───┬─────────┬────────┘              │+ _generate_kea_option_sequence()│
        │         │                       │+ _generate_kea_guidance()│
  ┌─────▼───┐ ┌───▼──────┐               └─────────────────────────┘
  │GroqService│ │OllamaService│
  │──────────│ │────────────│            ┌─────────────────────────┐
  │- api_key │ │- host      │            │      RAGEngine          │
  │- model   │ │- model     │            │   (rag_engine.py)       │
  │- available│ │- available │            │─────────────────────────│
  │──────────│ │────────────│            │- embedding_model        │
  │+ generate()│ │+ generate()│           │- client: ChromaDB       │
  │+ stream() │ │+ stream()  │           │- collections: Dict      │
  └──────────┘ └────────────┘            │─────────────────────────│
                                         │+ search()               │
  ┌──────────────┐  ┌──────────────┐     │+ index_all()            │
  │ RAGFallback  │  │ CareerEngine │     │+ load_and_index_colleges()│
  │──────────────│  │──────────────│     │+ get_colleges_by_rank() │
  │- rag         │  │- CAREER_PROFILES│  │+ get_eligible_scholarships()│
  │+ generate()  │  │- ASSESSMENT_Q │   └─────────────────────────┘
  │+ _static_response()│ │+ process_responses()│
  └──────────────┘  │+ get_questions()│
                    └──────────────┘
```

### 6.4.2 ORM Data Models (SQLAlchemy)

```
┌────────────────────────┐        ┌────────────────────────────┐
│       College          │        │      FeeStructure          │
│────────────────────────│        │────────────────────────────│
│ id: String (PK)        │───FK──▶│ category: String (PK)      │
│ name: String (indexed) │        │ gm_and_others_above_income │
│ type: String           │        │ snq_quota: Integer         │
│ location: String (idx) │        │ sc_st_concession: Integer  │
│ affiliation: String    │        │ cat1_upto_2_5_lakhs: Int   │
│ hostel_available: Bool │        │ others_upto_10_lakhs: Int  │
│ branches: JSON         │        │ cat1_above_2_5_lakhs: Int  │
│ fee_category: String(FK)│       └────────────────────────────┘
│ cutoff_data: JSON      │
└────────────────────────┘
```

### 6.4.3 Key Classes Summary

| Class | Module | Lines | Purpose |
|-------|--------|-------|---------|
| `InsightRuralCounselor` | `llm_service.py` | 270 | Main AI pipeline orchestrator — manages RAG context retrieval, prompt construction, and triple-fallback LLM execution (Groq → Ollama → RAG) |
| `GroqService` | `llm_service.py` | 85 | Groq Cloud API wrapper — OpenAI-compatible HTTP client for LLaMA 3.3 70B with streaming SSE support |
| `OllamaService` | `llm_service.py` | 100 | Local Ollama HTTP API wrapper — communicates with on-device LLaMA 3 via localhost:11434 |
| `RAGFallback` | `llm_service.py` | 60 | Zero-LLM response generator — produces structured data responses using only RAG search results |
| `RAGEngine` | `rag_engine.py` | 832 | ChromaDB vector database manager — indexes 7 data collections and provides semantic search with `all-MiniLM-L6-v2` embeddings |
| `CollegePredictor` | `ml_predictor.py` | 960 | KEA-accurate ML prediction engine — simulates Serial Dictatorship algorithm with reservation logic, trend regression, and probability calculation |
| `CareerEngine` | `career_engine.py` | 303 | Aptitude-based career matcher — maps student traits to engineering branches via weighted scoring |
| `CollegeReportPDF` | `pdf_generator.py` | 235 | FPDF2-based PDF generator — produces formatted college recommendation reports |
| `WhatsAppBot` | `whatsapp_bot.py` | 349 | Twilio-integrated WhatsApp bot — processes natural language messages via regex pattern matching |
| `College` | `models.py` | 10 | SQLAlchemy ORM model for college data with JSON fields for branches and cutoffs |
| `FeeStructure` | `models.py` | 8 | SQLAlchemy ORM model for category-wise KEA fee structures |

---

## 6.5 Sequence Diagram

### 6.5.1 AI Chat Query — End-to-End Sequence

```
Student          Frontend           Flask API        RAG Engine      LLM Service       Groq/Ollama
  │                  │                  │                │                │                │
  │ Types question   │                  │                │                │                │
  │─────────────────▶│                  │                │                │                │
  │                  │ POST /api/chat/stream             │                │                │
  │                  │ {message, profile, history}       │                │                │
  │                  │─────────────────▶│                │                │                │
  │                  │                  │ search(query)  │                │                │
  │                  │                  │───────────────▶│                │                │
  │                  │                  │                │ ChromaDB       │                │
  │                  │                  │                │ cosine search  │                │
  │                  │                  │                │ (7 collections)│                │
  │                  │                  │  top-8 docs    │                │                │
  │                  │                  │◀───────────────│                │                │
  │                  │                  │                │                │                │
  │                  │                  │ _build_messages(profile+RAG+history)             │
  │                  │                  │───────────────────────────────▶│                │
  │                  │                  │                │                │                │
  │                  │                  │                │  stream(messages)               │
  │                  │                  │                │                │───────────────▶│
  │                  │                  │                │                │  token stream  │
  │                  │                  │                │                │◀───────────────│
  │                  │                  │   SSE: data: {"chunk": token}  │                │
  │                  │                  │◀──────────────────────────────│                │
  │  Token rendered  │◀─────────────────│                │                │                │
  │  in chat bubble  │                  │                │                │                │
  │                  │   SSE: data: {"done": true}       │                │                │
  │                  │◀─────────────────│                │                │                │
  │ Complete response│                  │                │                │                │
  │◀─────────────────│                  │                │                │                │
```

### 6.5.2 ML College Prediction — End-to-End Sequence

```
Student          Frontend           Flask API       CollegePredictor     Data Files
  │                  │                  │                │                    │
  │ Fills form       │                  │                │                    │
  │ (rank, category, │                  │                │                    │
  │  branches)       │                  │                │                    │
  │─────────────────▶│                  │                │                    │
  │                  │ POST /api/predict/college         │                    │
  │                  │─────────────────▶│                │                    │
  │                  │                  │ get_predictor() │                    │
  │                  │                  │───────────────▶│                    │
  │                  │                  │                │ Load cutoff_dataset│
  │                  │                  │                │ + college_master   │
  │                  │                  │                │───────────────────▶│
  │                  │                  │                │◀───────────────────│
  │                  │                  │                │                    │
  │                  │                  │                │ For each college:  │
  │                  │                  │                │  1. Category cutoff│
  │                  │                  │                │  2. OBC relaxation │
  │                  │                  │                │  3. Reservation    │
  │                  │                  │                │  4. Trend predict  │
  │                  │                  │                │  5. Probability    │
  │                  │                  │                │  6. Fee & budget   │
  │                  │                  │                │  7. Score & rank   │
  │                  │                  │                │                    │
  │                  │                  │  {predictions, │                    │
  │                  │                  │   option_sequence,                  │
  │                  │                  │   guidance}     │                    │
  │                  │                  │◀───────────────│                    │
  │                  │ JSON Response    │                │                    │
  │  Results render  │◀─────────────────│                │                    │
  │  (cards, charts) │                  │                │                    │
  │◀─────────────────│                  │                │                    │
```

---
