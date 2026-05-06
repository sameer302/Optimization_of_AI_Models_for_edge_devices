#!/bin/bash

OUTPUT_DIR="/home/sameer/Desktop/optimization_of_ai_models/Experiments/hailo_benchmark_fps/csv_files_temp_monitoring_bs40_3hrs/gen3_ultra_performance_mode"
HEF_PATH="/home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo11/yolov11n_hailo8.hef"
SYS_LOGGER_PATH="/home/sameer/Desktop/optimization_of_ai_models/Experiments/system_metrics_logger.py"


BATCH=40 # Add more batch sizes as needed

cleanup() {
    echo "Stopping experiment..."
    kill -TERM $pid1 $pid2 2>/dev/null # sends SIGTERM (soft kill) to the processes and asks them to stop cleanly by saving files and closing resources
    sleep 1 # gives the processes a moment to exit gracefully
    kill -KILL $pid1 $pid2 2>/dev/null # sends SIGKILL (force kill) to the processes if they are still running, ensuring they are terminated
    pkill -9 -f "hailo benchmark" 2>/dev/null # force kill any remaining benchmark processes
    pkill -9 -f "system_metrics_logger" 2>/dev/null # force kill any remaining logger processes
    exit 0
}

# Catch Ctrl+C and kill
trap cleanup SIGINT SIGTERM # This sets up a trap to catch SIGINT (Ctrl+C) and SIGTERM (system termination) signals, ensuring that the cleanup function is called to stop the experiment gracefully when the user interrupts it.

echo "Running benchmark with batch size: $BATCH"

python $SYS_LOGGER_PATH \
--npu --hailo-temp --hailo-clock --out "$OUTPUT_DIR/NPU_performance_3hrs_bs${BATCH}.csv" & pid1=$!

env HAILO_MONITOR=1 hailo benchmark "$HEF_PATH" \
    --time-to-run 10800 \
    --batch-size $BATCH \
    --power-mode ultra_performance \
    --csv "$OUTPUT_DIR/Inference_performance_3hrs_bs${BATCH}.csv" & pid2=$!

# Wait for the benchmark to finish
wait $pid2

# Kill the logger after benchmark completes
kill $pid1 2>/dev/null
echo "completed batch size: $BATCH"

echo "Experiment completed for ultra_performance mode. Results are saved in $OUTPUT_DIR"
