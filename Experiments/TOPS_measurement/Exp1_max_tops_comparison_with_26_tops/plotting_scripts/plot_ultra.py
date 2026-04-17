from Experiments.TOPS_measurement.Exp1_max_tops_comparison_with_26_tops.plotting_scripts.plot_utils import plot_batch_vs_single_metric, plot_batch_vs_two_metrics, read_batch_metrics

folder = 'ultra_performance_mode_results'
filename_pattern = r'Inference_performance_1min_bs(\d+)\.csv'

batch_sizes, hw_only_fps, hw_latency = read_batch_metrics(
    folder,
    filename_pattern,
    primary_field='hw_only_fps',
    secondary_field='hw_latency',
)

if not batch_sizes:
    raise RuntimeError('No matching CSV files found in the ultra_performance_mode_results folder.')

plot_batch_vs_two_metrics(
    batch_sizes,
    hw_only_fps,
    hw_latency,
    primary_label='HW Only FPS',
    secondary_label='HW Latency (ms)',
    title='Ultra Inference: Batch Size vs HW Only FPS and HW Latency',
    output_filename='ultra_batch_size_vs_hw_only_fps_and_latency.png',
)
