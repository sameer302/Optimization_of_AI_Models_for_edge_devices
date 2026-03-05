import pandas as pd

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/yolo11n_camera_results/yolo11n_fps_26tops.csv"  # replace with your actual path

df = pd.read_csv(csv_file)

average_fps = df["fps"].mean()

print(f"Average FPS: {average_fps:.3f}")