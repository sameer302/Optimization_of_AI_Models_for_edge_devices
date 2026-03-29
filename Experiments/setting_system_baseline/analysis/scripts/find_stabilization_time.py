import pandas as pd
import numpy as np

def find_stabilization_time(
    csv_path,
    column_name,
    timestamp_col="timestamp",
    window_seconds=180,
    mean_thresh=0.02,
    std_thresh=0.05,
    consecutive_windows=3
):
    df = pd.read_csv(csv_path)

    # Parse timestamp
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.sort_values(by=timestamp_col)

    start_time = df[timestamp_col].iloc[0]

    df.set_index(timestamp_col, inplace=True)
    series = df[column_name].dropna()

    rolling_mean = series.rolling(f"{window_seconds}s").mean()
    rolling_std = series.rolling(f"{window_seconds}s").std()

    stable_count = 0

    for i in range(1, len(series)):
        if pd.isna(rolling_mean.iloc[i]) or pd.isna(rolling_mean.iloc[i-1]):
            continue

        mu_t = rolling_mean.iloc[i]
        mu_prev = rolling_mean.iloc[i-1]
        sigma_t = rolling_std.iloc[i]

        mean_change = abs(mu_t - mu_prev) / (mu_t + 1e-8)
        std_ratio = sigma_t / (mu_t + 1e-8)

        if mean_change < mean_thresh and std_ratio < std_thresh:
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= consecutive_windows:
            stabilization_time = series.index[i]
            duration = stabilization_time - start_time

            return {
                "stabilization_timestamp": stabilization_time,
                "duration_seconds": duration.total_seconds(),
                "duration_minutes": duration.total_seconds() / 60
            }

    return None

if __name__ == "__main__":
    csv_file = "/home/sameer/Desktop/optimization_of_ai_models/Experiments/setting_system_baseline/cpu_results/7_zero_all/yolo11n_system_metrics_cpu_pt.csv"  # replace with your actual path
    result = find_stabilization_time(csv_file, "latency_ms")

    if result:
        print(f"Stabilization Timestamp: {result['stabilization_timestamp']}")
        print(f"Duration until Stabilization: {result['duration_seconds']} seconds ({result['duration_minutes']} minutes)")
    else:
        print("No stabilization point found within the data.")