import hashlib
import json
import os
import sys
import time
import uuid
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.retrieval import HybridRetriever
from rag.memory import ConversationMemory
from rag.generation import generate_response
from rag.metrics import evaluate
from data.cleaner import load_and_clean_menus_from_json

_retriever: HybridRetriever | None = None
_sessions: dict[str, ConversationMemory] = {}

# Stores (query, context, response) per exchange so /api/evaluate can look them up.
# Capped at 200 entries to avoid unbounded memory growth.
_MAX_EXCHANGES = 200
_exchanges: OrderedDict[str, tuple[str, str, str]] = OrderedDict()

_BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
_INDEX_CACHE_DIR = os.path.join(_BACKEND_DIR, "index_cache")
_HASH_FILE = os.path.join(_INDEX_CACHE_DIR, "docs_hash.txt")


def _docs_hash(docs: list[str]) -> str:
    return hashlib.md5(json.dumps(docs, sort_keys=True).encode()).hexdigest()


def _index_is_valid(docs_hash: str) -> bool:
    if not os.path.exists(_HASH_FILE):
        return False
    try:
        with open(_HASH_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == docs_hash
    except Exception:
        return False


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is not None:
        return _retriever

    menu_path = os.path.join(_BACKEND_DIR, "menu")
    docs = load_and_clean_menus_from_json(menu_path)
    current_hash = _docs_hash(docs)

    os.makedirs(_INDEX_CACHE_DIR, exist_ok=True)

    if _index_is_valid(current_hash):
        print("Loading index from cache...")
        try:
            _retriever = HybridRetriever.load(_INDEX_CACHE_DIR)
        except Exception as e:
            print(f"Failed to load cached index ({e}). Rebuilding...")
            _retriever = HybridRetriever(docs)
            _retriever.save(_INDEX_CACHE_DIR)
            with open(_HASH_FILE, "w", encoding="utf-8") as f:
                f.write(current_hash)
    else:
        print("Building index (first run — will be cached for next time)...")
        _retriever = HybridRetriever(docs)
        _retriever.save(_INDEX_CACHE_DIR)
        with open(_HASH_FILE, "w", encoding="utf-8") as f:
            f.write(current_hash)

    return _retriever


def _get_or_create_session(session_id: str) -> ConversationMemory:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationMemory(max_turns=5)
    return _sessions[session_id]


def _store_exchange(exchange_id: str, query: str, context: str, response: str) -> None:
    if len(_exchanges) >= _MAX_EXCHANGES:
        _exchanges.popitem(last=False)  # evict oldest
    _exchanges[exchange_id] = (query, context, response)


def chat(query: str, session_id: str) -> dict:
    retriever = get_retriever()
    memory = _get_or_create_session(session_id)
    total_start = time.perf_counter()

    # Stage 1: Hybrid retrieval + reranking
    t0 = time.perf_counter()
    docs, retrieval_confidence = retriever.retrieve(query)
    retrieval_ms = int((time.perf_counter() - t0) * 1000)

    context = "\n\n".join(docs)

    # Stage 2: Generation
    t0 = time.perf_counter()
    response = generate_response(context, query, memory.format_for_prompt())
    generation_ms = int((time.perf_counter() - t0) * 1000)

    total_ms = int((time.perf_counter() - total_start) * 1000)
    memory.add(query, response)

    # Store exchange for on-demand evaluation
    exchange_id = str(uuid.uuid4())
    _store_exchange(exchange_id, query, context, response)

    return {
        "response": response,
        "exchange_id": exchange_id,
        "metrics": {
            "retrieval_confidence": retrieval_confidence,
            "latency": {
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "total_ms": total_ms,
            },
        },
    }


def evaluate_exchange(exchange_id: str) -> dict[str, float] | None:
    if exchange_id not in _exchanges:
        return None
    query, context, response = _exchanges[exchange_id]
    return evaluate(query, context, response)


def clear_session(session_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id].clear()


def get_session_history(session_id: str) -> list[tuple[str, str]]:
    if session_id not in _sessions:
        return []
    return _sessions[session_id].get_history()