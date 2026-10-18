import numpy as np
from sentence_transformers import SentenceTransformer
import config

class SBERTEmbedder:
    """
    SentenceTransformers (all-MiniLM-L6-v2) embedding model wrapper.
    """
    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        self._load_model()
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # L2 normalize vectors for cosine similarity vector search
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (embeddings / norms).astype("float32")
