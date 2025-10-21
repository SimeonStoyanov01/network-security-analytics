import json
import time
from pathlib import Path

ALERTS_FILE = Path(__file__).resolve().parents[2] / "data" / "alerts.jsonl"
ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
def log_alert(pcap_name: str, flow: dict, prediction: int):
    if prediction != 1:
        return

    # Pick only a few useful fields
    summary = {
        "Flow ID": flow.get("Flow ID"),
        "Src IP": flow.get("Src IP"),
        "Src Port": flow.get("Src Port"),
        "Dst IP": flow.get("Dst IP"),
        "Dst Port": flow.get("Dst Port"),
        "Protocol": flow.get("Protocol"),
        "Flow Duration": flow.get("Flow Duration"),
        "Tot Fwd Pkts": flow.get("Tot Fwd Pkts"),
        "Tot Bwd Pkts": flow.get("Tot Bwd Pkts"),
        "Label": flow.get("Label", "N/A")
    }

    alert = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pcap": pcap_name,
        "summary": summary,
        "message": f"Potential intrusion detected between {summary['Src IP']} and {summary['Dst IP']}"
    }

    with ALERTS_FILE.open("a") as f:
        json.dump(alert, f, indent=2)
        f.write("\n")

    print(f"[ALERT] 🚨 Suspicious flow detected from {summary['Src IP']} → {summary['Dst IP']} ({pcap_name})")
