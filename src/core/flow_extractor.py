import subprocess
import time
from pathlib import Path
import shutil
import os

CONTAINER_NAME = "cicflowmeter:offline"

def _ensure_docker_available():
    if shutil.which("docker") is None:
        raise EnvironmentError("Docker is not installed or not in PATH")

def _ensure_image_exists(image: str):
    try:
        subprocess.run(
            ["docker", "image", "inspect", image],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise EnvironmentError(f"Docker image '{image}' not found locally")

def extract_flows(pcap_path: Path, out_dir: Path) -> list[Path]:
    """
    Runs CICFlowMeter Docker container on a pcap file or directory.
    Returns list of generated CSV files.
    """
    _ensure_docker_available()
    _ensure_image_exists(CONTAINER_NAME)

    pcap_path = Path(pcap_path).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not pcap_path.exists():
        raise FileNotFoundError(f"PCAP path does not exist: {pcap_path}")

    if pcap_path.is_dir():
        mount_dir = pcap_path
        input_inside_container = "/data"
    else:
        mount_dir = pcap_path.parent
        input_inside_container = f"/data/{pcap_path.name}"

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{mount_dir}:/data",
        "-v", f"{out_dir}:/out",
        CONTAINER_NAME,
        input_inside_container,
        "/out"
    ]

    try:
        uid, gid = os.getuid(), os.getgid()
        cmd[3:3] = ["-u", f"{uid}:{gid}"]
    except AttributeError:
        pass  # Windows compatibility

    print(f"[FLOW] Running CICFlowMeter: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    time.sleep(1)

    csvs = list(out_dir.glob("*_Flow.csv"))
    if not csvs:
        raise FileNotFoundError(f"No output CSVs found in {out_dir}")

    print(f"[FLOW] Extracted {len(csvs)} CSV(s)")
    return csvs
# src/core/flow_extractor.py
# import subprocess
# import time
# from pathlib import Path
# import shutil
# import os

# CONTAINER_NAME = "cicflowmeter:offline"

# def _ensure_docker_available():
#     if shutil.which("docker") is None:
#         raise EnvironmentError("Docker is not installed or not in PATH")

# def _ensure_image_exists(image: str):
#     try:
#         subprocess.run(
#             ["docker", "image", "inspect", image],
#             check=True,
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )
#     except subprocess.CalledProcessError:
#         raise EnvironmentError(f"Docker image '{image}' not found locally")

# def _csv_inputs_from_path(pcap_path: Path) -> list[Path]:
#     """
#     If pcap_path is a CSV file or a dir containing CSVs, return list of CSV Path objects.
#     """
#     if pcap_path.is_file() and pcap_path.suffix.lower() in (".csv", ".tsv"):
#         return [pcap_path]
#     if pcap_path.is_dir():
#         csvs = sorted(pcap_path.glob("*.csv"))
#         return csvs
#     return []

# def extract_flows(pcap_path: Path, out_dir: Path) -> list[Path]:
#     """
#     If pcap_path is a CSV or a directory of CSVs -> return those CSV paths (no extraction).
#     Otherwise run CICFlowMeter (docker) and return generated CSV files.
#     """
#     pcap_path = Path(pcap_path).resolve()
#     out_dir = Path(out_dir).resolve()
#     out_dir.mkdir(parents=True, exist_ok=True)

#     # --- CSV short-circuit: if user passed CSV(s) just forward them ---
#     csv_inputs = _csv_inputs_from_path(pcap_path)
#     if csv_inputs:
#         # If CSVs were passed, optionally copy them to out_dir (or use in place).
#         # We'll copy so pipeline reads from a single controlled out_dir.
#         copied = []
#         for csv in csv_inputs:
#             dest = out_dir / csv.name
#             shutil.copy2(csv, dest)
#             copied.append(dest)
#         print(f"[FLOW] Received {len(copied)} CSV(s) as input; skipping flow extraction.")
#         return copied

#     # --- otherwise run CICFlowMeter via docker as before ---
#     _ensure_docker_available()
#     _ensure_image_exists(CONTAINER_NAME)

#     if not pcap_path.exists():
#         raise FileNotFoundError(f"PCAP path does not exist: {pcap_path}")

#     if pcap_path.is_dir():
#         mount_dir = pcap_path
#         input_inside_container = "/data"
#     else:
#         mount_dir = pcap_path.parent
#         input_inside_container = f"/data/{pcap_path.name}"

#     cmd = [
#         "docker", "run", "--rm",
#         "-v", f"{mount_dir}:/data",
#         "-v", f"{out_dir}:/out",
#         CONTAINER_NAME,
#         input_inside_container,
#         "/out"
#     ]

#     try:
#         uid, gid = os.getuid(), os.getgid()
#         cmd[3:3] = ["-u", f"{uid}:{gid}"]
#     except AttributeError:
#         pass

#     print(f"[FLOW] Running CICFlowMeter: {' '.join(cmd)}")
#     subprocess.run(cmd, check=True)
#     time.sleep(1)

#     csvs = list(out_dir.glob("*_Flow.csv"))
#     if not csvs:
#         raise FileNotFoundError(f"No output CSVs found in {out_dir}")

#     print(f"[FLOW] Extracted {len(csvs)} CSV(s)")
#     return csvs
