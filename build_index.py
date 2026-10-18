import sys
import pandas as pd
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from preprocessing.documents import process_dataset
from embeddings.faiss_index import FAISSIndexManager

def main():
    print("=" * 60)
    print("RESTROBOT -- FAISS VECTOR INDEX BUILDER")
    print("=" * 60)

    raw_csv = config.DATA_DIR / "sample_restaurants.csv"
    if not raw_csv.exists():
        print(f"Error: {raw_csv} not found!")
        sys.exit(1)

    print(f"Loading raw dataset: {raw_csv}")
    raw_df = pd.read_csv(raw_csv)
    print(f"Loaded {len(raw_df)} menu items across restaurants.")

    print("Preprocessing text and creating document representations...")
    processed_df = process_dataset(raw_df)

    processed_csv = config.PROCESSED_CSV_PATH
    processed_csv.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(processed_csv, index=False)
    print(f"[OK] Saved processed dataset to {processed_csv}")

    documents = processed_df.to_dict(orient="records")

    print("\nBuilding FAISS vector index...")
    faiss_manager = FAISSIndexManager(models_dir=config.BASE_DIR / "models")
    faiss_manager.build_and_save(documents)

    print("\n====================================================")
    print("FAISS INDEX BUILD COMPLETE AND READY FOR RETRIEVAL!")
    print("====================================================")

if __name__ == "__main__":
    main()
