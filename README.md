# RestroBot: A Comparative Study of Keyword Retrieval, Dense RAG, and Constraint-Aware Hybrid RAG for Conversational Restaurant Information Retrieval

## Abstract
Conversational restaurant information retrieval presents unique challenges due to multi-faceted user constraints including numeric price limits, dietary preferences (vegetarian vs. non-vegetarian), spice levels, and location boundaries. Traditional Keyword Retrieval (BM25) struggles with semantic nuance, while Conventional Dense RAG often suffers from semantic drift where numeric and categorical hard constraints are ignored. This research presents **RestroBot**, a novel conversational framework introducing **Constraint-Aware Hybrid RAG**. We empirically evaluate all three approaches on a standardized benchmark suite.

---

## 1. Problem Statement & Research Gap
Standard dense retrieval models (e.g. SBERT embeddings with FAISS vector search) map textual chunks into continuous vector spaces. While excellent at conceptual similarity (e.g. mapping "spicy snack" to "hot wings"), dense embeddings fail to enforce discrete hard constraints (e.g. returning a ₹220 chicken item when the query specifies "vegetarian under ₹200"). Keyword retrieval (BM25) provides exact token matching but lacks semantic generalization.

**Research Question:**
> *"Does Constraint-Aware Hybrid RAG improve retrieval relevance and constraint satisfaction compared with Keyword-Based Retrieval and Conventional Dense RAG for conversational restaurant information retrieval?"*

---

## 2. System Architecture

```
DATA SOURCES (JSON / CSV / Scraper Adapters)
    ↓
DATA CLEANING & NORMALIZATION (Normalizers: Price, Diet, Spice, Cuisine)
    ↓
STRUCTURED RESTAURANT & MENU DATABASE (SQLite / SQLAlchemy ORM)
    ↓
EMBEDDINGS GENERATION (SentenceTransformers `all-MiniLM-L6-v2`)
    ↓
FAISS VECTOR INDEX & BM25 INDEX
    ↓
USER NATURAL LANGUAGE QUERY
    ↓
CONSTRAINT EXTRACTION (Hard Numerical & Categorical Constraints vs Soft Preferences)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ RETRIEVAL METHOD SELECTION                                  │
│                                                             │
│ 1. Keyword Retrieval (BM25 Lexical Baseline)                │
│ 2. Conventional Dense RAG (SBERT + FAISS Semantic Baseline) │
│ 3. Constraint-Aware Hybrid RAG (Proposed Approach)          │
└─────────────────────────────────────────────────────────────┘
    ↓
HYBRID SCORING & HARD CONSTRAINT VALIDATION
    final_score = α * norm_semantic + β * norm_keyword + γ * constraint_score
    ↓
CONTEXT CONSTRUCTION & PROMPT ENGINEERING
    ↓
LLM RESPONSE GENERATION (Gemini 2.5 Flash / Local Ollama)
    ↓
EVALUATION FRAMEWORK & RESEARCH DASHBOARD
```

---

## 3. Comparative Approaches Overview

### Baseline 1: Keyword Retrieval (BM25)
- Pure lexical matching using BM25Okapi algorithm over tokenized menu titles and descriptions.
- Strictly no vector embeddings or semantic search used inside this engine.

### Baseline 2: Conventional Dense RAG
- Query encoded via `SentenceTransformers(all-MiniLM-L6-v2)`.
- Nearest neighbor search over FAISS vector store (`IndexFlatIP`).
- No explicit hard constraint filtering performed prior to LLM generation.

### Proposed Approach: Constraint-Aware Hybrid RAG
- **Query Understanding:** Extracts hard constraints (`dietary_preference`, `max_price`, `min_price`, `spice_level`, `restaurant_name`, `category`) and soft preferences.
- **Candidate Pool Generation:** Fetches candidate pool from both FAISS and BM25.
- **Hard Constraint Validation:** `ConstraintValidator` enforces discrete filtering (e.g., rejecting non-veg items for veg queries).
- **Transparent Hybrid Scoring:**
  $$\text{final\_score} = \alpha \cdot \text{norm\_semantic} + \beta \cdot \text{norm\_keyword} + \gamma \cdot \text{constraint\_score}$$
- **Re-ranking & Context Construction:** Top validated items formatted into prompt for Gemini API.

---

## 4. Key Technologies
- **Frontend:** React, Vite, JavaScript, Custom Dark-Mode UI CSS (100% Streamlit-free)
- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2
- **Vector Search & RAG:** SentenceTransformers (`all-MiniLM-L6-v2`), FAISS-CPU (`faiss.IndexFlatIP`), Rank-BM25 (`rank_bm25`)
- **LLM:** Gemini API (`google-genai`), optional Ollama LLaMA
- **Database:** SQLite (development), PostgreSQL ready
- **Evaluation & Visualization:** Matplotlib (publication-quality charts), Pytest, Pandas, NumPy

---

## 5. Project Directory Structure
```
restrobot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Environment settings & weights
│   │   ├── api/                 # REST routers (/chat, /compare, /restaurants, /evaluation)
│   │   ├── models/              # SQLAlchemy database ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Conversation memory manager
│   │   ├── retrieval/           # BM25, Dense RAG, and Hybrid retrievers
│   │   ├── rag/                 # SBERT embeddings, FAISS vector store, context builder
│   │   ├── constraints/         # Extractor & validator engines
│   │   └── llm/                 # Gemini API & Ollama provider abstractions
│   ├── ingestion/               # Loaders, cleaners, normalizers, scraper adapters
│   └── data/                    # Raw menu JSONs & sample datasets
├── frontend/
│   ├── src/
│   │   ├── components/          # Header, Sidebar, ItemCard, CompareView, MessageItem
│   │   ├── pages/               # ChatPage, EvaluationPage (Research Dashboard)
│   │   ├── services/            # REST API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── experiments/
│   ├── benchmark/               # Benchmark query set (benchmark_queries.json)
│   ├── metrics.py               # Precision@K, Recall@K, MRR, CSR metrics
│   ├── visualization.py         # Matplotlib chart generator
│   └── run_experiment.py        # Automated benchmark runner script
├── results/                     # JSON/CSV metrics & generated PNG charts
├── tests/                       # Automated unit test suite (pytest)
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Clone & Configure Environment
```bash
cp .env.example .env
# Edit .env to add your GEMINI_API_KEY (optional, fallback engine active if unconfigured)
```

### Step 2: Backend Setup & Execution
```bash
# Navigate to backend directory
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
FastAPI interactive docs will be available at `http://127.0.0.1:8000/docs`.

### Step 3: Frontend Setup & Execution
```bash
# In a new terminal, navigate to frontend directory
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 7. Running Benchmark Experiments & Evaluation

To execute the automated evaluation suite across all three approaches:

```bash
python experiments/run_experiment.py
```

This generates:
- `results/keyword_results.json`
- `results/dense_rag_results.json`
- `results/hybrid_results.json`
- `results/metrics.json`
- `results/comparison.csv`
- `results/charts/precision_recall_mrr_comparison.png`
- `results/charts/constraint_satisfaction_rate.png`
- `results/charts/latency_breakdown.png`

View these metrics interactively on the frontend Research Dashboard at `/evaluation`.

---

## 8. Representative Demonstration Queries

1. **Price & Dietary Constraint:**
   `"Show vegetarian food under ₹200"`
2. **Multi-Constraint:**
   `"Find spicy non-veg rolls under ₹150"`
3. **Restaurant & Dietary Constraint:**
   `"Show me vegetarian options from KFC under ₹200"`
4. **Category & Price Constraint:**
   `"Show biryani under ₹250"`
5. **Location & Category Constraint:**
   `"Find pizza under ₹300 near Delhi"`
6. **Conversational Follow-Up:**
   - Turn 1: `"Show vegetarian food under ₹200"`
   - Turn 2: `"Only spicy ones"` (demonstrates session memory context inheritance)

---

## 9. API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | GET | Health check status |
| `/api/chat` | POST | Single retrieval approach conversation endpoint |
| `/api/compare` | POST | Compare All mode endpoint (runs all 3 pipelines on same query) |
| `/api/restaurants` | GET | List all restaurants & menu stats |
| `/api/menu/{restaurant_id}`| GET | Get menu items for a restaurant |
| `/api/evaluation/results` | GET | Retrieve benchmark evaluation metrics & chart paths |
| `/api/evaluation/run` | POST | Trigger background benchmark evaluation run |

---

## 10. Research Findings & Conclusion
Empirical evaluation demonstrates that:
1. **Keyword Retrieval (BM25)** achieves low latency but suffers from zero semantic generalization.
2. **Conventional Dense RAG** achieves high semantic similarity but frequently returns constraint-violating items (e.g. non-veg items when vegetarian is requested under a tight price cap).
3. **Constraint-Aware Hybrid RAG** achieves a **100% Constraint Satisfaction Rate (CSR)** while maintaining high Precision@5 and MRR, proving that explicitly validating hard numerical and categorical constraints prior to re-ranking and generation significantly enhances reliability in domain-specific conversational RAG systems.
