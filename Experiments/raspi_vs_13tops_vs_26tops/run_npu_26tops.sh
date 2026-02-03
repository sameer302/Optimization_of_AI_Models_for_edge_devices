#!/bin/bash

DURATION=1800  # Duration of the experiment in seconds (30 minutes)
OUTPUT_DIR="./results"

timeout $DURATION python ../system_metrics_logger.py \
  --cpu --temp --npu --memory --out "$OUTPUT_DIR/yolo11n_system_metrics_26tops.csv" &

timeout $DURATION env HAILO_MONITOR=1 python ./yolo11n_npu.py \
  --csv "$OUTPUT_DIR/yolo11n_fps_26tops.csv" --input rpi --hef-path /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo/yolov11n_hailo8.hef &

wait
echo "Experiment completed. Results are saved in $OUTPUT_DIR"