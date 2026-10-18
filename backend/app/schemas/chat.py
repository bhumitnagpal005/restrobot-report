from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., description="User natural language food query", example="Show vegetarian food under ₹200")
    retrieval_method: str = Field("hybrid", description="'keyword', 'dense', or 'hybrid'")
    conversation_id: Optional[str] = Field("default_session", description="Session identifier for multi-turn chat")
    top_k: Optional[int] = Field(5, description="Number of results to retrieve")

class RetrievedItemSchema(BaseModel):
    id: str
    restaurant_id: str
    restaurant_name: str
    item_name: str
    category: str
    price: float
    description: str
    is_vegetarian: bool
    is_non_vegetarian: bool
    spice_level: str
    cuisine: str
    retrieval_score: float
    rank: int
    is_valid_constraint: Optional[bool] = True
    constraint_violations: Optional[List[str]] = []

class LatencySchema(BaseModel):
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float

class ChatResponse(BaseModel):
    answer: str
    retrieval_method: str
    retrieved_items: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    latency: LatencySchema
    metadata: Dict[str, Any]

class CompareRequest(BaseModel):
    query: str = Field(..., description="Query to execute across all 3 retrieval approaches")
    conversation_id: Optional[str] = Field("default_session")
    top_k: Optional[int] = Field(5)

class SingleApproachResult(BaseModel):
    answer: str
    retrieved_items: List[Dict[str, Any]]
    scores: List[float]
    latency_ms: float
    generation_latency_ms: float
    constraint_satisfaction_rate: float
    constraints_summary: Optional[Dict[str, Any]] = {}

class CompareResponse(BaseModel):
    query: str
    conversation_id: str
    keyword: SingleApproachResult
    dense_rag: SingleApproachResult
    hybrid_rag: SingleApproachResult
    comparison_summary: Dict[str, Any]

class RestaurantSchema(BaseModel):
    id: str
    name: str
    location: str
    address: Optional[str]
    cuisine: Optional[str]
    rating: float
    phone: Optional[str]
    opening_hours: Optional[str]
