import pandas as pd
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "modelexport" / "xgboost_pipeline(1).pkl"
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
    'Protocol', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts',
    'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max', 'Fwd Pkt Len Min',
    'Fwd Pkt Len Mean', 'Fwd Pkt Len Std', 'Bwd Pkt Len Max', 'Bwd Pkt Len Min',
    'Bwd Pkt Len Mean', 'Bwd Pkt Len Std', 'Flow IAT Mean', 'Flow IAT Std',
    'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Tot', 'Fwd IAT Mean', 'Fwd IAT Std',
    'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Tot', 'Bwd IAT Mean', 'Bwd IAT Std',
    'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags', 'Fwd Header Len', 'Bwd Header Len',
    'Pkt Len Min', 'Pkt Len Max', 'Pkt Len Mean', 'Pkt Len Std', 'Pkt Len Var',
    'FIN Flag Cnt', 'SYN Flag Cnt', 'RST Flag Cnt', 'PSH Flag Cnt', 'ACK Flag Cnt',
    'URG Flag Cnt', 'ECE Flag Cnt', 'Down/Up Ratio', 'Pkt Size Avg', 'Fwd Seg Size Avg',
    'Bwd Seg Size Avg', 'Subflow Fwd Pkts', 'Subflow Fwd Byts', 'Subflow Bwd Pkts',
    'Subflow Bwd Byts', 'Init Fwd Win Byts', 'Init Bwd Win Byts', 'Fwd Act Data Pkts',
    'Fwd Seg Size Min', 'Active Mean', 'Active Std', 'Active Max', 'Active Min',
    'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
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
