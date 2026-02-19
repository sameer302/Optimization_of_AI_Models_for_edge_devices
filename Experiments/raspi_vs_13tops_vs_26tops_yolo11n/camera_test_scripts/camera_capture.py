from picamera2 import Picamera2
import cv2

# -------------------------------------------------------
# Initialize Picamera2 object
# -------------------------------------------------------
picam = Picamera2()

# -------------------------------------------------------
# Create video configuration
# - size: camera resolution
# - format: pixel format (XRGB8888 = 4-channel format)
# -------------------------------------------------------
config = picam.create_video_configuration(
    main={"size": (640, 480), "format": "XRGB8888"}
)

# Apply configuration to camera
picam.configure(config)

# Start camera stream
picam.start()

# -------------------------------------------------------
# Create OpenCV display window
# WINDOW_NORMAL allows manual resizing
# -------------------------------------------------------
window_name = "Live Camera"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Set initial window size (display size, not camera resolution)
cv2.resizeWindow(window_name, 1000, 700)

# -------------------------------------------------------
# Main display loop
# -------------------------------------------------------
while True:

    # Capture frame from Picamera (returns BGRA format)
    frame = picam.capture_array()

    # Convert BGRA → BGR (OpenCV standard format)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # ---------------------------------------------------
    # Check if window was manually closed
    # If closed, property becomes < 1 → exit loop
    # ---------------------------------------------------
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

    # Display current frame in window
    cv2.imshow(window_name, frame)

    # Required for OpenCV window to refresh
    # Also processes GUI events
    cv2.waitKey(1)

# -------------------------------------------------------
# Cleanup
# -------------------------------------------------------

# Stop camera stream
picam.stop()

# Destroy all OpenCV windows
cv2.destroyAllWindows()