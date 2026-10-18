import time
import pandas as pd
import config
from embeddings.faiss_index import FAISSIndexManager

class DenseRetriever:
    """
    Model 2: Conventional Dense RAG Baseline using SBERT (all-MiniLM-L6-v2) + FAISS similarity search.
    """
    def __init__(self, faiss_manager: FAISSIndexManager, df: pd.DataFrame = None):
        self.faiss_manager = faiss_manager
        self.df = df

    def retrieve(self, query: str, top_k: int = config.FINAL_RETRIEVAL_K) -> dict:
        t0 = time.perf_counter()
        
        search_hits = self.faiss_manager.search(query, top_k=top_k)

        retrieved_items = []
        result_scores = []

        for rank, (doc, score) in enumerate(search_hits, 1):
            item = dict(doc) if isinstance(doc, dict) else {"document_text": str(doc)}
            item["retrieval_score"] = round(float(score), 4)
            item["rank"] = rank
            retrieved_items.append(item)
            result_scores.append(round(float(score), 4))

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "approach": "Dense RAG (SBERT + FAISS)",
            "query": query,
            "retrieved_items": retrieved_items,
            "scores": result_scores,
            "latency_ms": latency_ms
        }
