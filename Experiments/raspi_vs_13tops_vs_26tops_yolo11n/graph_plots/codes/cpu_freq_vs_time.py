import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_results/yolo11n_system_metrics_26tops.csv"

df = pd.read_csv(csv_file)

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Convert MHz → GHz
df["cpu_freq_GHz"] = df["cpu_freq_MHz"] / 1000

# Round to remove measurement noise
df["cpu_freq_GHz"] = df["cpu_freq_GHz"].round(3)

# Rolling smoothing
window = 20
df["freq_smooth"] = df["cpu_freq_GHz"].rolling(window).mean()

plt.figure(figsize=(10,5))

# Raw values (very light)
plt.plot(df["timestamp"], df["cpu_freq_GHz"],
         alpha=0.2, label="Raw Frequency")

# Smoothed values
plt.plot(df["timestamp"], df["freq_smooth"],
         linewidth=2, label="Smoothed Frequency")

plt.xlabel("Time")
plt.ylabel("CPU Frequency (GHz)")
plt.title("Raspberry Pi 5 CPU Frequency vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

# Important: zoom into realistic range
plt.ylim(2.35, 2.45)

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("cpu_frequency_vs_time.png", dpi=300)
plt.show()

print("CPU frequency plot saved.")