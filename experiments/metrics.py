import numpy as np
from typing import List, Dict, Any

def calculate_precision_at_k(retrieved_valid_flags: List[bool], k: int = 5) -> float:
    if not retrieved_valid_flags or k <= 0:
        return 0.0
    sub = retrieved_valid_flags[:k]
    return float(sum(sub)) / float(len(sub))

def calculate_recall_at_k(retrieved_valid_flags: List[bool], total_relevant_in_db: int, k: int = 5) -> float:
    if total_relevant_in_db <= 0:
        return 1.0 if any(retrieved_valid_flags[:k]) else 0.0
    sub = retrieved_valid_flags[:k]
    relevant_retrieved = sum(sub)
    return float(relevant_retrieved) / float(total_relevant_in_db)

def calculate_mrr(retrieved_valid_flags: List[bool]) -> float:
    for rank, is_valid in enumerate(retrieved_valid_flags, 1):
        if is_valid:
            return 1.0 / float(rank)
    return 0.0

def calculate_constraint_satisfaction_rate(retrieved_valid_flags: List[bool]) -> float:
    if not retrieved_valid_flags:
        return 0.0
    return float(sum(retrieved_valid_flags)) / float(len(retrieved_valid_flags))

def calculate_ndcg_at_k(retrieved_valid_flags: List[bool], k: int = 5) -> float:
    if not retrieved_valid_flags or k <= 0:
        return 0.0
    sub = retrieved_valid_flags[:k]
    dcg = 0.0
    for idx, rel in enumerate(sub):
        if rel:
            dcg += 1.0 / np.log2(idx + 2)
    
    # Ideal DCG assuming all top k are relevant
    idcg = sum(1.0 / np.log2(idx + 2) for idx in range(min(k, sum(sub) or 1)))
    return (dcg / idcg) if idcg > 0 else 0.0
