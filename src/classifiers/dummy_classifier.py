# import pandas as pd
# import random

# class DummyClassifier:
#     """
#     Stub model for testing. Later replace with joblib.load(model_path).
#     """
#     def predict(self, df: pd.DataFrame):
#         return [random.choice([0, 1]) for _ in range(len(df))]
import pandas as pd
import random
from pathlib import Path

def classify_flow(csv_path: Path, save_csv: bool = True) -> pd.DataFrame:
    """
    Mock classifier: randomly assigns 0 (benign) or 1 (malicious).
    Returns DataFrame with predictions.
    """
    df = pd.read_csv(csv_path)
    df["Label"] = [random.choice([0, 1]) for _ in range(len(df))]
    if save_csv:
        out_path = csv_path.with_name(csv_path.stem + "_classified.csv")
        df.to_csv(out_path, index=False)
        print(f"[CLASSIFIER] Saved classified CSV to {out_path.name}")
    print(f"[CLASSIFIER] Processed {len(df)} flows from {csv_path.name}")
    return df
