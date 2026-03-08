#!/usr/bin/env python3
"""
Wrapper to run detection_simple.py + system_metrics_logger.py in parallel,
mirroring the behaviour of the original bash experiment script.

Usage:
    python run_detection_app.py [options] [extra args forwarded to detection_simple.py]

Defaults:
    --duration   1800  (seconds)
    --output-dir ./results

Ctrl+C / SIGTERM will cleanly kill both child processes.
"""
import os
import sys
import signal
import subprocess
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------
DEFAULT_DURATION   = 1800
DEFAULT_OUTPUT_DIR = "./results"


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run detection_simple.py + system_metrics_logger.py in parallel."
    )

    # Experiment-level knobs
    parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help=f"Max run time in seconds (default: {DEFAULT_DURATION}).",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for result CSVs (default: {DEFAULT_OUTPUT_DIR}).",
    )

    # Metrics logger toggles (mirror system_metrics_logger.py flags)
    parser.add_argument("--cpu",    action="store_true", default=True,  help="Log CPU metrics.")
    parser.add_argument("--temp",   action="store_true", default=True,  help="Log temperature metrics.")
    parser.add_argument("--npu",    action="store_true", default=True,  help="Log NPU metrics.")
    parser.add_argument("--memory", action="store_true", default=True,  help="Log memory metrics.")
    parser.add_argument(
        "--metrics-csv",
        default=None,
        help="Override path for system-metrics CSV (default: <output-dir>/system_metrics.csv).",
    )

    # Detection app knobs
    parser.add_argument(
        "--csv",
        default=None,
        help="Override path for detection FPS CSV (default: <output-dir>/detection_fps.csv).",
    )
    parser.add_argument(
        "--input",
        default="rpi",
        help="Input source forwarded to detection_simple.py (default: rpi).",
    )
    parser.add_argument(
        "--hef-path",
        default=None,
        help="Path to .hef model file, forwarded to detection_simple.py.",
    )

    # Anything not recognised above is forwarded verbatim to detection_simple.py
    return parser.parse_known_args(argv)


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
def resolve_detection_script() -> Path:
    workspace_root = Path(__file__).resolve().parents[2]
    target = (
        workspace_root
        / "hailo-rpi5-examples"
        / "basic_pipelines"
        / "detection_simple.py"
    )
    if not target.exists():
        print(f"ERROR: detection_simple.py not found at: {target}")
        sys.exit(1)
    return target


def resolve_metrics_script() -> Path:
    target = Path(__file__).resolve().parent.parent / "system_metrics_logger.py"
    if not target.exists():
        print(f"ERROR: system_metrics_logger.py not found at: {target}")
        sys.exit(1)
    return target


# ---------------------------------------------------------------------------
# Command builders
# ---------------------------------------------------------------------------
def build_metrics_cmd(metrics_script: Path, args, output_dir: Path) -> list:
    csv_path = args.metrics_csv or str(output_dir / "system_metrics.csv")
    cmd = [sys.executable, str(metrics_script), "--out", csv_path]
    if args.cpu:    cmd.append("--cpu")
    if args.temp:   cmd.append("--temp")
    if args.npu:    cmd.append("--npu")
    if args.memory: cmd.append("--memory")
    return cmd


def build_detection_cmd(detection_script: Path, args, rest: list, output_dir: Path) -> list:
    csv_path = args.csv or str(output_dir / "detection_fps.csv")
    cmd = [sys.executable, str(detection_script), "--csv", csv_path]
    if args.input:    cmd += ["--input", args.input]
    if args.hef_path: cmd += ["--hef-path", args.hef_path]
    cmd += rest   # forward any unrecognised args verbatim
    return cmd


# ---------------------------------------------------------------------------
# Process management
# ---------------------------------------------------------------------------
processes: list[subprocess.Popen] = []


def cleanup(signum=None, frame=None):
    print("\nStopping experiment...")
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    sys.exit(0)


def run_experiment(metrics_cmd: list, detection_cmd: list, duration: int):
    signal.signal(signal.SIGINT,  cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    env = os.environ.copy()

    print(f"[metrics  ] {' '.join(metrics_cmd)}")
    print(f"[detection] {' '.join(detection_cmd)}")
    print(f"[duration ] {duration}s\n")

    metrics_proc   = subprocess.Popen(metrics_cmd,   env=env)
    detection_proc = subprocess.Popen(detection_cmd, env={**env, "HAILO_MONITOR": "1"})

    processes.extend([metrics_proc, detection_proc])

    try:
        metrics_proc.wait(timeout=duration)
        detection_proc.wait(timeout=duration)
    except subprocess.TimeoutExpired:
        print(f"Duration ({duration}s) reached — stopping processes.")
        cleanup()

    print("Experiment completed. Results saved in: " + str(Path(DEFAULT_OUTPUT_DIR).resolve()))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    args, rest = parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    detection_script = resolve_detection_script()
    metrics_script   = resolve_metrics_script()

    metrics_cmd   = build_metrics_cmd(metrics_script, args, output_dir)
    detection_cmd = build_detection_cmd(detection_script, args, rest, output_dir)

    run_experiment(metrics_cmd, detection_cmd, args.duration)


if __name__ == "__main__":
    main()