import argparse
import csv
import time
import os
import psutil
import subprocess
from datetime import datetime

LOG_INTERVAL = 1  # seconds
CSV_FILE = "hardware_metrics.csv"


def get_cpu():
    return psutil.cpu_percent(interval=None)


def get_memory():
    return psutil.virtual_memory().percent


def get_temp():
    temps = psutil.sensors_temperatures()
    if not temps:
        return None
    for sensor in temps.values():
        if sensor:
            return sensor[0].current
    return None


def get_npu():
    try:
        p = subprocess.Popen(
            ["hailortcli", "monitor"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        time.sleep(1.2)   # allow one refresh cycle
        p.terminate()

        out, _ = p.communicate(timeout=1)

        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                try:
                    util = float(parts[1])
                    fps = float(parts[2])
                    pid = int(parts[3])
                    return util, fps
                except ValueError:
                    continue

        return None, None

    except Exception:
        return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp", action="store_true")
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--memory", action="store_true")
    parser.add_argument("--npu", action="store_true")
    parser.add_argument("--duration", type=int, default=0,
                        help="seconds (0 = infinite)")
    args = parser.parse_args()

    fields = ["timestamp"]
    if args.temp:
        fields.append("temperature_C")
    if args.cpu:
        fields.append("cpu_percent")
    if args.memory:
        fields.append("memory_percent")
    if args.npu:
        fields.append("npu_utilization_percent")

    # Create descriptive header mapping for clarity
    header_descriptions = {
        "timestamp": "ISO8601 timestamp",
        "temperature_C": "System temperature (Celsius)",
        "cpu_percent": "CPU utilization (%)",
        "memory_percent": "Memory utilization (%)",
        "npu_utilization_percent": "NPU utilization (%)"
    }

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()  # Always write header

        start = time.time()
        while True:
            row = {"timestamp": datetime.now().isoformat()}

            if args.temp:
                row["temperature_C"] = get_temp()
            if args.cpu:
                row["cpu_percent"] = get_cpu()
            if args.memory:
                row["memory_percent"] = get_memory()
            if args.npu:
                util, fps = get_npu()
                row["npu_utilization_percent"] = util

            writer.writerow(row)
            f.flush()
            time.sleep(LOG_INTERVAL)

            if args.duration and (time.time() - start) >= args.duration:
                break


if __name__ == "__main__":
    main()