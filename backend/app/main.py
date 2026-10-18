import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import config
from backend.app.models.database import init_db, SessionLocal
from backend.ingestion.loaders import DataLoaderAdapter
from backend.app.rag.vector_store import VectorIndexManager
from backend.app.retrieval.keyword_retriever import KeywordRetriever
from backend.app.retrieval.dense_retriever import DenseRetriever
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.api import health, chat, compare, restaurants, evaluation

# Global application state for pre-warmed engines
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing RestroBot FastAPI server...")
    init_db()
    
    db = SessionLocal()
    try:
        loader = DataLoaderAdapter(config.RAW_DATA_DIR)
        df_dataset = loader.seed_database(db)
    finally:
        db.close()

    print(f"Dataset pre-loaded with {len(df_dataset)} menu items across restaurants.")

    # Initialize FAISS Vector Store Index
    vector_store = VectorIndexManager(config.INDEX_CACHE_DIR)
    if not vector_store.load():
        documents = []
        for _, row in df_dataset.iterrows():
            documents.append(row.to_dict())
        vector_store.build(documents)

    # Initialize retrieval engines
    kw_retriever = KeywordRetriever(df_dataset)
    dense_retriever = DenseRetriever(vector_store, df_dataset)
    hybrid_retriever = HybridRetriever(kw_retriever, dense_retriever, df_dataset)

    app_state["df_dataset"] = df_dataset
    app_state["vector_store"] = vector_store
    app_state["kw_retriever"] = kw_retriever
    app_state["dense_retriever"] = dense_retriever
    app_state["hybrid_retriever"] = hybrid_retriever

    print("RestroBot retrieval engines pre-warmed and operational!")
    yield
    print("Shutting down RestroBot server...")

app = FastAPI(
    title="RestroBot RAG Research Platform API",
    description="Backend REST API for comparative study of Keyword, Dense RAG, and Constraint-Aware Hybrid RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount generated chart images statically so frontend can display them directly
if config.CHARTS_DIR.exists():
    app.mount("/charts", StaticFiles(directory=str(config.CHARTS_DIR)), name="charts")

# Include API routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(compare.router)
app.include_router(restaurants.router)
app.include_router(evaluation.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
