import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config

def generate_plots():
    summary_csv = config.RESULTS_DIR / "summary.csv"
    if not summary_csv.exists():
        print(f"Error: {summary_csv} does not exist. Please run `python run_experiments.py` first.")
        return

    df = pd.read_csv(summary_csv)
    plots_dir = config.EVALUATION_DIR / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    models = ["BM25", "Dense RAG"]
    colors = ["#3498db", "#e74c3c"]

    metric_map = {
        "Precision@5": ("precision_comparison.png", "Precision@5 Metric Comparison", "Score (0.0 - 1.0)"),
        "Recall@5": ("recall_comparison.png", "Recall@5 Metric Comparison", "Score (0.0 - 1.0)"),
        "MRR": ("mrr_comparison.png", "Mean Reciprocal Rank (MRR)", "Score (0.0 - 1.0)"),
        "Latency (ms)": ("latency_comparison.png", "Average Retrieval Latency", "Milliseconds (ms)")
    }

    for metric_name, (filename, title, ylabel) in metric_map.items():
        row = df[df["Metric"] == metric_name]
        if row.empty:
            continue
            
        vals = [float(row["BM25"].values[0]), float(row["Dense RAG"].values[0])]

        plt.figure(figsize=(6, 4.5))
        bars = plt.bar(models, vals, color=colors, width=0.45)
        plt.ylabel(ylabel, fontsize=10, fontweight="bold")
        plt.title(title, fontsize=12, fontweight="bold", pad=12)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            label_fmt = f"{height:.3f}" if "Latency" not in metric_name else f"{height:.1f} ms"
            plt.annotate(label_fmt,
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.tight_layout()
        out_path = plots_dir / filename
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"[OK] Generated plot: {out_path}")

    print(f"\nAll evaluation plots successfully saved to {plots_dir}")

if __name__ == "__main__":
    generate_plots()
