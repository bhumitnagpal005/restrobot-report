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
from retrievers.hybrid_retriever import ConstraintAwareHybridRetriever
from run_experiments import main as run_eval_main
from visualization.generate_plots import generate_plots

def print_header():
    print("\n" + "=" * 60)
    print("                 RESTROBOT (PHASE 1 DEMO)")
    print("   Conversational Restaurant Information Retrieval System")
    print("=" * 60)

def print_menu():
    print("""
Select Retrieval Mode:
  1. Keyword Retrieval (BM25 Baseline)
  2. Conventional Dense RAG (SBERT + FAISS Baseline)
  3. Compare Both Models (Same Query Execution)
  4. Run Quantitative Benchmark Evaluation
  5. Exit
""")

def display_items(items: list, title: str, latency_ms: float):
    print(f"\n" + "-" * 55)
    print(f"{title} (Latency: {latency_ms} ms)")
    print("-" * 55)
    if not items:
        print("No items retrieved.")
        return

    for idx, item in enumerate(items, 1):
        rest = item.get("restaurant", "Unknown")
        name = item.get("item_name", "Item")
        price = item.get("price", 0)
        diet = str(item.get("diet", "")).capitalize()
        score = item.get("retrieval_score", 0.0)
        
        print(f"  {idx}. {name}")
        print(f"     Restaurant: {rest} | Price: Rs. {price:.0f} | Diet: {diet} | Score: {score}")
        if item.get("description"):
            print(f"     Desc: {item.get('description')}")
        print()

def main():
    print_header()
    
    processed_csv = config.PROCESSED_CSV_PATH
    if not processed_csv.exists():
        print("Initializing dataset and FAISS index for the first time...")
        from build_index import main as build_main
        build_main()

    df_dataset = pd.read_csv(processed_csv)
    faiss_manager = FAISSIndexManager(models_dir=BASE_DIR / "models")
    if not faiss_manager.load():
        print("Loading/building FAISS vector store index...")
        from build_index import main as build_main
        build_main()
        faiss_manager.load()

    kw_retriever = KeywordRetriever(df_dataset)
    dense_retriever = DenseRetriever(faiss_manager, df_dataset)

    while True:
        print_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            query = input("\nEnter your natural-language query: ").strip()
            if query:
                res = kw_retriever.retrieve(query, top_k=5)
                display_items(res["retrieved_items"], "MODEL 1 - KEYWORD RETRIEVAL (BM25)", res["latency_ms"])

        elif choice == "2":
            query = input("\nEnter your natural-language query: ").strip()
            if query:
                res = dense_retriever.retrieve(query, top_k=5)
                display_items(res["retrieved_items"], "MODEL 2 - DENSE RAG (SBERT + FAISS)", res["latency_ms"])

        elif choice == "3":
            query = input("\nEnter your query for side-by-side comparison: ").strip()
            if query:
                print("\n" + "=" * 60)
                print(f"           MODEL COMPARISON - SAME QUERY EXECUTION")
                print(f"QUERY: \"{query}\"")
                print("=" * 60)
                
                kw_res = kw_retriever.retrieve(query, top_k=5)
                display_items(kw_res["retrieved_items"], "MODEL 1: KEYWORD RETRIEVAL (BM25)", kw_res["latency_ms"])

                dense_res = dense_retriever.retrieve(query, top_k=5)
                display_items(dense_res["retrieved_items"], "MODEL 2: CONVENTIONAL DENSE RAG (SBERT + FAISS)", dense_res["latency_ms"])

        elif choice == "4":
            print("\nExecuting benchmark evaluation & generating plots...")
            run_eval_main()
            generate_plots()

        elif choice == "5":
            print("\nExiting RestroBot. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
