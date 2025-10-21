from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
from workers.flow import process_pcap

WATCH_DIR = Path(__file__).resolve().parents[1] / "data" / "input"

class PcapHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".pcap"):
            return
        print(f"[WATCHER] Detected new PCAP: {event.src_path}")
        process_pcap.delay(event.src_path)

def start_watcher():
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    event_handler = PcapHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=False)
    observer.start()
    print(f"[WATCHER] Monitoring {WATCH_DIR} for new PCAP files...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
