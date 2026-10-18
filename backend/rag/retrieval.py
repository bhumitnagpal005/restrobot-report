import json
import math
import os
import pickle

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

_DENSE_MODEL = "all-MiniLM-L6-v2"
_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class HybridRetriever:
    """
    Two-stage retriever:
      Stage 1 — Hybrid: dense (FAISS) + sparse (BM25) fused via Reciprocal Rank Fusion
      Stage 2 — Rerank: cross-encoder narrows candidates to top_k_final
    """

    def __init__(self, documents: list[str]):
        self.documents = documents
        self._build_dense_index()
        self._build_bm25_index()
        self.reranker = CrossEncoder(_RERANKER_MODEL)

    # ------------------------------------------------------------------ #
    # Index construction                                                 #
    # ------------------------------------------------------------------ #

    def _build_dense_index(self) -> None:
        self.embedder = SentenceTransformer(_DENSE_MODEL)
        embeddings = self.embedder.encode(self.documents, show_progress_bar=True)
        self.embeddings = np.array(embeddings, dtype="float32")
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def _build_bm25_index(self) -> None:
        tokenized = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    # ------------------------------------------------------------------ #
    # Index persistence                                                  #
    # ------------------------------------------------------------------ #

    def save(self, cache_dir: str) -> None:
        os.makedirs(cache_dir, exist_ok=True)
        faiss.write_index(self.index, os.path.join(cache_dir, "faiss.index"))
        np.save(os.path.join(cache_dir, "embeddings.npy"), self.embeddings)
        with open(os.path.join(cache_dir, "bm25.pkl"), "wb") as f:
            pickle.dump(self.bm25, f)
        with open(os.path.join(cache_dir, "documents.json"), "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False)

    @classmethod
    def load(cls, cache_dir: str) -> "HybridRetriever":
        instance = cls.__new__(cls)
        instance.index = faiss.read_index(os.path.join(cache_dir, "faiss.index"))
        instance.embeddings = np.load(os.path.join(cache_dir, "embeddings.npy"))
        with open(os.path.join(cache_dir, "bm25.pkl"), "rb") as f:
            instance.bm25 = pickle.load(f)
        with open(os.path.join(cache_dir, "documents.json"), encoding="utf-8") as f:
            instance.documents = json.load(f)
        instance.embedder = SentenceTransformer(_DENSE_MODEL)
        instance.reranker = CrossEncoder(_RERANKER_MODEL)
        return instance

    # ------------------------------------------------------------------ #
    # Individual retrievers                                              #
    # ------------------------------------------------------------------ #

    def _dense_retrieve(self, query: str, k: int) -> list[int]:
        k_capped = min(k, len(self.documents))
        if k_capped == 0:
            return []
        query_vec = self.embedder.encode([query], show_progress_bar=False).astype("float32")
        _, indices = self.index.search(query_vec, k_capped)
        return [int(idx) for idx in indices[0] if idx != -1]

    def _bm25_retrieve(self, query: str, k: int) -> list[int]:
        k_capped = min(k, len(self.documents))
        if k_capped == 0:
            return []
        scores = self.bm25.get_scores(query.lower().split())
        return [int(idx) for idx in np.argsort(scores)[::-1][:k_capped]]

    # ------------------------------------------------------------------ #
    # Fusion                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[int]:
        scores: dict[int, float] = {}
        for ranking in rankings:
            for rank, doc_idx in enumerate(ranking):
                scores[doc_idx] = scores.get(doc_idx, 0.0) + 1.0 / (k + rank + 1)
        return [idx for idx, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        query: str,
        top_k_initial: int = 20,
        top_k_final: int = 5,
    ) -> tuple[list[str], float]:
        """
        Returns (documents, retrieval_confidence).
        retrieval_confidence is the sigmoid of the top cross-encoder logit, giving a 0–1 score.
        """
        if not self.documents:
            return [], 0.0

        dense_hits = self._dense_retrieve(query, top_k_initial)
        bm25_hits = self._bm25_retrieve(query, top_k_initial)
        fused_indices = self._reciprocal_rank_fusion([dense_hits, bm25_hits])[:top_k_initial]

        if not fused_indices:
            return [], 0.0

        candidates = [self.documents[i] for i in fused_indices]
        pairs = [(query, doc) for doc in candidates]
        scores = self.reranker.predict(pairs, show_progress_bar=False)

        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)

        top_logit = float(ranked[0][0]) if ranked else 0.0
        confidence = round(1.0 / (1.0 + math.exp(-top_logit)), 3)  # sigmoid → 0–1

        return [doc for _, doc in ranked[:top_k_final]], confidence