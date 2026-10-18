import time
from typing import List, Dict, Any, Tuple
import pandas as pd

from backend.app.retrieval.base_retriever import BaseRetriever
from backend.app.rag.vector_store import VectorIndexManager

class DenseRetriever(BaseRetriever):
    """
    Conventional Dense RAG approach using SBERT (all-MiniLM-L6-v2) + FAISS similarity search.
    No explicit hard constraint filtering performed before generation.
    """
    def __init__(self, vector_store: VectorIndexManager, dataset: pd.DataFrame):
        super().__init__(dataset)
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, session_context: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()
        search_hits = self.vector_store.search(query, top_k=top_k)

        results = []
        result_scores = []
        for rank, (doc, score) in enumerate(search_hits, 1):
            if isinstance(doc, dict):
                item = dict(doc)
            else:
                item = {
                    "item_name": str(doc),
                    "price": 0.0,
                    "is_vegetarian": True,
                    "is_non_vegetarian": False,
                    "spice_level": "normal",
                    "cuisine": "General",
                    "description": str(doc)
                }
            item["retrieval_score"] = float(score)
            item["rank"] = rank
            results.append(item)
            result_scores.append(float(score))

        latency_ms = (time.time() - start_time) * 1000.0
        metadata = {
            "method": "Conventional Dense RAG",
            "latency_ms": round(latency_ms, 2),
            "scores": result_scores,
            "top_k": top_k
        }
        return results, metadata
