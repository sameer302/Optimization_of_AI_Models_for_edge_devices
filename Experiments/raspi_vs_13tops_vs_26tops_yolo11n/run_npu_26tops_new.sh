#!/bin/bash
# run_experiment.sh
# Runs run_detection_app.py with default parameters.
# Override any value by passing args directly:
#   ./run_experiment.sh --duration 600 --output-dir ./my_run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python "$SCRIPT_DIR/run_detection_app.py" \
  --duration 1800 \
  --output-dir ./results \
  --input rpi \
  --hef-path /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo/yolov11n_hailo8.hef \
  "$@"