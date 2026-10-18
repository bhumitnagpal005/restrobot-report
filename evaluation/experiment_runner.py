"""
Automated Batch Experiment Runner & Ablation Study for RestroBot.
Executes benchmark queries, logs performance metrics, and saves research tables to evaluation/results/.
"""

import json
import pandas as pd
from pathlib import Path
from preprocessing.metadata import load_dataset
from embeddings.index import VectorIndex
from retrievers.keyword_retriever import KeywordRetriever
from retrievers.dense_retriever import DenseRetriever
from retrievers.hybrid_retriever import HybridRetriever
from evaluation.evaluator import Evaluator
import config


def run_benchmark_experiments() -> pd.DataFrame:
    """
    Runs evaluation benchmark over all queries in benchmark_queries.csv.
    """
    df_dataset = load_dataset(config.RAW_DATA_DIR, config.PROCESSED_CSV_PATH)
    
    vec_index = VectorIndex(config.INDEX_CACHE_DIR)
    if not vec_index.load():
        vec_index.build(df_dataset["document_text"].tolist(), df_dataset)

    kw_retriever = KeywordRetriever(df_dataset)
    dense_retriever = DenseRetriever(vec_index, df_dataset)
    hybrid_retriever = HybridRetriever(vec_index, df_dataset)

    evaluator = Evaluator(kw_retriever, dense_retriever, hybrid_retriever)

    if not config.BENCHMARK_CSV_PATH.exists():
        print(f"[Warning] Benchmark CSV not found at {config.BENCHMARK_CSV_PATH}")
        return pd.DataFrame()

    df_queries = pd.read_csv(config.BENCHMARK_CSV_PATH)
    results = []

    print(f"Executing experiment benchmark across {len(df_queries)} queries...")

    for idx, row in df_queries.iterrows():
        q_id = row.get("query_id", f"Q{idx+1:03d}")
        query = row.get("query", "")
        gt_raw = str(row.get("expected_items", ""))
        gt_items = [g.strip() for g in gt_raw.split("|") if g.strip()]

        res = evaluator.evaluate_query_all_approaches(query, ground_truth_items=gt_items)

        # Log row per approach
        for app_name, key in [("Keyword Retrieval", "keyword"), ("Conventional Dense RAG", "dense"), ("Constraint-Aware Hybrid RAG", "hybrid")]:
            app_res = res[key]
            results.append({
                "query_id": q_id,
                "query": query,
                "query_type": row.get("query_type", "General"),
                "approach": app_name,
                "precision_at_5": app_res.get("p_at_5", 0.0),
                "recall_at_5": app_res.get("r_at_5", 0.0),
                "mrr": app_res.get("mrr", 0.0),
                "constraint_satisfaction_rate": app_res.get("csr", 0.0),
                "total_latency_ms": app_res.get("total_latency_ms", 0),
            })

    results_df = pd.DataFrame(results)
    
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = config.RESULTS_DIR / "experiment_summary.csv"
    results_df.to_csv(summary_path, index=False)
    
    # Save overall averages
    avg_summary = results_df.groupby("approach")[["precision_at_5", "recall_at_5", "mrr", "constraint_satisfaction_rate", "total_latency_ms"]].mean()
    avg_path = config.RESULTS_DIR / "approach_averages.csv"
    avg_summary.to_csv(avg_path)

    print(f"Benchmark results successfully saved to {summary_path}")
    print("\n--- EXPERIMENTAL SUMMARY (AVERAGES) ---")
    print(avg_summary.to_string())

    return results_df


if __name__ == "__main__":
    run_benchmark_experiments()
