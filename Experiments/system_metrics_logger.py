import argparse
import csv
import time
import os
import psutil
import subprocess
from datetime import datetime

LOG_INTERVAL = 1  # seconds


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


# --- Hailo device handle (initialized once if needed) ---
_hailo_device = None

def _get_hailo_device():
    global _hailo_device
    if _hailo_device is None:
        try:
            from hailo_platform import Device
            _hailo_device = Device()
        except Exception as e:
            print(f"[WARNING] Could not initialize Hailo device: {e}")
            _hailo_device = False  # Mark as failed so we don't retry
    return _hailo_device if _hailo_device else None


def get_hailo_temp():
    """Get Hailo chip temperature in Celsius via ts0_temperature sensor."""
    device = _get_hailo_device()
    if device is None:
        return None
    try:
        return device.control.get_chip_temperature().ts0_temperature
    except Exception:
        return None


def get_hailo_clock():
    """Get Hailo neural network core clock rate in MHz."""
    device = _get_hailo_device()
    if device is None:
        return None
    try:
        info = device.control.get_extended_device_information()
        # Parse "Neural Network Core Clock Rate: 400.0MHz" from string representation
        for line in str(info).splitlines():
            if "Neural Network Core Clock Rate" in line:
                # Extract numeric value before "MHz"
                clock_str = line.split(":")[1].strip().replace("MHz", "")
                return float(clock_str)
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp", action="store_true", help="Log CPU/system temperature")
    parser.add_argument("--cpu", action="store_true", help="Log CPU utilization")
    parser.add_argument("--memory", action="store_true", help="Log memory utilization")
    parser.add_argument("--npu", action="store_true", help="Log NPU utilization via hailortcli")
    parser.add_argument("--freq", action="store_true", help="Log CPU frequency")
    parser.add_argument("--voltage", action="store_true", help="Log CPU core voltage")
    parser.add_argument("--throttle", action="store_true", help="Log throttled status flags")
    parser.add_argument("--hailo-temp", action="store_true", help="Log Hailo chip temperature (C)")
    parser.add_argument("--hailo-clock", action="store_true", help="Log Hailo neural core clock rate (MHz)")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0 = infinite)")
    parser.add_argument("--out", type=str, default="hardware_metrics.csv", help="Path to output CSV file")

    args = parser.parse_args()

    csv_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True) if os.path.dirname(csv_path) else None

    # Build CSV fields based on selected flags
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
    if args.hailo_temp:
        fields.append("hailo_temp_C")
    if args.hailo_clock:
        fields.append("hailo_clock_MHz")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

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
            if args.hailo_temp:
                row["hailo_temp_C"] = get_hailo_temp()
            if args.hailo_clock:
                row["hailo_clock_MHz"] = get_hailo_clock()

            writer.writerow(row)
            f.flush()
            time.sleep(LOG_INTERVAL)

            if args.duration and (time.time() - start) >= args.duration:
                break


if __name__ == "__main__":
    main()