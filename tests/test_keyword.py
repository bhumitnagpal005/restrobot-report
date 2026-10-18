import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import pandas as pd
from retrievers.keyword_retriever import KeywordRetriever

def test_keyword_retriever():
    sample_data = [
        {"item_name": "Paneer Tikka Roll", "restaurant": "Spice Villa", "price": 180, "diet": "vegetarian", "document_text": "Paneer Tikka Roll Spicy paneer roll with vegetables"},
        {"item_name": "Chicken Biryani", "restaurant": "Spice Villa", "price": 220, "diet": "non-vegetarian", "document_text": "Chicken Biryani Aromatic basmati rice with spicy chicken"}
    ]
    df = pd.DataFrame(sample_data)
    retriever = KeywordRetriever(df)
    
    res = retriever.retrieve("biryani", top_k=2)
    assert len(res["retrieved_items"]) > 0
    assert "biryani" in res["retrieved_items"][0]["item_name"].lower()
    assert res["approach"] == "Keyword Retrieval (BM25)"
