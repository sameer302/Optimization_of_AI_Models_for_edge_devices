import os
import re
import pandas as pd
import matplotlib.pyplot as plt

folder_path = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/hailo_benchmark_fps/csv_files_fps_monitoring/gen2_performance_mode_results"

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
plt.figure()
plt.plot(batch_sizes, fps_values, marker='o')
plt.xlabel("Batch Size")
plt.ylabel("FPS (hw_only_fps)")
plt.title("Gen2 Performance Mode FPS")
plt.grid()
plt.savefig("gen2_performance_mode_fps.png")
plt.show()