import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app import config

_model_instance = None

def get_embedding_model() -> SentenceTransformer:
    global _model_instance
    if _model_instance is None:
        print(f"Loading SentenceTransformer embedding model: {config.EMBEDDING_MODEL}")
        _model_instance = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model_instance

def encode_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # Normalize vectors for cosine similarity search
    faiss_norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    faiss_norm[faiss_norm == 0] = 1.0
    return (embeddings / faiss_norm).astype("float32")
