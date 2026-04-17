import csv
import os
import re
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt


def read_batch_metrics(
    directory: str,
    filename_pattern: str,
    primary_field: str,
    secondary_field: Optional[str] = None,
) -> Tuple[List[int], List[float], Optional[List[float]]]:
    """Read batch size and metric values from CSV files in a directory."""
    pattern = re.compile(filename_pattern)
    batch_sizes: List[int] = []
    primary_values: List[float] = []
    secondary_values: Optional[List[float]] = [] if secondary_field else None

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if not match:
            continue

        batch_size = int(match.group(1))
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            row = next(reader, None)
            if row is None:
                continue

            primary_value = float(row[primary_field])
            batch_sizes.append(batch_size)
            primary_values.append(primary_value)

            if secondary_field:
                secondary_value = float(row[secondary_field]) if row.get(secondary_field) else None
                secondary_values.append(secondary_value)

    sorted_indices = sorted(range(len(batch_sizes)), key=lambda i: batch_sizes[i])
    batch_sizes = [batch_sizes[i] for i in sorted_indices]
    primary_values = [primary_values[i] for i in sorted_indices]
    if secondary_field and secondary_values is not None:
        secondary_values = [secondary_values[i] for i in sorted_indices]

    return batch_sizes, primary_values, secondary_values


def plot_batch_vs_two_metrics(
    batch_sizes: List[int],
    primary_values: List[float],
    secondary_values: List[float],
    primary_label: str,
    secondary_label: str,
    title: str,
    output_filename: str,
    primary_color: str = 'tab:blue',
    secondary_color: str = 'tab:red',
) -> None:
    """Create a plot with a primary y-axis and a secondary y-axis."""
    fig, ax_primary = plt.subplots(figsize=(10, 6))
    ax_secondary = ax_primary.twinx()

    ax_primary.plot(batch_sizes, primary_values, marker='o', color=primary_color, label=primary_label)
    ax_secondary.plot(batch_sizes, secondary_values, marker='s', color=secondary_color, label=secondary_label)

    ax_primary.set_xlabel('Batch Size')
    ax_primary.set_ylabel(primary_label, color=primary_color)
    ax_secondary.set_ylabel(secondary_label, color=secondary_color)
    ax_primary.tick_params(axis='y', labelcolor=primary_color)
    ax_secondary.tick_params(axis='y', labelcolor=secondary_color)
    ax_primary.grid(True)

    lines_primary, labels_primary = ax_primary.get_legend_handles_labels()
    lines_secondary, labels_secondary = ax_secondary.get_legend_handles_labels()
    ax_primary.legend(lines_primary + lines_secondary, labels_primary + labels_secondary, loc='best')

    plt.title(title)
    fig.tight_layout()
    plt.savefig(output_filename)
    plt.close(fig)


def plot_batch_vs_single_metric(
    batch_sizes: List[int],
    metric_values: List[float],
    title: str,
    ylabel: str,
    output_filename: str,
    y_range: Optional[Tuple[float, float]] = None,
) -> None:
    """Create a single-axis batch size plot."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(batch_sizes, metric_values, marker='o', color='tab:blue')
    ax.set_xlabel('Batch Size')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if y_range:
        ax.set_ylim(y_range)
    ax.set_xticks(batch_sizes)
    ax.grid(True)
    fig.tight_layout()
    plt.savefig(output_filename)
    plt.close(fig)
