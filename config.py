"""
Central Configuration for RestroBot Research Project.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INDEX_CACHE_DIR = BASE_DIR / "index_cache"
EVALUATION_DIR = BASE_DIR / "evaluation"
RESULTS_DIR = EVALUATION_DIR / "results"

PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "vellore_restaurants.csv"
BENCHMARK_CSV_PATH = EVALUATION_DIR / "benchmark_queries.csv"

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, INDEX_CACHE_DIR, EVALUATION_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Location
CITY_NAME = "Vellore"
LOCATION_DEFAULT = "Vellore, India"

# Retrieval & Vector Search Settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Retrieval Top-K Defaults
INITIAL_CANDIDATE_K = 20
FINAL_RETRIEVAL_K = 5

# Hybrid Reranking Weights: Alpha (Semantic) + Beta (Constraint) + Gamma (Metadata)
WEIGHT_ALPHA = 0.50  # Semantic similarity weight
WEIGHT_BETA = 0.35   # Constraint satisfaction weight
WEIGHT_GAMMA = 0.15  # Metadata relevance weight

# LLM Generation Settings
LLM_CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
]
LLM_TEMPERATURE = 0.2
LLM_MAX_OUTPUT_TOKENS = 800

# Conversation Memory
MAX_CONVERSATION_TURNS = 5
