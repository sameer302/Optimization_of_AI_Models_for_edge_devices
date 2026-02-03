#!/usr/bin/env python3
"""
Wrapper to run detection_simple.py from experiments folder.
Usage: python run_detection_simple.py [args...]
Any args are forwarded to detection_simple.py
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# workspace root is two levels up from this script
workspace_root = Path(__file__).resolve().parents[2]

det = workspace_root / "hailo-rpi5-examples" / "basic_pipelines" / "detection_simple.py"
# expected path to detection_simple.py inside workspace
det = workspace_root / "hailo-rpi5-examples" / "basic_pipelines" / "detection_simple.py"
if not det.exists():
    print(f"ERROR: detection_simple.py not found at: {det}")
    sys.exit(1)

# parse only the --csv arg here and forward remaining args
parser = argparse.ArgumentParser(description="Wrapper to run detection_simple.py from experiments folder.")
parser.add_argument('--csv', help='Path to write CSV log (file or directory).', default=None)
args, rest = parser.parse_known_args()

# Build forwarding args: include other args plus --csv if provided
forward_args = rest
if args.csv:
    forward_args = forward_args + ["--csv", args.csv]

cmd = [sys.executable, str(det)] + forward_args
ret = subprocess.run(cmd, env=os.environ)
sys.exit(ret.returncode)
