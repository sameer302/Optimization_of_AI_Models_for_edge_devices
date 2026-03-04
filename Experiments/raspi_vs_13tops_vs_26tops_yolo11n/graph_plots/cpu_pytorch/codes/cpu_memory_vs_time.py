import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_more_objects_results/yolo11n_system_metrics_cpu_pt_1.csv"

df = pd.read_csv(csv_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Rolling smoothing window
window = 20

df["cpu_smooth"] = df["cpu_percent"].rolling(window).mean()
df["mem_smooth"] = df["memory_percent"].rolling(window).mean()

# ---------- CPU Plot ----------
plt.figure(figsize=(10,5))

plt.plot(df["timestamp"], df["cpu_percent"], alpha=0.3, label="Raw CPU %")
plt.plot(df["timestamp"], df["cpu_smooth"], linewidth=2, label="Smoothed CPU %")

plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.title("CPU Usage vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("cpu_percent_vs_time_clean.png", dpi=300)
plt.close()


# ---------- Memory Plot ----------
plt.figure(figsize=(10,5))

plt.plot(df["timestamp"], df["memory_percent"], alpha=0.3, label="Raw Memory %")
plt.plot(df["timestamp"], df["mem_smooth"], linewidth=2, label="Smoothed Memory %")

plt.xlabel("Time")
plt.ylabel("Memory Usage (%)")
plt.title("Memory Usage vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("memory_percent_vs_time_clean.png", dpi=300)
plt.close()

print("CPU and Memory plots saved.")