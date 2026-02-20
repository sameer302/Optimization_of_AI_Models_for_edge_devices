# -------------------------------------------------------
# Import required libraries
# -------------------------------------------------------

from picamera2 import Picamera2   # Interface to Raspberry Pi camera (libcamera backend)
import cv2                        # OpenCV for display, saving images and video
import time                       # Used to generate unique filenames


# -------------------------------------------------------
# Initialize Picamera2 object
# -------------------------------------------------------

picam = Picamera2()  
# Creates a camera control object (does NOT start camera yet)


# -------------------------------------------------------
# Create video configuration
# -------------------------------------------------------
# main:
#   size   → Output resolution (width, height)
# Available sensor modes (for reference only)
# 0: (640, 480)
# 1: (1296, 972)
# 2: (1920, 1080)
# 3: (2592, 1944)
#   format → Pixel format (XRGB8888 = 4-channel: B,G,R,unused)
# -------------------------------------------------------

config = picam.create_video_configuration(
    main={"size": (2592, 1944), "format": "XRGB8888"}
)

picam.configure(config)  
# Applies the configuration to the camera pipeline

picam.start()  
# Starts the camera stream (sensor begins delivering frames)


# -------------------------------------------------------
# Create OpenCV display window
# -------------------------------------------------------
# WINDOW_NORMAL → Allows window resizing manually
# -------------------------------------------------------

window_name = "Live Camera"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)


# -------------------------------------------------------
# VIDEO MODE VARIABLES
# Comment this entire section if using photo-only mode
# -------------------------------------------------------

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
# Defines video codec (MP4 format)

video_filename = f"video_{int(time.time())}.mp4"  
# Unique filename using current timestamp

video_writer = cv2.VideoWriter(
    video_filename,
    fourcc,
    15,              # Frames per second to be displayed during playback not capture rate
    (2592, 1944)     # Must match frame resolution
)

# -------------------------------------------------------
# Main display loop
# -------------------------------------------------------
# Continuously:
#   1. Capture frame
#   2. Convert format
#   3. Display frame
#   4. Check keyboard input
# -------------------------------------------------------

while True:

    # Capture current frame from camera (BGRA format)
    frame = picam.capture_array()

    # Convert BGRA → BGR (OpenCV standard 3-channel format)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # If window is manually closed → exit safely
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break
    # Display current frame
    cv2.imshow(window_name, frame)

    # Required for:
    #   - Window refresh
    #   - Capturing key presses
    key = cv2.waitKey(1) & 0xFF


    # ---------------------------------------------------
    # PHOTO MODE
    # Press 'p' to capture image
    # Comment this section if using video-only mode
    # ---------------------------------------------------

    if key == ord('p'):
        photo_filename = f"photo_{int(time.time())}.jpg"
        cv2.imwrite(photo_filename, frame)
        print(f"Saved: {photo_filename}")


    # ---------------------------------------------------
    # VIDEO MODE
    # Comment this line if using photo-only mode
    # ---------------------------------------------------

    video_writer.write(frame)
    # Writes each frame to video file


    # ---------------------------------------------------
    # Quit condition
    # Press 'q' to exit program
    # ---------------------------------------------------

    if key == ord('q'):
        break
 

# -------------------------------------------------------
# Cleanup Section
# -------------------------------------------------------

video_writer.release()  
# Finalizes and properly closes video file

picam.stop()  
# Stops camera stream

cv2.destroyAllWindows()  
# Closes all OpenCV windows