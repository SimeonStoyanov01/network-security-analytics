from pathlib import Path
import subprocess
import shutil
import time
import os

CONTAINER_NAME = "cicflowmeter:offline"

def _ensure_docker():
    if shutil.which("docker") is None:
        raise EnvironmentError("Docker is not installed or not found in PATH.")

def _check_image(image: str) -> bool:
    try:
        subprocess.run(["docker", "image", "inspect", image],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def run_cicflowmeter(pcap_input: str, output_dir: str):
    """
    Runs the Dockerized CICFlowMeter on a PCAP file or directory.
    Returns a list of generated CSV file paths.
    """
    _ensure_docker()
    if not _check_image(CONTAINER_NAME):
        raise EnvironmentError(f"Docker image '{CONTAINER_NAME}' not found. Please build it first.")

    pcap_path = Path(pcap_input).resolve()
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    mount_dir = pcap_path if pcap_path.is_dir() else pcap_path.parent
    inside = "/data" if pcap_path.is_dir() else f"/data/{pcap_path.name}"

    # Optional: ensure correct file permissions
    try:
        uid, gid = os.getuid(), os.getgid()
        user_flag = ["-u", f"{uid}:{gid}"]
    except AttributeError:
        user_flag = []

    cmd = [
        "docker", "run", "--rm",
        *user_flag,
        "-v", f"{mount_dir}:/data",
        "-v", f"{out_path}:/out",
        CONTAINER_NAME,
        inside,
        "/out",
    ]

    print(f"🚀 Running CICFlowMeter in Docker: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    time.sleep(1)
    csvs = list(out_path.glob("*_Flow.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSVs generated in {out_path}")
    return csvs
