import time
import re
from typing import List, Dict, Any, Tuple
import pandas as pd
from rank_bm25 import BM25Okapi
from backend.app.retrieval.base_retriever import BaseRetriever

def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

class KeywordRetriever(BaseRetriever):
    """
    Genuine Lexical / Keyword Retrieval baseline using BM25Okapi algorithm.
    Strictly NO vector search or SBERT embeddings used inside this module.
    """
    def __init__(self, dataset: pd.DataFrame):
        super().__init__(dataset)
        self.corpus = self.dataset["document_text"].tolist() if "document_text" in self.dataset.columns else []
        self.tokenized_corpus = [tokenize(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus) if self.tokenized_corpus else None

    def retrieve(self, query: str, top_k: int = 5, session_context: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()
        if not self.bm25 or self.dataset.empty:
            return [], {"latency_ms": 0.0, "scores": []}

        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        result_scores = []
        for rank, idx in enumerate(top_indices, 1):
            if scores[idx] > 0.0 or rank == 1:
                row = self.dataset.iloc[idx].to_dict()
                row["retrieval_score"] = float(scores[idx])
                row["rank"] = rank
                results.append(row)
                result_scores.append(float(scores[idx]))

        latency_ms = (time.time() - start_time) * 1000.0
        metadata = {
            "method": "Keyword (BM25)",
            "latency_ms": round(latency_ms, 2),
            "scores": result_scores,
            "top_k": top_k
        }
        return results, metadata
