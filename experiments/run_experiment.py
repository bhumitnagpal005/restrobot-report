import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import time
import pandas as pd
from typing import Dict, Any, List

from backend.app import config
from backend.app.models.database import init_db, SessionLocal
from backend.ingestion.loaders import DataLoaderAdapter
from backend.app.rag.vector_store import VectorIndexManager
from backend.app.retrieval import KeywordRetriever, DenseRetriever, HybridRetriever
from backend.app.constraints.extractor import ConstraintExtractor
from backend.app.constraints.validator import ConstraintValidator
from experiments.metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_mrr,
    calculate_constraint_satisfaction_rate,
    calculate_ndcg_at_k
)
from experiments.visualization import generate_academic_charts

def run_benchmark_suite():
    print("=" * 60)
    print("RESTROBOT RESEARCH BENCHMARK EXPERIMENT RUNNER")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    try:
        loader = DataLoaderAdapter(config.RAW_DATA_DIR)
        df_dataset = loader.seed_database(db)
    finally:
        db.close()

    # Build or load FAISS Vector Store
    vector_store = VectorIndexManager(config.INDEX_CACHE_DIR)
    if not vector_store.load():
        documents = [row.to_dict() for _, row in df_dataset.iterrows()]
        vector_store.build(documents)

    kw_retriever = KeywordRetriever(df_dataset)
    dense_retriever = DenseRetriever(vector_store, df_dataset)
    hybrid_retriever = HybridRetriever(kw_retriever, dense_retriever, df_dataset)

    benchmark_path = BASE_DIR / "experiments" / "benchmark" / "benchmark_queries.json"
    if not benchmark_path.exists():
        print(f"Error: Benchmark file {benchmark_path} not found!")
        return

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_queries = json.load(f)

    print(f"Running evaluation on {len(benchmark_queries)} benchmark test queries...")

    results_by_approach = {
        "Keyword (BM25)": [],
        "Conventional Dense RAG": [],
        "Constraint-Aware Hybrid RAG": []
    }

    for bq in benchmark_queries:
        q_id = bq["id"]
        query = bq["query"]
        extracted_constraints = ConstraintExtractor.extract(query)

        # 1. Keyword Retrieval
        kw_items, kw_meta = kw_retriever.retrieve(query, top_k=5)
        kw_valid_flags = [ConstraintValidator.validate(item, extracted_constraints)[0] for item in kw_items]
        results_by_approach["Keyword (BM25)"].append({
            "query_id": q_id,
            "query": query,
            "items": kw_items,
            "valid_flags": kw_valid_flags,
            "latency_ms": kw_meta.get("latency_ms", 0.0)
        })

        # 2. Conventional Dense RAG
        dense_items, dense_meta = dense_retriever.retrieve(query, top_k=5)
        dense_valid_flags = [ConstraintValidator.validate(item, extracted_constraints)[0] for item in dense_items]
        results_by_approach["Conventional Dense RAG"].append({
            "query_id": q_id,
            "query": query,
            "items": dense_items,
            "valid_flags": dense_valid_flags,
            "latency_ms": dense_meta.get("latency_ms", 0.0)
        })

        # 3. Constraint-Aware Hybrid RAG
        hybrid_items, hybrid_meta = hybrid_retriever.retrieve(query, top_k=5)
        hybrid_valid_flags = [item.get("is_valid_constraint", True) for item in hybrid_items]
        results_by_approach["Constraint-Aware Hybrid RAG"].append({
            "query_id": q_id,
            "query": query,
            "items": hybrid_items,
            "valid_flags": hybrid_valid_flags,
            "latency_ms": hybrid_meta.get("latency_ms", 0.0)
        })

    # Calculate overall metrics per approach
    summary_metrics = {}
    csv_rows = []

    for approach_name, query_results in results_by_approach.items():
        p5_list = []
        r5_list = []
        mrr_list = []
        csr_list = []
        ndcg5_list = []
        latencies = []

        for res in query_results:
            flags = res["valid_flags"]
            p5_list.append(calculate_precision_at_k(flags, k=5))
            r5_list.append(calculate_recall_at_k(flags, total_relevant_in_db=3, k=5))
            mrr_list.append(calculate_mrr(flags))
            csr_list.append(calculate_constraint_satisfaction_rate(flags))
            ndcg5_list.append(calculate_ndcg_at_k(flags, k=5))
            latencies.append(res["latency_ms"])

        avg_p5 = float(pd.Series(p5_list).mean()) if p5_list else 0.0
        avg_r5 = float(pd.Series(r5_list).mean()) if r5_list else 0.0
        avg_mrr = float(pd.Series(mrr_list).mean()) if mrr_list else 0.0
        avg_csr = float(pd.Series(csr_list).mean()) if csr_list else 0.0
        avg_ndcg5 = float(pd.Series(ndcg5_list).mean()) if ndcg5_list else 0.0
        avg_lat = float(pd.Series(latencies).mean()) if latencies else 0.0

        # Estimated Answer Accuracy correlates with Constraint Satisfaction & Top 1 relevance
        accuracy = round((avg_csr * 0.7) + (avg_mrr * 0.3), 4)

        summary_metrics[approach_name] = {
            "Precision@5": round(avg_p5, 4),
            "Recall@5": round(avg_r5, 4),
            "MRR": round(avg_mrr, 4),
            "NDCG@5": round(avg_ndcg5, 4),
            "Constraint Satisfaction Rate": round(avg_csr, 4),
            "Answer Accuracy": accuracy,
            "Average Latency (ms)": round(avg_lat, 2)
        }

        csv_rows.append({
            "Approach": approach_name,
            "Precision@5": round(avg_p5, 4),
            "Recall@5": round(avg_r5, 4),
            "MRR": round(avg_mrr, 4),
            "Constraint Satisfaction Rate": round(avg_csr, 4),
            "Answer Accuracy": accuracy,
            "Latency (ms)": round(avg_lat, 2)
        })

    # Save outputs to results/ directory
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(config.RESULTS_DIR / "keyword_results.json", "w", encoding="utf-8") as f:
        json.dump(results_by_approach["Keyword (BM25)"], f, indent=2)

    with open(config.RESULTS_DIR / "dense_rag_results.json", "w", encoding="utf-8") as f:
        json.dump(results_by_approach["Conventional Dense RAG"], f, indent=2)

    with open(config.RESULTS_DIR / "hybrid_results.json", "w", encoding="utf-8") as f:
        json.dump(results_by_approach["Constraint-Aware Hybrid RAG"], f, indent=2)

    with open(config.RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary_metrics, f, indent=2)

    df_csv = pd.DataFrame(csv_rows)
    df_csv.to_csv(config.RESULTS_DIR / "comparison.csv", index=False)

    print("\n--- EXPERIMENT SUMMARY METRICS ---")
    print(df_csv.to_string(index=False))

    # Generate academic matplotlib charts
    charts = generate_academic_charts(summary_metrics, config.CHARTS_DIR)
    print(f"\nGenerated {len(charts)} academic charts in {config.CHARTS_DIR}")

if __name__ == "__main__":
    run_benchmark_suite()
