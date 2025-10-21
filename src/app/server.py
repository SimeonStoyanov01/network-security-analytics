from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import json
from workers.flow import process_pcap

app = FastAPI(title="Network Security Analytics API")

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "data" / "input"
ALERTS_FILE = BASE_DIR / "data" / "alerts.jsonl"

INPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload_pcap(file: UploadFile = File(...)):
    dest = INPUT_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    print(f"[API] Uploaded {file.filename}")
    process_pcap.delay(str(dest))
    return {"status": "queued", "file": file.filename}

@app.get("/alerts")
def get_alerts(limit: int = 100):
    if not ALERTS_FILE.exists():
        return []
    lines = ALERTS_FILE.read_text().splitlines()[-limit:]
    return [json.loads(line) for line in lines]
