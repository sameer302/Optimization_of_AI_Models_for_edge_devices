import os
from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import hailo
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection_simple.detection_pipeline_simple import GStreamerDetectionApp
import csv
import time
from datetime import datetime

# User-defined class to be used in the callback function: Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        # Write CSV to script directory, not current working directory
        csv_path = Path(__file__).resolve().parent / "npu_fps_log.csv"
        self.csv = open(csv_path, "w", newline="")
        self.writer = csv.writer(self.csv)
        self.writer.writerow(["timestamp", "frame_count", "fps"])
        self.csv.flush()  # Flush header to disk immediately
        try:
            os.fsync(self.csv.fileno())  # Force write to disk
        except Exception:
            pass

    def log_fps(self, buffer=None):
        now_ts = time.time()
        now = datetime.now().isoformat()
        elapsed = now_ts - self.start_time
        fps = round(self.get_count() / elapsed if elapsed > 0 else 0.0, 2)

        self.writer.writerow([now, self.get_count(), fps])
        self.csv.flush()  # Flush each row to disk
        try:
            os.fsync(self.csv.fileno())  # Force write to disk
        except Exception:
            pass

    def close(self):
        self.csv.close()

# User-defined callback function: This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    buffer = info.get_buffer()  # Get the GstBuffer from the probe info
    if buffer is None:  # Check if the buffer is valid
        return Gst.PadProbeReturn.OK

    user_data.increment()  # Using the user_data to count the number of frames

    # ---- ADD THIS BLOCK ----
    if user_data.get_count() % 30 == 0:   # log every 30 frames
        user_data.log_fps()
    # -----------------------

    string_to_print = f"Frame count: {user_data.get_count()}\n"
    for detection in hailo.get_roi_from_buffer(buffer).get_objects_typed(hailo.HAILO_DETECTION):  # Get the detections from the buffer & Parse the detections
        string_to_print += (f"Detection: {detection.get_label()} Confidence: {detection.get_confidence():.2f}\n")
    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    env_file     = project_root / ".env"
    env_path_str = str(env_file)
    os.environ["HAILO_ENV_FILE"] = env_path_str
    user_data = user_app_callback_class()  # Create an instance of the user app callback class
    app = GStreamerDetectionApp(app_callback, user_data)
    try:
        app.run()
    finally:
        user_data.close()

