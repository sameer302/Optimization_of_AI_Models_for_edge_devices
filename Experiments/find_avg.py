import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns  # Removed to avoid potential issues

# Static configuration: Add your CSV files and their columns here
csv_files = [
    "/home/sameer/Desktop/optimization_of_ai_models/Experiments/tops_calculation/npu_usage_csv_logs/hailo8_benchmark_5min_performance_bs1.csv",  # Replace with actual path
    "/home/sameer/Desktop/optimization_of_ai_models/Experiments/tops_calculation/npu_usage_csv_logs/hailo8_benchmark_5min_ultra_performance_bs1.csv"  # Add more as needed
]

columns = [
    ["hailo_temp_C"],  # Columns for first CSV
    ["hailo_temp_C"]  # Columns for second CSV
]

# Custom labels for the box plots (must match the number of groups)
labels = [
    "Performance",  # Label for first group
    "Ultra Performance"  # Label for second group
]

# Ensure columns list matches csv_files length
if len(columns) != len(csv_files):
    print("Error: Number of column lists must match number of CSV files.")
    exit()

# Read data
data = {}
for csv, cols in zip(csv_files, columns):
    df = pd.read_csv(csv)
    for col in cols:
        if col in df.columns:
            data[f"{csv.split('/')[-1]}_{col}"] = df[col].dropna()  # Use filename for label, drop NaN
        else:
            print(f"Warning: Column '{col}' not found in {csv}. Skipping.")

# Prepare data for plotting
if not data:
    print("No valid data to plot.")
    exit()

long_df = pd.DataFrame()
for key, series in data.items():
    temp = pd.DataFrame({'value': series, 'group': key})
    long_df = pd.concat([long_df, temp], ignore_index=True)

# Check labels length
groups = long_df['group'].unique()
if len(labels) != len(groups):
    print(f"Error: Number of labels ({len(labels)}) must match number of groups ({len(groups)}).")
    exit()

# Create comparative box plot
plt.figure(figsize=(10, 6))
groups = long_df['group'].unique()
data_to_plot = [long_df[long_df['group'] == g]['value'].values for g in groups]
bp = plt.boxplot(data_to_plot, tick_labels=labels, patch_artist=True, boxprops=dict(facecolor='lightblue', color='blue'), medianprops=dict(color='red', linewidth=2))
plt.title('Temperature variation for Batch size 1')
plt.ylabel('Temperature (°C)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Annotate medians
medians = [item.get_ydata()[0] for item in bp['medians']]
for i, median in enumerate(medians):
    plt.text(i+1 + 0.1, median, f'{median:.2f}', ha='left', va='center', fontsize=10, color='red')

plt.tight_layout()
plt.savefig('/home/sameer/Desktop/optimization_of_ai_models/Experiments/tops_calculation/comparative_boxplot.png')
print("Box plot saved as 'comparative_boxplot.png'")