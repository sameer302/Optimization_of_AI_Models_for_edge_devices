from picamera2 import Picamera2
import time

# -------------------------------------------------------
# Initialize camera
# -------------------------------------------------------
picam = Picamera2()

# -------------------------------------------------------
# Available sensor modes (for reference only)
# 0: (640, 480)
# 1: (1296, 972)
# 2: (1920, 1080)
# 3: (2592, 1944)
# -------------------------------------------------------

# -------------------------------------------------------
# Step 1: Hardcode resolution to 640 x 480
# -------------------------------------------------------
selected_size = (640, 480)

print(f"\nUsing Resolution: {selected_size}")

# -------------------------------------------------------
# Step 2: Create configuration
# - main: sets resolution and pixel format
# - controls:
#       AeEnable = False → disable auto exposure
#       FrameDurationLimits → allow wide manual range
# -------------------------------------------------------
config = picam.create_video_configuration(
    main={"size": selected_size, "format": "XRGB8888"},
    controls={
        "AeEnable": False,
        "FrameDurationLimits": (1000, 10000000),
    }
)

# -------------------------------------------------------
# Step 3: Apply configuration and start camera
# -------------------------------------------------------
picam.configure(config)
picam.start()

# Give sensor time to stabilize
time.sleep(2)

# -------------------------------------------------------
# Step 4: Capture one frame to retrieve metadata
# -------------------------------------------------------
picam.capture_array()
metadata = picam.capture_metadata()

# -------------------------------------------------------
# Step 5: Print current runtime values
# -------------------------------------------------------
print("\n--- Current Runtime Values (Metadata) ---")
print("ExposureTime (µs):", metadata.get("ExposureTime"))
print("FrameDuration (µs):", metadata.get("FrameDuration"))

# -------------------------------------------------------
# Step 6: Print supported control ranges
# These show (min, max, default) values
# -------------------------------------------------------
print("\n--- Supported Control Ranges (min, max, default) ---")

controls = picam.camera_controls

print("AeEnable:", controls.get("AeEnable"))
print("ExposureTime:", controls.get("ExposureTime"))
print("FrameDurationLimits:", controls.get("FrameDurationLimits"))

# -------------------------------------------------------
# Step 7: Stop camera
# -------------------------------------------------------
picam.stop()