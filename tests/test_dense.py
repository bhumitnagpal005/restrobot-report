import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import pandas as pd
from embeddings.faiss_index import FAISSIndexManager
from retrievers.dense_retriever import DenseRetriever

def test_dense_retriever():
    sample_docs = [
        {"item_name": "Paneer Tikka Roll", "restaurant": "Spice Villa", "price": 180, "diet": "vegetarian", "document_text": "Paneer Tikka Roll Spicy paneer roll with vegetables"},
        {"item_name": "Chicken Biryani", "restaurant": "Spice Villa", "price": 220, "diet": "non-vegetarian", "document_text": "Chicken Biryani Aromatic basmati rice with spicy chicken"}
    ]
    df = pd.DataFrame(sample_docs)
    
    models_dir = BASE_DIR / "models_test"
    faiss_mgr = FAISSIndexManager(models_dir=models_dir)
    faiss_mgr.build_and_save(sample_docs)
    
    retriever = DenseRetriever(faiss_mgr, df)
    res = retriever.retrieve("biryani", top_k=2)
    
    assert len(res["retrieved_items"]) > 0
    assert res["approach"] == "Dense RAG (SBERT + FAISS)"
