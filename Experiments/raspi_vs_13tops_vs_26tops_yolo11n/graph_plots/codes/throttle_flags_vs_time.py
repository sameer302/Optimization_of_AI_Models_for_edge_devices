import pandas as pd
import matplotlib.pyplot as plt

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/fps_and_system_metrics_csv_logs/yolo11n_system_metrics_26tops.csv"

df = pd.read_csv(csv_file)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# convert hex flag to integer
df["throttle_flag_int"] = df["throttled_flags_hex"].apply(lambda x: int(x, 16))

# 0 = no throttling, 1 = throttling event
df["throttle_active"] = df["throttle_flag_int"].apply(lambda x: 1 if x != 0 else 0)

plt.figure(figsize=(10,4))

plt.step(df["timestamp"], df["throttle_active"], where="post")

plt.yticks([0,1], ["No throttling", "Throttling"])
plt.xlabel("Time")
plt.ylabel("Throttle Status")
plt.title("Throttle Status vs Time")

plt.grid(True, linestyle="--", alpha=0.5)
plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig("throttle_status_vs_time.png", dpi=300)
plt.close()

print("Throttle status plot saved.")