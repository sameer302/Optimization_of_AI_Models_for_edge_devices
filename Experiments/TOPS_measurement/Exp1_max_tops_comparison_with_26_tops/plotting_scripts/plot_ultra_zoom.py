from Experiments.TOPS_measurement.Exp1_max_tops_comparison_with_26_tops.plotting_scripts.plot_utils import plot_batch_vs_single_metric, read_batch_metrics

folder = 'ultra_performance_mode_results'
filename_pattern = r'Inference_performance_1min_bs(\d+)\.csv'

batch_sizes, hw_only_fps, _ = read_batch_metrics(
    folder,
    filename_pattern,
    primary_field='hw_only_fps',
    secondary_field=None,
)

filtered_pairs = [(bs, fps) for bs, fps in zip(batch_sizes, hw_only_fps) if 41 <= bs <= 63]
if not filtered_pairs:
    raise RuntimeError('No matching batch sizes found in range 41-63.')

filtered_batch_sizes, filtered_hw_only_fps = zip(*filtered_pairs)

plot_batch_vs_single_metric(
    list(filtered_batch_sizes),
    list(filtered_hw_only_fps),
    title='Ultra Inference: Batch Size 41-63 vs HW Only FPS',
    ylabel='HW Only FPS',
    output_filename='ultra_batch_size_41_63_vs_hw_only_fps.png',
)
