import subprocess
import pandas as pd
import argparse
import os
from pathlib import Path
import glob
import time
import shutil
import sys

container_name = "cicflowmeter:offline"

def _ensure_docker_available():
    if shutil.which("docker") is None:
        raise EnvironmentError("Docker executable not found in PATH. Install Docker to continue.")


def _ensure_image_exists(image: str) -> bool:
    # Return True if docker image exists locally
    try:
        subprocess.run(["docker", "image", "inspect", image], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def run_cicflowmeter(pcap_input: str, output_dir: str):
    # Expand user and resolve
    pcap_input = os.path.expanduser(pcap_input)
    output_dir = os.path.expanduser(output_dir)

    pcap_path = Path(pcap_input).resolve()
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    # Determine mount dir and container input path
    if pcap_path.is_dir():
        mount_dir = pcap_path
        input_inside_container = "/data"
    else:
        mount_dir = pcap_path.parent
        input_inside_container = f"/data/{pcap_path.name}"

    # Basic pre-checks
    _ensure_docker_available()
    if not _ensure_image_exists(container_name):
        raise EnvironmentError(
            f"Docker image '{container_name}' not found locally. Build it first (see CICFlowMeter/Dockerfile) or pull it."
        )

    # Construct the exact docker command you provided: mount pcap dir to /data, out dir to /out, image, then /data /out
    # When input is a single file we still mount the parent and pass /data/<file>
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{mount_dir}:/data",
        "-v", f"{out_path}:/out",
        container_name,
        input_inside_container,
        "/out",
    ]

    # If running on a POSIX system, run the container as the calling user so files
    # created inside the mounted output directory are owned by the host user
    try:
        uid = os.getuid()
        gid = os.getgid()
    except AttributeError:
        uid = None
        gid = None

    if uid is not None:
        # insert the -u UID:GID after 'docker', 'run', '--rm' (index 3)
        cmd[3:3] = ["-u", f"{uid}:{gid}"]

    print(f"Running CICFlowMeter in Docker: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Docker run failed with exit code {e.returncode}") from e

    # Wait briefly to ensure output is flushed
    time.sleep(1)

    csvs = list(out_path.glob("*_Flow.csv"))
    if not csvs:
        raise FileNotFoundError(f"No output CSVs found in {out_path}")
    return csvs

def main():
    parser = argparse.ArgumentParser(description="Extract flow features using CICFlowMeter.")
    parser.add_argument("--pcap", required=True, help="Path to input pcap file or folder")
    parser.add_argument("--outdir", default="data/flows", help="Output directory for flow CSVs")
    parser.add_argument("--model", help="Path to trained ML model (optional)")
    args = parser.parse_args()

    csv_files = run_cicflowmeter(args.pcap, args.outdir)
    print(f"✅ Features extracted to {len(csv_files)} CSV(s): {[str(f) for f in csv_files]}")

    # Example: load and predict if model is provided
    if args.model:
        import joblib
        clf = joblib.load(args.model)
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            X = df.drop(columns=["Label"], errors="ignore")
            df["Prediction"] = clf.predict(X)
            out_csv = csv_file.with_name(f"predictions_{csv_file.name}")
            df.to_csv(out_csv, index=False)
            print(f"✅ Predictions saved to: {out_csv}")

if __name__ == "__main__":
    main()
