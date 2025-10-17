import json
import time
from pathlib import Path

ALERTS_FILE = Path("data/alerts.jsonl")

def log_alerts(alerts):
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ALERTS_FILE.open("a") as f:
        for alert in alerts:
            f.write(json.dumps(alert) + "\n")

def build_alerts(pcap_name, csv_name, predictions, df):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    alerts = []
    for i, pred in enumerate(predictions):
        if pred == 1:
            alerts.append({
                "timestamp": timestamp,
                "pcap": pcap_name,
                "flow_file": csv_name,
                "row": i,
                "prediction": int(pred),
            })
    return alerts

def read_alerts(limit: int = 100):
    if not ALERTS_FILE.exists():
        return []
    lines = ALERTS_FILE.read_text().splitlines()[-limit:]
    return [json.loads(line) for line in lines]
