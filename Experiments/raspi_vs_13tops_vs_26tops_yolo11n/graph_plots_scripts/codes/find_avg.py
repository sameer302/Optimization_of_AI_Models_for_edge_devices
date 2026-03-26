import pandas as pd

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/fps_and_system_metrics_csv_logs/yolo11n_fps_26tops.csv"  # replace with your actual path

df = pd.read_csv(csv_file)

average_fps = df["fps"].mean()

print(f"Average FPS: {average_fps:.3f}")