import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app import config

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])

@router.get("/results")
def get_evaluation_results():
    metrics_path = config.RESULTS_DIR / "metrics.json"
    comparison_csv_path = config.RESULTS_DIR / "comparison.csv"
    
    if not metrics_path.exists():
        return {
            "status": "not_run",
            "message": "Evaluation experiments have not been executed yet. Run POST /api/evaluation/run to execute.",
            "metrics": {},
            "charts_available": []
        }

    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
            
        charts = []
        if config.CHARTS_DIR.exists():
            for p in config.CHARTS_DIR.glob("*.png"):
                charts.append(p.name)

        return {
            "status": "available",
            "metrics": metrics_data,
            "charts": charts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed loading evaluation metrics: {e}")

@router.post("/run")
def trigger_evaluation_run(background_tasks: BackgroundTasks):
    from experiments.run_experiment import run_benchmark_suite
    try:
        background_tasks.add_task(run_benchmark_suite)
        return {
            "status": "initiated",
            "message": "Benchmark experiment suite triggered in background. Charts and JSON metrics will update shortly."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed initiating evaluation run: {e}")
