import sys
import pandas as pd
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from embeddings.faiss_index import FAISSIndexManager
from retrievers.keyword_retriever import KeywordRetriever
from retrievers.dense_retriever import DenseRetriever
from evaluation.evaluator import BenchmarkEvaluator

def main():
    print("=" * 60)
    print("           RESTROBOT RESEARCH EVALUATION RUNNER")
    print("=" * 60)
    
    # Load dataset
    processed_csv = config.PROCESSED_CSV_PATH
    if not processed_csv.exists():
        print("Processed dataset not found! Building FAISS index & dataset first...")
        from build_index import main as build_main
        build_main()
        
    df_dataset = pd.read_csv(processed_csv)
    
    # Load FAISS index
    faiss_manager = FAISSIndexManager(models_dir=BASE_DIR / "models")
    if not faiss_manager.load():
        print("FAISS index not found! Building now...")
        from build_index import main as build_main
        build_main()
        faiss_manager.load()

    kw_retriever = KeywordRetriever(df_dataset)
    dense_retriever = DenseRetriever(faiss_manager, df_dataset)

    evaluator = BenchmarkEvaluator(kw_retriever, dense_retriever)
    
    print("\nRunning benchmark evaluation suite over test queries...")
    eval_res = evaluator.evaluate_all(k=5)
    
    query_df = eval_res["query_results_df"]
    summary = eval_res["summary_dict"]

    results_dir = config.RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)
    
    query_df.to_csv(results_dir / "query_results.csv", index=False)
    
    summary_df = pd.DataFrame([
        {"Metric": "Precision@5", "BM25": summary["BM25 Precision@5"], "Dense RAG": summary["Dense RAG Precision@5"]},
        {"Metric": "Recall@5", "BM25": summary["BM25 Recall@5"], "Dense RAG": summary["Dense RAG Recall@5"]},
        {"Metric": "MRR", "BM25": summary["BM25 MRR"], "Dense RAG": summary["Dense RAG MRR"]},
        {"Metric": "Latency (ms)", "BM25": summary["BM25 Avg Latency (ms)"], "Dense RAG": summary["Dense RAG Avg Latency (ms)"]}
    ])
    summary_df.to_csv(results_dir / "summary.csv", index=False)

    print("\n----------------------------------------------------")
    print(f"Benchmark Test Queries Evaluated: {summary['Total Benchmark Queries']}")
    print("----------------------------------------------------")
    print(f"BM25 Precision@5 : {summary['BM25 Precision@5']}")
    print(f"BM25 Recall@5    : {summary['BM25 Recall@5']}")
    print(f"BM25 MRR         : {summary['BM25 MRR']}")
    print(f"BM25 Latency     : {summary['BM25 Avg Latency (ms)']} ms")
    print("----------------------------------------------------")
    print(f"DENSE RAG Precision@5 : {summary['Dense RAG Precision@5']}")
    print(f"DENSE RAG Recall@5    : {summary['Dense RAG Recall@5']}")
    print(f"DENSE RAG MRR         : {summary['Dense RAG MRR']}")
    print(f"DENSE RAG Latency     : {summary['Dense RAG Avg Latency (ms)']} ms")
    print("----------------------------------------------------")
    print("COMPARISON SUMMARY")
    print("----------------------------------------------------")
    print(summary_df.to_string(index=False))
    print("====================================================")
    print(f"[OK] Saved query-level results to {results_dir / 'query_results.csv'}")
    print(f"[OK] Saved summary metrics to {results_dir / 'summary.csv'}")

if __name__ == "__main__":
    main()
