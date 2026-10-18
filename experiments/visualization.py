import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for server generation
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from backend.app import config

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

def generate_academic_charts(summary_metrics: dict, output_dir: Path = config.CHARTS_DIR) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    approaches = ["Keyword (BM25)", "Conventional Dense RAG", "Constraint-Aware Hybrid RAG"]
    colors = ["#3498db", "#e74c3c", "#2ecc71"]

    # Extract metrics per approach
    kw = summary_metrics.get("Keyword (BM25)", {})
    dense = summary_metrics.get("Conventional Dense RAG", {})
    hybrid = summary_metrics.get("Constraint-Aware Hybrid RAG", {})

    p5 = [kw.get("Precision@5", 0), dense.get("Precision@5", 0), hybrid.get("Precision@5", 0)]
    r5 = [kw.get("Recall@5", 0), dense.get("Recall@5", 0), hybrid.get("Recall@5", 0)]
    mrr = [kw.get("MRR", 0), dense.get("MRR", 0), hybrid.get("MRR", 0)]
    csr = [kw.get("Constraint Satisfaction Rate", 0), dense.get("Constraint Satisfaction Rate", 0), hybrid.get("Constraint Satisfaction Rate", 0)]
    acc = [kw.get("Answer Accuracy", 0), dense.get("Answer Accuracy", 0), hybrid.get("Answer Accuracy", 0)]
    latency = [kw.get("Average Latency (ms)", 0), dense.get("Average Latency (ms)", 0), hybrid.get("Average Latency (ms)", 0)]

    # 1. Main Retrieval Performance Comparison (Precision@5, Recall@5, MRR)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(approaches))
    width = 0.25

    rects1 = ax.bar(x - width, p5, width, label="Precision@5", color="#34495e")
    rects2 = ax.bar(x, r5, width, label="Recall@5", color="#2980b9")
    rects3 = ax.bar(x + width, mrr, width, label="MRR", color="#27ae60")

    ax.set_ylabel("Score (0.0 - 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Retrieval Performance Comparison Across Approaches", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(approaches, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left")

    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.2f}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    chart1_path = output_dir / "precision_recall_mrr_comparison.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    generated_files.append(chart1_path.name)

    # 2. Constraint Satisfaction Rate Comparison
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(approaches, csr, color=colors, width=0.5)
    ax.set_ylabel("Constraint Satisfaction Rate (0.0 - 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Constraint Satisfaction Rate (CSR) by Retrieval Approach", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.15)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height * 100:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    chart2_path = output_dir / "constraint_satisfaction_rate.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    generated_files.append(chart2_path.name)

    # 3. Response Latency Breakdown
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(approaches, latency, color=["#f39c12", "#e67e22", "#d35400"], width=0.5)
    ax.set_ylabel("Latency (milliseconds)", fontsize=11, fontweight="bold")
    ax.set_title("Average Retrieval Latency per Query", fontsize=12, fontweight="bold", pad=12)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f} ms",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    chart3_path = output_dir / "latency_breakdown.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    generated_files.append(chart3_path.name)

    return generated_files
