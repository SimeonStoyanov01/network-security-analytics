from core.flow_extractor import run_cicflowmeter
from core.classifier import DummyClassifier
from core.alerting import log_alerts, build_alerts
import pandas as pd

def process_pcap(pcap_path: str, out_dir: str):
    """
    Full pipeline:
    1. Run CICFlowMeter
    2. Generate predictions
    3. Save alerts
    """
    csvs = run_cicflowmeter(pcap_path, out_dir)
    model = DummyClassifier()

    all_alerts = []
    for csv in csvs:
        df = pd.read_csv(csv)
        preds = model.predict(df)
        alerts = build_alerts(pcap_path, csv.name, preds, df)
        log_alerts(alerts)
        all_alerts.extend(alerts)

    return all_alerts
