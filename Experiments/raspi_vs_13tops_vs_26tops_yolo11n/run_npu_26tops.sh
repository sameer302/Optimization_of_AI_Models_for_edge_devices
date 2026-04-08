#!/bin/bash

DURATION=1800
OUTPUT_DIR="/home/sameer/Desktop/optimization_of_ai_models/Experiments/raspi_vs_13tops_vs_26tops_yolo11n/fps_and_system_metrics_csv_logs"

cleanup() {
    echo "Stopping experiment..."
    pkill -P $$        # Kill all child processes
    exit 0
}

# Catch Ctrl+C and kill
trap cleanup SIGINT SIGTERM

timeout $DURATION python ../system_metrics_logger.py \
  --cpu --temp --freq --voltage --memory --throttle --npu --hailo-temp --hailo-clock --out "$OUTPUT_DIR/yolo11n_system_metrics_26tops.csv" &

timeout $DURATION env HAILO_MONITOR=1 python /home/sameer/Desktop/optimization_of_ai_models/hailo-apps/hailo_apps/python/pipeline_apps/detection_simple/detection_simple1.py \
  --csv-path "$OUTPUT_DIR/yolo11n_fps_26tops1.csv" \
  --input rpi \
  --width 640 \
  --height 480 \
  --batch-size 1 \
  --hef-path /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo11/yolov11n_hailo8.hef &

wait
echo "Experiment completed. Results are saved in $OUTPUT_DIR"