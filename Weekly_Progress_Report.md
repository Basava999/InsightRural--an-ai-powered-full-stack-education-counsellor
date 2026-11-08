# INSIGHTRURAL: WEEKLY PROGRESS REPORT

**Project Duration:** 9 Weeks  
**Team Size:** 4 Members  

### Team Roles & Responsibilities:
* **Member 1 (Frontend Developer):** Focuses on Progressive Web App (PWA) architecture, Vanilla JS/CSS UI, chat interface, SSE streaming, and animations.
* **Member 2 (Backend Developer):** Focuses on Flask REST APIs, SQLite integration, server routing, and FPDF generation.
* **Member 3 (AI / Vector DB Engineer):** Focuses on ChromaDB embeddings, RAG pipeline, Groq Cloud logic, and offline Ollama LLM integration.
* **Member 4 (Machine Learning Engineer):** Focuses on Scikit-Learn predictive modeling, KEA algorithms, cutoff regressions, and data mapping.

---

### WEEK 1: Project Initiation & Data Collection
* **Member 1:** Conducted UI/UX research. Defined the requirement for a lightweight, dependency-free Vanilla JS frontend to ensure operation on legacy rural hardware. Created basic wireframe sketches.
* **Member 2:** Initialized the Python Flask backend environment. Drafted the base relational schemas for SQLite to store college attributes and fee structures.
* **Member 3:** Comparative analysis of Generative AI frameworks. Selected Groq for high-speed cloud inference and Ollama for edge-based fallback. Planned the architecture for the Retrieval-Augmented Generation (RAG) system.
* **Member 4:** Commenced massive web-scraping and data collection. Gathered 3 years of historical KCET cutoff data, college codes, and branch matrices directly from KEA records.

### WEEK 2: Backend Scaffolding & Initial Modeling
* **Member 1:** Developed the structural HTML5/CSS3 layouts for the platform. Built the responsive sidebar navigation, landing page skeleton, and setup CSS variables for light/dark mode themes.
* **Member 2:** Created the foundational Flask REST API endpoints. Successfully established the database connection pool and built CRUD routes for retrieving basic university JSON data.
* **Member 3:** Configured a local instance of ChromaDB. Began testing the `all-MiniLM-L6-v2` sentence-transformer model to convert sample text into 384-dimensional dense vectors.
* **Member 4:** Cleaned raw scraped data using Python Pandas. Formatted scattered tables into highly structured master datasets (e.g., `cutoff_dataset.json`, `Fee.json`).

### WEEK 3: Core Interface & Database Injection
* **Member 1:** Engineered the core conversational "chat-bubble" user interface. Handled dynamic CSS resizing for text areas and configured local state management (`state.js`).
* **Member 2:** Fully populated the SQLite database utilizing SQLAlchemy. Inserted verified data for exactly 228 Karnataka engineering colleges mapping branches to institutional codes.
* **Member 3:** Transformed the cleaned KEA JSONs into embedded chunks and successfully ingested them across 7 distinct ChromaDB collections (fees, hostels, cutoffs).
* **Member 4:** Prototyped the initial Linear Regression machine learning model using Scikit-Learn to predict 2025 cutoff trends based on 2022-2024 historical shifts.

### WEEK 4: LLM Orchestration & ML Predictor Logic (Part 1)
* **Member 1:** Implemented a real-time Markdown parsing script within the chat UI to render structured lists, bold text, and HTML tables outputted by the AI.
* **Member 2:** Built Python orchestration classes to handle complex user contexts, allowing the backend to temporarily memorize student ranks/preferences during sessions.
* **Member 3:** Developed the `InsightRuralCounselor` class. Wrote the dual-LLM logic that natively catches Groq HTTP timeouts and redirects identical prompts to the offline Ollama daemon (`localhost:11434`).
* **Member 4:** Retrained the ML cutoff model by mathematically injecting KEA reservation scalers (applying precise weighted multipliers for GM, SC, ST, Rural, Kannada Medium, and HK-371J quotas).

### WEEK 5: System Integration & SSE Streaming
* **Member 1:** Refactored the frontend chat `fetch()` scripts to ingest `text/event-stream` packets, enabling the visual real-time "typing" effect associated with Modern AI.
* **Member 2:** Configured Flask generators using the `yield` command to stream Server-Sent Events (SSE) back to the client directly from the LLM endpoint.
* **Member 3:** Completed deep Prompt Engineering. Force-bounded the LLM to prioritize the fetched ChromaDB RAG chunk arrays to strictly eliminate mathematical hallucinations regarding college fees.
* **Member 4:** Built the simulation logic for the KEA Serial Dictatorship seat allotment algorithm, translating predicted cutoff ranks into categorical percentage bounds (Very Safe to Long Shot).

### WEEK 6: PWA Features & Dashboard Modules
* **Member 1:** Transformed the website into a Progressive Web App (PWA). Configured the `manifest.json` and active Service Workers to cache critical CSS/JS components enabling offline viability.
* **Member 2:** Constructed complex SQL aggregate queries and exposed `/api/statistics` endpoints for the real-time Live Dashboard.
* **Member 3:** Thoroughly load-tested the edge-computing capabilities ensuring the LLaMA 3 8B model could operate solely on localized CPU/RAM without catastrophic timeout.
* **Member 4:** Designed a custom composite scoring system combining admission probability (40%), college prestige (25%), fees (15%), and preferences (20%) into a unified ROI "Match Index".

### WEEK 7: Scholarship Autopilot & Additional Utilities
* **Member 1:** Designed detailed UI panels for the ML College Predictor, the Scholarship Autopilot, and the KEA Counseling guide tabs. 
* **Member 2:** Utilized the `FPDF2` Python library to dynamically ingest student demographic data and output correctly formatted, professional PDF scholarship applications.
* **Member 3:** Injected generative templates instructing the LLM to autonomously write hyper-personalized soft-skills essays (SOPs) for specific scholarship grants.
* **Member 4:** Conducted rigorous ML back-testing by feeding the system 2023 cutoff data and validating its predictive success rate against actual 2024 KEA allotment results.

### WEEK 8: UI Polishing, Bug Fixing, and Optimization
* **Member 1:** Overhauled the application's aesthetic. Added HTML5 Canvas particle/network animations and live-ticking counting banners to the landing page to invoke a premium, trust-building experience.
* **Member 2:** Improved backend payload times by truncating overly large JSON responses into paginated clusters and resolving localized routing bugs.
* **Member 3:** Optimized Cosine Similarity search parameters. Calibrated the RAG system to utilize precisely `Top-8` document chunks to prevent maximum token context limit overflow in the LLM.
* **Member 4:** Resolved mathematical edge-case errors where specific overlapping reservations (e.g., Rural + 371J combined) caused extreme deviations in ML percentage forecasting.

### WEEK 9: Final Quality Assurance, Testing & Presentation
* **Member 1:** Ran Google Lighthouse accessibility audits. Confirmed the PWA installability hooks correctly prompted "Add to Home Screen" on standard Android devices with 100% responsiveness.
* **Member 2:** Compiled all internal codebase logic into final `README.md` and `DEPLOYMENT.md` files. Standardized `requirements.txt` to ensure strict environment replicability.
* **Member 3:** Conducted aggressive red-team testing of the Chat AI, actively trying to induce hallucinatory answers regarding fees; confirmed the strict RAG pipeline held bounds securely.
* **Member 4:** Verified total algorithmic adherence of the College Predictor logic against official Karnataka Examination Authority guidelines outlined in their official documentation.
