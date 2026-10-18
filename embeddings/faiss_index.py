import os
import json
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import config
from embeddings.embedder import SBERTEmbedder

class FAISSIndexManager:
    """
    FAISS Index Manager handling vector creation, persistence, and similarity search.
    Stores index files in models/ directory.
    """
    def __init__(self, models_dir: Path = config.BASE_DIR / "models"):
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.models_dir / "faiss.index"
        self.meta_path = self.models_dir / "metadata.json"
        self.npy_path = self.models_dir / "embeddings.npy"
        
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.embedder = SBERTEmbedder()

    def build_and_save(self, documents: List[Dict[str, Any]]) -> None:
        """
        Generates SBERT embeddings for documents and builds FAISS index.
        Saves faiss.index, metadata.json, and embeddings.npy.
        """
        if not documents:
            raise ValueError("No documents provided to build FAISS index.")
            
        self.metadata = documents
        doc_texts = [doc["document_text"] for doc in documents]
        
        print(f"Generating SBERT ({config.EMBEDDING_MODEL_NAME}) embeddings for {len(documents)} items...")
        embeddings = self.embedder.encode(doc_texts)
        
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product on normalized vectors = Cosine Similarity
        self.index.add(embeddings)
        
        # Save artifacts
        faiss.write_index(self.index, str(self.index_path))
        np.save(self.npy_path, embeddings)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)

        print(f"[OK] FAISS Index successfully saved to {self.index_path}")
        print(f"[OK] Metadata saved to {self.meta_path}")
        print(f"[OK] Embeddings saved to {self.npy_path}")

    def load(self) -> bool:
        """
        Loads pre-built FAISS index and metadata if available.
        Returns True if successfully loaded, False otherwise.
        """
        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                return True
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                return False
        return False

    def search(self, query: str, top_k: int = config.FINAL_RETRIEVAL_K) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches FAISS vector space for top_k nearest documents.
        Returns list of (metadata_dict, similarity_score).
        """
        if self.index is None or not self.metadata:
            if not self.load():
                raise RuntimeError("FAISS Index is not loaded or built yet. Please run `python build_index.py` first.")

        query_emb = self.embedder.encode([query])
        scores, indices = self.index.search(query_emb, min(top_k, len(self.metadata)))

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if 0 <= idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        return results
