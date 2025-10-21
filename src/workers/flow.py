# src/workers/flow.py
from celery import Celery
from pathlib import Path
from core.pipeline import run_pipeline

app = Celery("flow_worker", broker="redis://localhost:6379/0")

@app.task
def process_pcap(pcap_path: str):
    pcap = Path(pcap_path)
    out_dir = pcap.parent.parent / "out" / pcap.stem
    return run_pipeline(pcap, out_dir)
