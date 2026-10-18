from typing import List

def calculate_precision_at_k(retrieved_item_names: List[str], ground_truth_names: List[str], k: int = 5) -> float:
    """
    Calculates Precision@K = (number of relevant retrieved items in top K) / K
    """
    if not retrieved_item_names or k <= 0:
        return 0.0
    
    top_k_retrieved = retrieved_item_names[:k]
    gt_lower = set(name.strip().lower() for name in ground_truth_names)
    
    relevant_count = 0
    for name in top_k_retrieved:
        if name.strip().lower() in gt_lower:
            relevant_count += 1
            
    return float(relevant_count) / float(len(top_k_retrieved))

def calculate_recall_at_k(retrieved_item_names: List[str], ground_truth_names: List[str], k: int = 5) -> float:
    """
    Calculates Recall@K = (number of relevant retrieved items in top K) / (total ground truth items)
    """
    if not ground_truth_names:
        return 1.0
    if not retrieved_item_names or k <= 0:
        return 0.0
        
    top_k_retrieved = retrieved_item_names[:k]
    gt_lower = set(name.strip().lower() for name in ground_truth_names)
    
    relevant_count = 0
    for name in top_k_retrieved:
        if name.strip().lower() in gt_lower:
            relevant_count += 1
            
    return float(relevant_count) / float(len(gt_lower))

def calculate_mrr(retrieved_item_names: List[str], ground_truth_names: List[str]) -> float:
    """
    Calculates Mean Reciprocal Rank (MRR) = 1 / rank of first relevant retrieved item.
    """
    if not retrieved_item_names or not ground_truth_names:
        return 0.0
        
    gt_lower = set(name.strip().lower() for name in ground_truth_names)
    for rank, name in enumerate(retrieved_item_names, 1):
        if name.strip().lower() in gt_lower:
            return 1.0 / float(rank)
            
    return 0.0
