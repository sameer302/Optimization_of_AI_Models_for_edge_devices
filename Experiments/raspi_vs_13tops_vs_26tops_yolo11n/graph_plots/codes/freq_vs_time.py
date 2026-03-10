import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/fps_and_system_metrics_csv_logs/yolo11n_system_metrics_26tops.csv"

df = pd.read_csv(csv_file)

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

plt.figure(figsize=(10,5))

# Raw values (very light)
plt.plot(df["timestamp"], df["hailo_clock_MHz"],
         alpha=0.2, label="Raw Frequency")

# Smoothed values
plt.plot(df["timestamp"], df["hailo_clock_MHz"],
         linewidth=2, label="Smoothed Frequency")

plt.xlabel("Time")
plt.ylabel("NPU Frequency (GHz)")
plt.title("Raspberry Pi 5 NPU Frequency vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("npu_frequency_vs_time.png", dpi=300)
plt.show()

print("NPU frequency plot saved.")