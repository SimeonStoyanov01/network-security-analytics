import subprocess
import pandas as pd
import argparse
import os
import glob
import time

def run_cicflowmeter(pcap_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    # Extract directory and filename
    pcap_dir = os.path.abspath(os.path.dirname(pcap_path))
    pcap_file = os.path.basename(pcap_path)

    # Docker command: mount the directory and the output folder
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(pcap_path)}:/data",
        "-v", f"{os.path.abspath(output_dir)}:/out",
        "cicflowmeter",
        "./cfm",
        "/data",
        "/out"
    ]


    print(f"Running CICFlowMeter on: {pcap_path}")
    subprocess.run(cmd, check=True)

    # Wait briefly to ensure output is flushed
    time.sleep(1)

    # Find the CSV corresponding to our pcap
    base = os.path.splitext(pcap_file)[0]
    csv_pattern = os.path.join(output_dir, f"{base}_Flow.csv")
    matching_csv = glob.glob(csv_pattern)
    if not matching_csv:
        raise FileNotFoundError(f"Expected output CSV not found: {csv_pattern}")
    return matching_csv[0]

def main():
    parser = argparse.ArgumentParser(description="Extract flow features using CICFlowMeter.")
    parser.add_argument("--pcap", required=True, help="Path to input pcap file")
    parser.add_argument("--outdir", default="data/flows", help="Output directory for flow CSVs")
    parser.add_argument("--model", help="Path to trained ML model (optional)")
    args = parser.parse_args()

    csv_path = run_cicflowmeter(args.pcap, args.outdir)
    print(f"✅ Features extracted to: {csv_path}")

    # Optional: load and process features
    df = pd.read_csv(csv_path)
    print(f"Extracted {len(df)} flows, {len(df.columns)} features")

    # Example: if you already trained a scikit-learn model
    if args.model:
        import joblib
        clf = joblib.load(args.model)
        X = df.drop(columns=["Label"], errors="ignore")  # drop label if present
        preds = clf.predict(X)
        df["Prediction"] = preds
        out_csv = os.path.join(args.outdir, "predictions.csv")
        df.to_csv(out_csv, index=False)
        print(f"✅ Predictions saved to: {out_csv}")

if __name__ == "__main__":
    main()
