import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

df = pd.read_csv("/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_results/yolo11n_fps_26tops.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Rolling smoothing
window = 2
df["fps_smooth"] = df["fps"].rolling(window).mean()

plt.figure(figsize=(10,5))

# Raw FPS
plt.plot(df["timestamp"], df["fps"],
         alpha=0.3, marker="o", label="Raw FPS")

# Smoothed FPS
plt.plot(df["timestamp"], df["fps_smooth"],
         linewidth=2, label="Smoothed FPS")

plt.xlabel("Time")
plt.ylabel("FPS")
plt.title("YOLOv11n Inference FPS vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("fps_vs_time.png", dpi=300)
plt.show()

print("FPS plot saved.")
