from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import subprocess
import time
import os
import pandas as pd
import random
import json

app = FastAPI()

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "data" / "input"
OUT_DIR = REPO_ROOT / "data" / "out"
ALERTS_FILE = REPO_ROOT / "data" / "alerts.txt"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_flows(pcap_path: Path, out_subdir: Path):
    # Use the existing capture.run_cicflowmeter which runs the cicflowmeter docker image.
    run_cicflowmeter = None
    # Try common import paths
    try:
        from capture import run_cicflowmeter as rc
        run_cicflowmeter = rc
    except Exception:
        try:
            from src.capture import run_cicflowmeter as rc2
            run_cicflowmeter = rc2
        except Exception:
            # Try loading the file directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("capture_mod", str(Path(__file__).resolve().parents[1] / "capture.py"))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                run_cicflowmeter = getattr(mod, "run_cicflowmeter", None)

    if run_cicflowmeter is None:
        raise RuntimeError("capture.run_cicflowmeter is not available")

    # run_cicflowmeter accepts a pcap path (file or dir) and an output dir
    csvs = run_cicflowmeter(str(pcap_path), str(out_subdir))
    return csvs


def classify_and_log(out_subdir: Path, pcap_name: str):
    alerts = []
    for csv in out_subdir.glob("*_Flow.csv"):
        try:
            df = pd.read_csv(csv)
        except Exception:
            continue
        for i, row in df.iterrows():
            label = int(random.choice([0, 1]))
            if label == 1:
                alert = {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "pcap": pcap_name,
                    "flow_file": str(csv.name),
                    "row_index": int(i),
                    "features": row.dropna().to_dict(),
                }
                alerts.append(alert)
                with ALERTS_FILE.open("a") as fh:
                    fh.write(json.dumps(alert) + "\n")
    return alerts


@app.post("/upload")
async def upload_pcap(file: UploadFile = File(...)):
    # Save uploaded pcap
    dest = INPUT_DIR / file.filename
    temp = dest.with_suffix(dest.suffix + ".partial")
    with temp.open("wb") as f:
        content = await file.read()
        f.write(content)
    temp.rename(dest)

    # Process synchronously for now
    out_subdir = OUT_DIR / (dest.stem + f"_{int(time.time())}")
    out_subdir.mkdir(parents=True, exist_ok=True)
    try:
        extract_flows(dest, out_subdir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    alerts = classify_and_log(out_subdir, dest.name)
    return {"pcap": dest.name, "csvs": [str(p.name) for p in out_subdir.glob("*_Flow.csv")], "alerts": len(alerts)}


@app.get("/alerts")
def get_alerts(limit: int = 100):
    if not ALERTS_FILE.exists():
        return []
    lines = ALERTS_FILE.read_text().strip().splitlines()
    lines = lines[-limit:]
    return [json.loads(l) for l in lines]
