import os
import csv
import matplotlib.pyplot as plt
import re

# Directory containing the CSV files
directory = 'performance_mode_results'

# List to hold batch sizes and hw_only_fps values
batch_sizes = []
hw_only_fps_values = []

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
                break  # Assuming only one row
        
        batch_sizes.append(batch_size)
        hw_only_fps_values.append(hw_only_fps)

# Sort by batch size
sorted_indices = sorted(range(len(batch_sizes)), key=lambda i: batch_sizes[i])
batch_sizes = [batch_sizes[i] for i in sorted_indices]
hw_only_fps_values = [hw_only_fps_values[i] for i in sorted_indices]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(batch_sizes, hw_only_fps_values, marker='o')
plt.title('Batch Size vs HW Only FPS')
plt.xlabel('Batch Size')
plt.ylabel('HW Only FPS')
plt.grid(True)
plt.savefig('batch_size_vs_hw_only_fps.png')
plt.close()