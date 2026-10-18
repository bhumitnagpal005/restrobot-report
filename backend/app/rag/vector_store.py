import os
import json
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from backend.app import config
from backend.app.rag.embeddings import encode_texts

class VectorIndexManager:
    """
    FAISS vector index manager for dense semantic similarity retrieval.
    """
    def __init__(self, cache_dir: Path = config.INDEX_CACHE_DIR):
        self.cache_dir = cache_dir
        self.index_path = cache_dir / "faiss.index"
        self.meta_path = cache_dir / "documents.json"
        self.index = None
        self.documents: List[Dict[str, Any]] = []

    def build(self, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            return
        
        self.documents = documents
        texts = [doc["document_text"] for doc in documents]
        embeddings = encode_texts(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product over normalized vectors = Cosine Similarity
        self.index.add(embeddings)

        # Save index and metadata
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)
        print(f"FAISS Vector Index built successfully with {len(documents)} document vectors.")

    def load(self) -> bool:
        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                return True
            except Exception as e:
                print(f"Failed loading vector index: {e}")
                return False
        return False

    def search(self, query: str, top_k: int = config.TOP_K) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None or not self.documents:
            return []

        query_emb = encode_texts([query])
        scores, indices = self.index.search(query_emb, min(top_k, len(self.documents)))

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if 0 <= idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        return results
