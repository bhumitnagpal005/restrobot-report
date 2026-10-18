import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from evaluation.metrics import calculate_precision_at_k, calculate_recall_at_k, calculate_mrr

def test_precision_at_k():
    retrieved = ["Paneer Tikka Roll", "Veg Roll", "Chicken Biryani"]
    ground_truth = ["Paneer Tikka Roll", "Veg Roll"]
    
    # 2 out of 3 retrieved are in ground truth -> 2/3 = 0.6667
    prec = calculate_precision_at_k(retrieved, ground_truth, k=3)
    assert round(prec, 2) == 0.67

def test_recall_at_k():
    retrieved = ["Paneer Tikka Roll", "Chicken Biryani"]
    ground_truth = ["Paneer Tikka Roll", "Veg Roll"]
    
    # 1 out of 2 ground truth items retrieved -> 1/2 = 0.5
    rec = calculate_recall_at_k(retrieved, ground_truth, k=2)
    assert rec == 0.5

def test_mrr():
    retrieved = ["Chicken Biryani", "Paneer Tikka Roll"]
    ground_truth = ["Paneer Tikka Roll"]
    
    # First relevant item is at rank 2 -> MRR = 1/2 = 0.5
    mrr = calculate_mrr(retrieved, ground_truth)
    assert mrr == 0.5
