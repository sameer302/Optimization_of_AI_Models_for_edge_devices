import pandas as pd

csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/setting_system_baseline/cpu_results/five_zero_all/yolo11n_fps_cpu_pt.csv"  # replace with your actual path

df = pd.read_csv(csv_file)

average_fps = df["latency_ms"].mean()

print(f"Average:{average_fps:.3f}")