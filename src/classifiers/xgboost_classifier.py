import pandas as pd
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "modelexport" / "xgboost_pipeline.pkl"
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        print(f"[MODEL] Loaded XGBoost pipeline from {MODEL_PATH.name}")
    return _model

import pandas as pd
from pathlib import Path

EXPECTED_FEATURES = [
    "ACK Flag Cnt", "Active Max", "Active Mean", "Active Min", "Active Std",
    "Bwd Header Len", "Bwd IAT Max", "Bwd IAT Mean", "Bwd IAT Min", "Bwd IAT Std",
    "Bwd IAT Tot", "Bwd PSH Flags", "Bwd Pkt Len Max", "Bwd Pkt Len Mean",
    "Bwd Pkt Len Min", "Bwd Pkt Len Std", "Bwd Pkts/s", "Bwd Seg Size Avg",
    "Bwd URG Flags", "CWE Flag Count", "Down/Up Ratio", "Dst IP", "ECE Flag Cnt",
    "FIN Flag Cnt", "Flow Duration", "Flow IAT Max", "Flow IAT Mean",
    "Flow IAT Min", "Flow IAT Std", "Flow ID", "Fwd Act Data Pkts",
    "Fwd Header Len", "Fwd IAT Max", "Fwd IAT Mean", "Fwd IAT Min", "Fwd IAT Std",
    "Fwd IAT Tot", "Fwd PSH Flags", "Fwd Pkt Len Max", "Fwd Pkt Len Mean",
    "Fwd Pkt Len Min", "Fwd Pkt Len Std", "Fwd Pkts/s", "Fwd Seg Size Avg",
    "Fwd Seg Size Min", "Fwd URG Flags", "Idle Max", "Idle Mean", "Idle Min",
    "Idle Std", "Init Bwd Win Byts", "Init Fwd Win Byts", "PSH Flag Cnt",
    "Pkt Len Max", "Pkt Len Mean", "Pkt Len Min", "Pkt Len Std", "Pkt Len Var",
    "Pkt Size Avg", "Protocol", "RST Flag Cnt", "SYN Flag Cnt", "Src IP",
    "Src Port", "Subflow Bwd Byts", "Subflow Bwd Pkts", "Subflow Fwd Byts",
    "Subflow Fwd Pkts", "Tot Bwd Pkts", "Tot Fwd Pkts", "TotLen Bwd Pkts",
    "TotLen Fwd Pkts", "URG Flag Cnt"
]


def preprocess_csv(csv_path: Path):
    model = load_model()
    df = pd.read_csv(csv_path)

    # Get the exact features model was trained on
    expected_features = list(model.feature_names_in_)

    # Keep only these features, add missing ones as 0
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0

    # Select columns in the exact order
    df = df[expected_features]

    # Convert everything to numeric (non-convertible strings -> 0)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
 
    return df

def predict_flows(csv_path: Path, save_csv: bool = True) -> pd.DataFrame:
    model = load_model()
    X = preprocess_csv(csv_path)

    y_pred = model.predict(X)
    X["Prediction"] = y_pred
    print(f"[PREDICT] Completed predictions for {len(X)} flows.")

    if save_csv:
        output_path = csv_path.parent / f"{csv_path.stem}_predictions.csv"
        X.to_csv(output_path, index=False)
        print(f"[PREDICT] Predictions saved to {output_path}")

    return X
