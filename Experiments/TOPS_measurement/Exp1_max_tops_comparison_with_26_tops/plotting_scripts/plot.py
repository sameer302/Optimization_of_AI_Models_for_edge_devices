import os
import csv
import matplotlib.pyplot as plt
import re

# Directory containing the CSV files
directory = 'performance_mode_results'

# List to hold batch sizes, hw_only_fps, and latency values
batch_sizes = []
hw_only_fps_values = []
hw_latency_values = []

# Regex to extract batch size from filename
pattern = re.compile(r'yolo11n_benchmark_hailo8_1min_performance_bs(\d+)\.csv')

# Iterate over files in the directory
for filename in os.listdir(directory):
    match = pattern.match(filename)
    if match:
        batch_size = int(match.group(1))
        filepath = os.path.join(directory, filename)
        
        # Read the CSV file
        with open(filepath, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hw_only_fps = float(row['hw_only_fps'])
                hw_latency = float(row['hw_latency']) if row.get('hw_latency') else None
                break  # Assuming only one row
        
        batch_sizes.append(batch_size)
        hw_only_fps_values.append(hw_only_fps)
        hw_latency_values.append(hw_latency)

# Sort by batch size
sorted_indices = sorted(range(len(batch_sizes)), key=lambda i: batch_sizes[i])
batch_sizes = [batch_sizes[i] for i in sorted_indices]
hw_only_fps_values = [hw_only_fps_values[i] for i in sorted_indices]
hw_latency_values = [hw_latency_values[i] for i in sorted_indices]

# Plot FPS and latency with twin y-axis
fig, ax_fps = plt.subplots(figsize=(10, 6))
ax_latency = ax_fps.twinx()

ax_fps.plot(batch_sizes, hw_only_fps_values, marker='o', color='tab:blue', label='HW Only FPS')
ax_latency.plot(batch_sizes, hw_latency_values, marker='s', color='tab:red', label='HW Latency (ms)')

ax_fps.set_xlabel('Batch Size')
ax_fps.set_ylabel('HW Only FPS', color='tab:blue')
ax_latency.set_ylabel('HW Latency (ms)', color='tab:red')
ax_fps.tick_params(axis='y', labelcolor='tab:blue')
ax_latency.tick_params(axis='y', labelcolor='tab:red')
ax_fps.grid(True)

lines_fps, labels_fps = ax_fps.get_legend_handles_labels()
lines_latency, labels_latency = ax_latency.get_legend_handles_labels()
ax_fps.legend(lines_fps + lines_latency, labels_fps + labels_latency, loc='best')

plt.title('Batch Size vs HW Only FPS and HW Latency')
fig.tight_layout()
plt.savefig('batch_size_vs_hw_only_fps_and_latency.png')
plt.close()

# Plot zoom view for batch sizes 41-63 with FPS range 180-200
filtered_pairs = [(bs, fps) for bs, fps in zip(batch_sizes, hw_only_fps_values) if 41 <= bs <= 63]
if filtered_pairs:
    filtered_batch_sizes, filtered_hw_only_fps = zip(*filtered_pairs)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(filtered_batch_sizes, filtered_hw_only_fps, marker='o', color='tab:blue')
    ax2.set_xlabel('Batch Size')
    ax2.set_ylabel('HW Only FPS')
    ax2.set_title('Batch Size 41-63 vs HW Only FPS (180-200)')
    ax2.set_ylim(180, 200)
    ax2.set_xticks(filtered_batch_sizes)
    ax2.grid(True)
    fig2.tight_layout()
    plt.savefig('batch_size_41_63_vs_hw_only_fps_zoom.png')
    plt.close()