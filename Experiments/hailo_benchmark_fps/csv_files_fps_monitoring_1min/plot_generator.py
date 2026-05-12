import os
import re
import pandas as pd
import matplotlib.pyplot as plt

folder_path = "/workspaces/Optimization_of_AI_Models_for_edge_devices/Experiments/hailo_benchmark_fps/csv_files_fps_monitoring_1min/gen3_ultra_performance_mode_results"

batch_sizes = []
fps_values = []

for file in os.listdir(folder_path):
    # Only process required files
    if file.startswith("Inference_performance_1min_bs") and file.endswith(".csv"):
        
        # Extract batch size
        match = re.search(r'bs(\d+)', file)
        if not match:
            continue
        bs = int(match.group(1))
        
        # Only include batch sizes from 41 to 63
        if bs < 41 or bs > 63:
            continue

        file_path = os.path.join(folder_path, file)

        # Read CSV
        df = pd.read_csv(file_path)

        # Extract hw_only_fps (first row)
        fps = df.loc[0, "hw_only_fps"]

        batch_sizes.append(bs)
        fps_values.append(fps)

# Sort by batch size
batch_sizes, fps_values = zip(*sorted(zip(batch_sizes, fps_values)))

# Plot
plt.figure(figsize=(10, 6))
plt.plot(batch_sizes, fps_values, marker='o', color='tab:blue', linewidth=2, markersize=6)
plt.xlabel("Batch Size")
plt.ylabel("FPS (hw_only_fps)")
plt.title("Gen3 Ultra Performance Mode: FPS vs Batch Size (41-63)")

# Adjust y-axis scale for better visualization of small range
fps_min, fps_max = min(fps_values), max(fps_values)
fps_range = fps_max - fps_min
plt.ylim(fps_min - 0.1 * fps_range, fps_max + 0.1 * fps_range)

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("gen3_ultra_performance_mode_fps_bs41_63.png")
plt.show()