import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def parse_list(arg):
    return arg.split(",")

def format_mmss(x, pos):
    m = int(x // 60)
    s = int(x % 60)
    return f"{m:02d}:{s:02d}"

parser = argparse.ArgumentParser()

parser.add_argument("--x_csvs", required=True, type=parse_list)
parser.add_argument("--x_cols", required=True, type=parse_list)

parser.add_argument("--y_csvs", required=True, type=parse_list)
parser.add_argument("--y_cols", required=True, type=parse_list)

parser.add_argument("--labels", required=True, type=parse_list)

parser.add_argument("--xlabel", required=True)
parser.add_argument("--ylabel", required=True)
parser.add_argument("--title", default="")

args = parser.parse_args()

n = len(args.labels)

if not (len(args.x_csvs) == len(args.x_cols) ==
        len(args.y_csvs) == len(args.y_cols) == n):
    raise ValueError("All input lists must have same length")

plt.figure(figsize=(8, 5))

is_time_axis = False

for i in range(n):

    x_df = pd.read_csv(args.x_csvs[i])
    y_df = pd.read_csv(args.y_csvs[i])

    col_name = args.x_cols[i]

    # ---------- X handling ----------
    if "time" in col_name.lower():
        time_data = pd.to_datetime(x_df[col_name])

        # Relative time alignment
        t0 = time_data.iloc[0]
        x = (time_data - t0).dt.total_seconds()

        is_time_axis = True
    else:
        x = x_df[col_name]

    # ---------- Y handling ----------
    y = y_df[args.y_cols[i]]

    # Length safety
    min_len = min(len(x), len(y))
    plt.plot(x[:min_len], y[:min_len], label=args.labels[i])

# ---------- Axis formatting ----------
plt.xlabel(args.xlabel)

if is_time_axis:
    ax = plt.gca()

    ax.xaxis.set_major_locator(ticker.MultipleLocator(300))  # 5 minutes = 300 seconds
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_mmss))

    plt.xticks(rotation=45)

plt.ylabel(args.ylabel)
plt.title(args.title)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
