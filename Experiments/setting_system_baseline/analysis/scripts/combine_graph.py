import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Folder containing CSVs
csv_files = glob.glob("/home/sameer/Desktop/optimization_of_ai_models/Experiments/setting_system_baseline/analysis/fps_readings/*.csv")

plt.figure()

for file in csv_files:
    df = pd.read_csv(file)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Create relative time (seconds from start)
    df['time_sec'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

    # Smooth FPS (choose one)

    # Option 1: Rolling average
    df['fps_smooth'] = df['fps'].rolling(window=5, min_periods=1).mean()

    # Option 2: Exponential smoothing (uncomment if preferred)
    # df['fps_smooth'] = df['fps'].ewm(span=10).mean()

    # Plot
    plt.plot(df['time_sec'], df['fps_smooth'], label=os.path.basename(file))

plt.xlabel("Time (seconds)")
plt.ylabel("FPS")
plt.title("Smoothed FPS vs Time (All Runs)")
plt.legend()
plt.grid()

# Save figure
plt.savefig("/home/sameer/Desktop/optimization_of_ai_models/Experiments/setting_system_baseline/analysis/plots/fps_comparison.png", dpi=300, bbox_inches='tight')

plt.show()