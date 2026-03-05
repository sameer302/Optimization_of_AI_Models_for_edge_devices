import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_results/yolo11n_system_metrics_cpu_ncnn.csv"

df = pd.read_csv(csv_file)

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Smooth voltage signal
window = 20
df["voltage_smooth"] = df["cpu_voltage_V"].rolling(window).mean()

plt.figure(figsize=(10,5))

# Raw voltage (light)
plt.plot(df["timestamp"], df["cpu_voltage_V"],
         alpha=0.3, label="Raw CPU Voltage")

# Smoothed voltage
plt.plot(df["timestamp"], df["voltage_smooth"],
         linewidth=2, label="Smoothed CPU Voltage")

plt.xlabel("Time")
plt.ylabel("CPU Voltage (V)")
plt.title("CPU Voltage vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("cpu_voltage_vs_time.png", dpi=300)
plt.close()

print("CPU voltage plot saved.")