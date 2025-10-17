from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from app.pipeline import process_pcap
from core.alerting import read_alerts
import time, shutil, json

app = FastAPI(title="Network Security Analytics API")

INPUT_DIR = Path("data/input")
OUT_DIR = Path("data/out")
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload_pcap(file: UploadFile = File(...)):
    """Accepts a PCAP file, runs the analysis pipeline, and returns generated alerts."""
    dest = INPUT_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    out_subdir = OUT_DIR / f"{dest.stem}_{int(time.time())}"
    out_subdir.mkdir(parents=True, exist_ok=True)

    try:
        alerts = process_pcap(str(dest), str(out_subdir))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"pcap": dest.name, "alerts": alerts}

@app.get("/alerts")
def get_alerts(limit: int = 100):
    """Return last N alerts (default: 100)."""
    return read_alerts(limit)
