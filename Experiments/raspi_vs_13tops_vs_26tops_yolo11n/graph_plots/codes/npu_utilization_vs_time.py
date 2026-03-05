import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_results/yolo11n_system_metrics_26tops.csv"

df = pd.read_csv(csv_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Rolling smoothing window
window = 20

df["npu_smooth"] = df["npu_utilization_percent"].rolling(window).mean()

plt.figure(figsize=(10,5))

plt.plot(df["timestamp"], df["npu_utilization_percent"], alpha=0.3, label="Raw NPU %")
plt.plot(df["timestamp"], df["npu_smooth"], linewidth=2, label="Smoothed NPU %")
plt.xlabel("Time")
plt.ylabel("NPU Usage (%)")
plt.title("NPU Usage vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("npu_utilization_vs_time.png", dpi=300)
plt.close()

print("NPU utilization plot saved.")