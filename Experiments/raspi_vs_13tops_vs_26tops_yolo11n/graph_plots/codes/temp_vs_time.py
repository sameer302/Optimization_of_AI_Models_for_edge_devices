import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/fps_and_system_metrics_csv_logs/yolo11n_system_metrics_26tops.csv"

df = pd.read_csv(csv_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Smooth values using rolling average
window = 20
df["temperature_smooth"] = df["hailo_temp_C"].rolling(window).mean()

plt.figure(figsize=(10,5))

# Raw values (light)
plt.plot(df["timestamp"], df["hailo_temp_C"], alpha=0.3, label="Raw")

# Smoothed values
plt.plot(df["timestamp"], df["temperature_smooth"], linewidth=2, label="Smoothed")

plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.title("NPU Temperature vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("temperature_vs_time.png", dpi=300)
plt.show()