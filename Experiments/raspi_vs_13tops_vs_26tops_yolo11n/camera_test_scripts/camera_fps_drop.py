from picamera2 import Picamera2
import cv2
import time
import argparse

# -----------------------------
# Argument Parsing
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--width", type=int, required=True)
parser.add_argument("--height", type=int, required=True)
parser.add_argument("--seconds", type=int, default=10)
parser.add_argument("--output", type=str, default="demo.avi")
args = parser.parse_args()

resW = args.width
resH = args.height
duration = args.seconds
output_name = args.output

print(f"\nResolution: {resW}x{resH}")
print(f"Duration: {duration}s")

# -----------------------------
# Camera Setup
# -----------------------------
picam = Picamera2()

config = picam.create_video_configuration(
    main={"size": (resW, resH), "format": "XRGB8888"}
)

# Update 1: Added FrameDurationLimits to controls
# config = picam.create_video_configuration(
#     main={"size": (resW, resH), "format": "XRGB8888"},
#     controls={
#         "AeEnable": False,
#         "FrameDurationLimits": (1000, 10000000), 
#     }
# )

picam.configure(config)
picam.start()
time.sleep(2)

results = {}

# ---------------------------------
# 1️⃣ SENSOR-LEVEL FPS
# ---------------------------------
picam.capture_array()
metadata = picam.capture_metadata()
frame_duration = metadata.get("FrameDuration")

if frame_duration:
    sensor_fps = 1_000_000 / frame_duration
    results["Sensor"] = sensor_fps
else:
    results["Sensor"] = 0

# ---------------------------------
# 2️⃣ CAPTURE-ONLY
# ---------------------------------
start = time.time()
frames = 0
while time.time() - start < duration:
    frame = picam.capture_array()
    frames += 1

elapsed = time.time() - start
results["Capture"] = frames / elapsed

# ---------------------------------
# 3️⃣ CAPTURE + RECORD
# ---------------------------------
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
writer = cv2.VideoWriter(output_name, fourcc, 30, (resW, resH))

start = time.time()
frames = 0
while time.time() - start < duration:
    frame = picam.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    writer.write(frame_bgr)
    frames += 1

elapsed = time.time() - start
writer.release()
results["Capture + Record"] = frames / elapsed

# ---------------------------------
# 4️⃣ CAPTURE + DISPLAY
# ---------------------------------
start = time.time()
frames = 0
while time.time() - start < duration:
    frame = picam.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    cv2.imshow("Live Feed", frame_bgr)
    frames += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

elapsed = time.time() - start
cv2.destroyAllWindows()
results["Capture + Display"] = frames / elapsed

# ---------------------------------
# 5️⃣ CAPTURE + DISPLAY + RECORD
# ---------------------------------
writer = cv2.VideoWriter("display_" + output_name, fourcc, 30, (resW, resH))

start = time.time()
frames = 0
while time.time() - start < duration:
    frame = picam.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    cv2.imshow("Live Feed", frame_bgr)
    writer.write(frame_bgr)
    frames += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

elapsed = time.time() - start
writer.release()
cv2.destroyAllWindows()
results["Capture + Display + Record"] = frames / elapsed

picam.stop()

# -----------------------------
# Final Results
# -----------------------------
print("\n========== FPS COMPARISON ==========")
for stage, fps in results.items():
    print(f"{stage:<30}: {fps:.2f} FPS")

print("Done.")