import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# API Keys & LLM settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("gemini_token", ""))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Vector & Embeddings Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K", "5"))

# Hybrid Retrieval Weights: final_score = alpha * semantic + beta * keyword + gamma * constraint
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.5"))
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.2"))
CONSTRAINT_WEIGHT = float(os.getenv("CONSTRAINT_WEIGHT", "0.3"))

# Database & Directory Paths
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'restrobot.db'}")
RAW_DATA_DIR = BASE_DIR / "backend" / "data" / "menu"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
INDEX_CACHE_DIR = BASE_DIR / "backend" / "index_cache"
RESULTS_DIR = BASE_DIR / "results"
CHARTS_DIR = RESULTS_DIR / "charts"

# Ensure required runtime directories exist
INDEX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Conversation Settings
MAX_CONVERSATION_TURNS = 10
