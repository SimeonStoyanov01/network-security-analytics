import pandas as pd
from pathlib import Path
import joblib
import numpy as np
import sys
import argparse

MODEL_PATH = Path(__file__).resolve().parent / "modelexport" / "xgboost_pipeline.pkl"
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        print(f"[MODEL] Loaded XGBoost pipeline from {MODEL_PATH.name}")
    return _model

def preprocess_csv(csv_path: Path):
    # Load data
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Drop same columns as training
    drop_cols = ["Timestamp", "Fwd Byts/b Avg", "Fwd Pkts/b Avg", "Fwd Blk Rate Avg",
                 "Bwd Byts/b Avg", "Bwd Pkts/b Avg", "Bwd Blk Rate Avg",
                 "Flow Byts/s", "Flow Pkts/s", "Dst Port"]
    
    for col in drop_cols:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    
    # Drop constant columns
    X_test = df.select_dtypes(include=[np.number])
    constant_cols = X_test.nunique()[X_test.nunique() <= 1].index.tolist()
    if constant_cols:
        print(f"[PREPROCESS] Dropped constant columns: {constant_cols}")
        X_test.drop(constant_cols, axis=1, inplace=True)
    
    # Get expected feature count from pipeline model
    model = load_model()
    expected_features = len(model.named_steps['standardscaler'].mean_)
    
    # Ensure we have the right number of features
    if len(X_test.columns) != expected_features:
        print(f"[PREPROCESS] Adjusting features: {len(X_test.columns)} -> {expected_features}")
        # Add dummy columns if we have fewer features
        while len(X_test.columns) < expected_features:
            X_test[f'dummy_{len(X_test.columns)}'] = 0
        # Drop extra columns if we have more features  
        X_test = X_test.iloc[:, :expected_features]
    
    return X_test

def predict_flows(csv_path: Path, save_csv: bool = True) -> pd.DataFrame:
    model = load_model()
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