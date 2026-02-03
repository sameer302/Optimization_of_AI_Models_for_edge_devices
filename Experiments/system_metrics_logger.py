import argparse
import csv
from email import parser
from html import parser
import time
import os
import psutil
import subprocess
from datetime import datetime

LOG_INTERVAL = 1  # seconds
CSV_FILE = "hardware_metrics.csv"


def get_cpu():
    return psutil.cpu_percent(interval=None)

def get_cpu_freq():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_clock", "arm"], text=True)
        return int(out.strip().split("=")[1]) / 1e6  # MHz
    except:
        return None
    
def get_voltage():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_volts", "core"], text=True)
        return float(out.strip().split("=")[1].replace("V", ""))
    except:
        return None

def get_throttled_flags():
    try:
        out = subprocess.check_output(["vcgencmd", "get_throttled"], text=True)
        return out.strip().split("=")[1]  # hex flags
    except:
        return None

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
        # NEW: output path
    parser.add_argument(
        "--out",
        type=str,
        default="hardware_metrics.csv",
        help="Path to output CSV file"
    )
    parser.add_argument("--freq", action="store_true")
    parser.add_argument("--voltage", action="store_true")
    parser.add_argument("--throttle", action="store_true")

    args = parser.parse_args()

    csv_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True) if os.path.dirname(csv_path) else None

    fields = ["timestamp"]
    if args.temp:
        fields.append("temperature_C")
    if args.cpu:
        fields.append("cpu_percent")
    if args.memory:
        fields.append("memory_percent")
    if args.npu:
        fields.append("npu_utilization_percent")
    if args.freq:
        fields.append("cpu_freq_MHz")
    if args.voltage:
        fields.append("cpu_voltage_V")
    if args.throttle:
        fields.append("throttled_flags_hex")

    # Create descriptive header mapping for clarity
    header_descriptions = {
        "timestamp": "ISO8601 timestamp",
        "temperature_C": "System temperature (Celsius)",
        "cpu_percent": "CPU utilization (%)",
        "memory_percent": "Memory utilization (%)",
        "npu_utilization_percent": "NPU utilization (%)",
        "cpu_freq_MHz": "CPU frequency (MHz)",
        "cpu_voltage_V": "CPU voltage (Volts)",
        "throttled_flags_hex": "Throttled status flags (hex)"
    }

    with open(csv_path, "w", newline="") as f:
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
            if args.freq:
                row["cpu_freq_MHz"] = get_cpu_freq()
            if args.voltage:
                row["cpu_voltage_V"] = get_voltage()
            if args.throttle:
                row["throttled_flags_hex"] = get_throttled_flags()

            writer.writerow(row)
            f.flush()
            time.sleep(LOG_INTERVAL)

            if args.duration and (time.time() - start) >= args.duration:
                break


if __name__ == "__main__":
    main()