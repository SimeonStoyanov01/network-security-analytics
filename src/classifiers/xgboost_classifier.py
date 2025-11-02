import pandas as pd
from pathlib import Path
import joblib
import numpy as np
import sys
import argparse

from core.alerting import log_alert

MODEL_PATH = Path(__file__).resolve().parent / "modelexport" / "xgboost_pipeline(2).pkl"
FEATURES_PATH = Path(__file__).parent / "modelexport" / "feature_names.pkl"

FEATURE_NAMES = None
_model = None

def load_model():
    global _model, FEATURE_NAMES
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        print(f"[MODEL] Loaded XGBoost pipeline from {MODEL_PATH.name}")
    if FEATURE_NAMES is None:
        FEATURE_NAMES = joblib.load(FEATURES_PATH)
        print(f"[MODEL] Loaded feature names from {FEATURES_PATH.name}")
    return _model

def preprocess_csv(csv_path: Path):
    model = load_model()  # ensures FEATURE_NAMES is loaded
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Fill missing columns with zeros
    for col in FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0

    # Keep only the columns the model expects, in the right order
    X_test = df[FEATURE_NAMES].copy()

    # keep only numeric features
    numeric_cols = X_test.select_dtypes(include=[np.number]).columns
    X_test = X_test[numeric_cols]

    # Fill NaNs with 0 (or another strategy if you prefer)
    X_test.fillna(0, inplace=True)

    return X_test



def predict_flows(csv_path: Path, save_csv: bool = True) -> pd.DataFrame:
    model = load_model()

    df_original = pd.read_csv(csv_path)
    df_original.columns = df_original.columns.str.strip()

    X = preprocess_csv(csv_path)

    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None
    
    # Create results dataframe
    results = X.copy()
    results["Prediction"] = y_pred
    if y_proba is not None:
        results["Probability"] = y_proba
        
    print(f"[PREDICT] Completed predictions for {len(X)} flows.")
    print("[DEBUG] Prediction value counts:")
    print(pd.Series(y_pred).value_counts())
   
    for i, pred in enumerate(y_pred):
        if pred == 1:
            flow = df_original.iloc[i].to_dict()  # original row with IPs
            log_alert(csv_path.stem, flow, pred)

    if save_csv:
        output_path = csv_path.parent / f"{csv_path.stem}_predictions.csv"
        results.to_csv(output_path, index=False)
        print(f"[PREDICT] Predictions saved to {output_path}")

    return results

def main():
    """Command line interface for the prediction script"""
    parser = argparse.ArgumentParser(description='Predict network attacks using XGBoost model')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file to process')
    parser.add_argument('--no-save', action='store_true', help='Skip saving predictions to file')
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    
    if not csv_path.exists():
        print(f"Error: CSV file '{csv_path}' not found!")
        sys.exit(1)
    
    print(f"[MAIN] Processing CSV file: {csv_path}")
    
    try:
        results = predict_flows(csv_path, save_csv=not args.no_save)
        print("\n[MAIN] Prediction completed successfully!")
        return 0
    except Exception as e:
        print(f"\n[MAIN] Error during prediction: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())