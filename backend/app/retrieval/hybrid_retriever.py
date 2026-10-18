import time
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

from backend.app import config
from backend.app.retrieval.base_retriever import BaseRetriever
from backend.app.retrieval.keyword_retriever import KeywordRetriever
from backend.app.retrieval.dense_retriever import DenseRetriever
from backend.app.constraints.extractor import ConstraintExtractor
from backend.app.constraints.validator import ConstraintValidator
from backend.app.constraints.schema import ExtractedConstraints

class HybridRetriever(BaseRetriever):
    """
    Constraint-Aware Hybrid RAG retriever.
    Combines query constraint extraction, FAISS dense semantic retrieval, BM25 keyword retrieval,
    hard constraint validation, transparent hybrid scoring, and re-ranking.
    """
    def __init__(
        self,
        kw_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
        dataset: pd.DataFrame,
        alpha: float = config.SEMANTIC_WEIGHT,
        beta: float = config.KEYWORD_WEIGHT,
        gamma: float = config.CONSTRAINT_WEIGHT
    ):
        super().__init__(dataset)
        self.kw_retriever = kw_retriever
        self.dense_retriever = dense_retriever
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def retrieve(self, query: str, top_k: int = 5, session_context: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        start_time = time.time()
        
        # Step 1: Constraint Extraction
        extracted_constraints = ConstraintExtractor.extract(query, session_context=session_context)

        # Step 2: Fetch broader candidate pool from both Keyword and Dense Retrievers
        pool_size = max(top_k * 4, 20)
        kw_candidates, _ = self.kw_retriever.retrieve(query, top_k=pool_size)
        dense_candidates, _ = self.dense_retriever.retrieve(query, top_k=pool_size)

        # Combine candidate pool by item ID
        candidates_map = {}
        for item in dense_candidates:
            item_id = item.get("item_id") or item.get("id")
            candidates_map[item_id] = {
                "item": item,
                "dense_score": float(item.get("retrieval_score", 0.0)),
                "kw_score": 0.0
            }

        for item in kw_candidates:
            item_id = item.get("item_id") or item.get("id")
            if item_id in candidates_map:
                candidates_map[item_id]["kw_score"] = float(item.get("retrieval_score", 0.0))
            else:
                candidates_map[item_id] = {
                    "item": item,
                    "dense_score": 0.0,
                    "kw_score": float(item.get("retrieval_score", 0.0))
                }

        # Step 3: Score Normalization
        dense_scores = [c["dense_score"] for c in candidates_map.values()]
        kw_scores = [c["kw_score"] for c in candidates_map.values()]

        max_dense = max(dense_scores) if dense_scores and max(dense_scores) > 0 else 1.0
        max_kw = max(kw_scores) if kw_scores and max(kw_scores) > 0 else 1.0

        # Step 4: Constraint Validation & Hybrid Scoring
        scored_candidates = []
        valid_count = 0
        total_evaluated = len(candidates_map)

        for item_id, cand_data in candidates_map.items():
            item = cand_data["item"]
            norm_semantic = cand_data["dense_score"] / max_dense
            norm_keyword = cand_data["kw_score"] / max_kw

            is_valid, constraint_score, violations = ConstraintValidator.validate(item, extracted_constraints)
            if is_valid:
                valid_count += 1

            # Transparent hybrid scoring formula
            final_score = (
                self.alpha * norm_semantic +
                self.beta * norm_keyword +
                self.gamma * constraint_score
            )
            
            # Penalize invalid hard constraint items severely in rank
            if not is_valid and extracted_constraints.hard_constraints:
                final_score *= 0.1

            enriched_item = dict(item)
            enriched_item["final_score"] = round(float(final_score), 4)
            enriched_item["semantic_score"] = round(float(norm_semantic), 4)
            enriched_item["keyword_score"] = round(float(norm_keyword), 4)
            enriched_item["constraint_score"] = round(float(constraint_score), 4)
            enriched_item["is_valid_constraint"] = is_valid
            enriched_item["constraint_violations"] = violations
            
            scored_candidates.append(enriched_item)

        # Step 5: Re-ranking by final hybrid score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        top_results = scored_candidates[:top_k]

        for rank, item in enumerate(top_results, 1):
            item["rank"] = rank
            item["retrieval_score"] = item["final_score"]

        latency_ms = (time.time() - start_time) * 1000.0
        csr = (valid_count / total_evaluated) if total_evaluated > 0 else 1.0

        metadata = {
            "method": "Constraint-Aware Hybrid RAG",
            "latency_ms": round(latency_ms, 2),
            "scores": [item["final_score"] for item in top_results],
            "extracted_constraints": extracted_constraints.dict(),
            "constraints_summary": extracted_constraints.dict_summary(),
            "constraint_satisfaction_rate": round(csr, 4),
            "top_k": top_k,
            "weights": {"alpha": self.alpha, "beta": self.beta, "gamma": self.gamma}
        }
        return top_results, metadata
