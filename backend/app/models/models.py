from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(100), index=True)
    address = Column(Text, nullable=True)
    cuisine = Column(String(100), nullable=True)
    rating = Column(Float, default=0.0)
    phone = Column(String(30), nullable=True)
    opening_hours = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey("restaurants.id"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(Float, nullable=False, index=True)
    description = Column(Text, default="")
    is_vegetarian = Column(Boolean, default=False, index=True)
    is_non_vegetarian = Column(Boolean, default=False, index=True)
    spice_level = Column(String(50), default="normal", index=True)
    cuisine = Column(String(100), default="General", index=True)
    availability = Column(Boolean, default=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="items")


class BenchmarkQuery(Base):
    __tablename__ = "benchmark_queries"

    id = Column(String(50), primary_key=True)
    query_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    expected_constraints = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GroundTruth(Base):
    __tablename__ = "ground_truth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String(50), ForeignKey("benchmark_queries.id"), nullable=False)
    item_id = Column(String(50), ForeignKey("menu_items.id"), nullable=False)
    relevance_score = Column(Float, default=1.0)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id = Column(String(50), primary_key=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    model_name = Column(String(100), nullable=False)
    total_queries = Column(Integer, default=0)
    metrics_summary = Column(JSON, nullable=True)


class RetrievalResult(Base):
    __tablename__ = "retrieval_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey("experiment_runs.id"), nullable=False)
    query_id = Column(String(50), nullable=False)
    retrieval_method = Column(String(50), nullable=False)
    precision_k = Column(Float, default=0.0)
    recall_k = Column(Float, default=0.0)
    mrr = Column(Float, default=0.0)
    constraint_satisfaction_rate = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    retrieved_item_ids = Column(JSON, nullable=True)
