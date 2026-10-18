from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import pandas as pd

class BaseRetriever(ABC):
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, session_context: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieves top_k matching items for a query.
        Returns:
            retrieved_items: List[Dict[str, Any]]
            metadata: Dict[str, Any] containing scores, latencies, constraints, etc.
        """
        pass
