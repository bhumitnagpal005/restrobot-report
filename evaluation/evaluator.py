import pandas as pd
from typing import Dict, Any, List
from evaluation.metrics import calculate_precision_at_k, calculate_recall_at_k, calculate_mrr
import config

class BenchmarkEvaluator:
    """
    Evaluator executing Model 1 (BM25) and Model 2 (Dense RAG) over benchmark queries.
    Compares retrieved candidates against ground-truth items.
    """
    def __init__(self, kw_retriever, dense_retriever, benchmark_csv=config.EVALUATION_DIR / "benchmark_queries.csv", ground_truth_csv=config.EVALUATION_DIR / "ground_truth.csv"):
        self.kw_retriever = kw_retriever
        self.dense_retriever = dense_retriever
        self.benchmark_df = pd.read_csv(benchmark_csv)
        self.gt_df = pd.read_csv(ground_truth_csv)

    def get_ground_truth_for_query(self, query_id: str) -> List[str]:
        sub = self.gt_df[self.gt_df["query_id"] == query_id]
        return sub["expected_item_name"].tolist()

    def evaluate_all(self, k: int = 5) -> Dict[str, Any]:
        query_results = []

        for idx, row in self.benchmark_df.iterrows():
            q_id = row["query_id"]
            query = row["query"]
            category = row["category"]
            gt_items = self.get_ground_truth_for_query(q_id)

            # 1. Run Keyword Retrieval (BM25)
            kw_res = self.kw_retriever.retrieve(query, top_k=k)
            kw_names = [item.get("item_name", "") for item in kw_res.get("retrieved_items", [])]
            kw_p5 = calculate_precision_at_k(kw_names, gt_items, k=k)
            kw_r5 = calculate_recall_at_k(kw_names, gt_items, k=k)
            kw_mrr = calculate_mrr(kw_names, gt_items)
            kw_lat = kw_res.get("latency_ms", 0.0)

            # 2. Run Dense RAG (SBERT + FAISS)
            dense_res = self.dense_retriever.retrieve(query, top_k=k)
            dense_names = [item.get("item_name", "") for item in dense_res.get("retrieved_items", [])]
            dense_p5 = calculate_precision_at_k(dense_names, gt_items, k=k)
            dense_r5 = calculate_recall_at_k(dense_names, gt_items, k=k)
            dense_mrr = calculate_mrr(dense_names, gt_items)
            dense_lat = dense_res.get("latency_ms", 0.0)

            query_results.append({
                "query_id": q_id,
                "query": query,
                "category": category,
                "ground_truth": ", ".join(gt_items),
                "kw_retrieved": ", ".join(kw_names[:3]),
                "kw_precision_5": round(kw_p5, 4),
                "kw_recall_5": round(kw_r5, 4),
                "kw_mrr": round(kw_mrr, 4),
                "kw_latency_ms": kw_lat,
                "dense_retrieved": ", ".join(dense_names[:3]),
                "dense_precision_5": round(dense_p5, 4),
                "dense_recall_5": round(dense_r5, 4),
                "dense_mrr": round(dense_mrr, 4),
                "dense_latency_ms": dense_lat
            })

        df_query_res = pd.DataFrame(query_results)

        # Summary averages
        summary = {
            "Total Benchmark Queries": len(df_query_res),
            "BM25 Precision@5": round(float(df_query_res["kw_precision_5"].mean()), 4),
            "BM25 Recall@5": round(float(df_query_res["kw_recall_5"].mean()), 4),
            "BM25 MRR": round(float(df_query_res["kw_mrr"].mean()), 4),
            "BM25 Avg Latency (ms)": round(float(df_query_res["kw_latency_ms"].mean()), 2),
            "Dense RAG Precision@5": round(float(df_query_res["dense_precision_5"].mean()), 4),
            "Dense RAG Recall@5": round(float(df_query_res["dense_recall_5"].mean()), 4),
            "Dense RAG MRR": round(float(df_query_res["dense_mrr"].mean()), 4),
            "Dense RAG Avg Latency (ms)": round(float(df_query_res["dense_latency_ms"].mean()), 2)
        }

        return {
            "query_results_df": df_query_res,
            "summary_dict": summary
        }
