#!/bin/bash

DURATION=1800
OUTPUT_DIR="./cpu_results/all_zero_all"

cleanup() {
    echo "Stopping experiment..."
    pkill -P $$ 
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- Start inference ---
timeout $DURATION python /home/sameer/Desktop/optimization_of_ai_models/ejtech_ultralytics/yolo_detect.py \
  --csv "$OUTPUT_DIR/yolo11n_fps_cpu_pt.csv" \
  --capture_resolution 640x480 \
  --source=picamera0 \
  --model /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo11/yolo11n.pt &

INFER_PID=$!
YOLO_PID=$(pgrep -P "$INFER_PID")
echo "yolo_detect.py PID: $YOLO_PID"

# Logger uses --pid $YOLO_PID (or $INFER_PID if you prefer)
timeout $DURATION python ../system_metrics_logger.py \
  --cpu --temp --memory --freq --voltage --throttle \
  --threads --running-threads --pid $YOLO_PID \
  --out "$OUTPUT_DIR/yolo11n_system_metrics_cpu_pt.csv" &


wait
echo "Experiment completed. Results are saved in $OUTPUT_DIR"