#!/bin/bash

DURATION=1800  # Duration of the experiment in seconds (30 minutes)
OUTPUT_DIR="./results"

cleanup() {
    echo "Stopping experiment..."
    pkill -P $$        # Kill all child processes
    exit 0
}

trap cleanup SIGINT SIGTERM

timeout $DURATION python ../system_metrics_logger.py \
  --cpu --temp --memory --freq --voltage --throttle --out "$OUTPUT_DIR/yolo11n_system_metrics_cpu_ncnn.csv" &

timeout $DURATION python ./yolo11n_cpu.py \
  --csv "$OUTPUT_DIR/yolo11n_fps_cpu_ncnn.csv" --resolution=640x480 --source=picamera0  --model /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo/yolo11n_ncnn_model &

wait
echo "Experiment completed. Results are saved in $OUTPUT_DIR"