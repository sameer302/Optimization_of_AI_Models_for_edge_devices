from picamera2 import Picamera2
import time

picam = Picamera2()

# ---------------------------------------
# Step 1: Print available sensor modes
# ---------------------------------------
print("\nAvailable Sensor Modes:\n")

sensor_modes = picam.sensor_modes

for i, mode in enumerate(sensor_modes):
    print(f"{i}: Resolution = {mode['size']} | Max FPS ≈ {mode.get('fps', 'N/A')}")

# ---------------------------------------
# Step 2: Choose mode index manually
# ---------------------------------------
selected_mode_index = 3   # <-- CHANGE THIS NUMBER

selected_mode = sensor_modes[selected_mode_index]
selected_size = selected_mode["size"]

print(f"\nSelected Mode: {selected_size}")

# ---------------------------------------
# Step 3: Configure camera with that mode
# ---------------------------------------
config = picam.create_video_configuration(
    main={"size": selected_size, "format": "XRGB8888"}, 
    controls={
        "AeEnable": False,
        "FrameDurationLimits": (1000, 10000000),  # 10 ms = 100 FPS
    }
)

picam.configure(config)
picam.start()

time.sleep(2)

picam.capture_array()
metadata = picam.capture_metadata()

print("\n--- Current Runtime Values (Metadata) ---")
print("ExposureTime (µs):", metadata.get("ExposureTime"))
print("FrameDuration (µs):", metadata.get("FrameDuration"))

print("\n--- Supported Control Ranges (min, max, default) ---")
controls = picam.camera_controls

print("AeEnable:", controls.get("AeEnable"))
print("ExposureTime:", controls.get("ExposureTime"))
print("FrameDurationLimits:", controls.get("FrameDurationLimits"))

picam.stop()