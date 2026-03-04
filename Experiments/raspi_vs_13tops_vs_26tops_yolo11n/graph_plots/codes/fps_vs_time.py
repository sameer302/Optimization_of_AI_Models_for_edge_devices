import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

data = """
timestamp,frame_count,fps
2026-02-03T20:21:10.627042,30,2.41
2026-02-03T20:21:22.893814,60,2.512
2026-02-03T20:21:34.647890,90,2.575
2026-02-03T20:21:46.489045,120,2.563
2026-02-03T20:21:58.409677,150,2.539
2026-02-03T20:22:10.103350,180,2.58
2026-02-03T20:22:22.023370,210,2.54
"""

# Load data
df = pd.read_csv(StringIO(data))

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
