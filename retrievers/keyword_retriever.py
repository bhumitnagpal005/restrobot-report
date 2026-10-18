import time
import re
import pandas as pd
from rank_bm25 import BM25Okapi
import config

def tokenize(text: str) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    return re.findall(r"\w+", text.lower())

class KeywordRetriever:
    """
    Model 1: Lexical / Keyword-Based Retrieval Baseline using BM25Okapi.
    Strictly NO SBERT, FAISS, or vector embeddings used inside this model.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.corpus = self.df["document_text"].tolist() if "document_text" in self.df.columns else []
        self.tokenized_corpus = [tokenize(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus) if self.tokenized_corpus else None

    def retrieve(self, query: str, top_k: int = config.FINAL_RETRIEVAL_K) -> dict:
        t0 = time.perf_counter()
        
        tokenized_query = tokenize(query)
        if not self.bm25 or not tokenized_query:
            return {
                "approach": "Keyword Retrieval (BM25)",
                "query": query,
                "retrieved_items": [],
                "scores": [],
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        scores = self.bm25.get_scores(tokenized_query)
        top_indices = scores.argsort()[::-1][:min(top_k, len(self.df))]

        retrieved_items = []
        result_scores = []

        for rank, idx in enumerate(top_indices, 1):
            score = float(scores[idx])
            item = self.df.iloc[idx].to_dict()
            item["retrieval_score"] = round(score, 4)
            item["rank"] = rank
            retrieved_items.append(item)
            result_scores.append(round(score, 4))

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "approach": "Keyword Retrieval (BM25)",
            "query": query,
            "retrieved_items": retrieved_items,
            "scores": result_scores,
            "latency_ms": latency_ms
        }
