# src/core/pipeline.py
from core.flow_extractor import extract_flows
from classifiers.dummy_classifier import classify_flow
from classifiers.xgboost_classifier import predict_flows
from core.alerting import log_alert

def run_pipeline(pcap_path, out_dir):
    """Run the full pipeline: extract → classify → alert."""
    csvs = extract_flows(pcap_path, out_dir)
    for csv in csvs:
        df = predict_flows(csv, save_csv=True) # Changed to use classify_flow from dummy_classifier.py, revert to predict_flows for xgboost
        for _, row in df.iterrows():
            log_alert(pcap_path.name, row.dropna().to_dict(), row["Label"])
    return f"Processed {pcap_path.name} ({len(csvs)} CSVs)"

