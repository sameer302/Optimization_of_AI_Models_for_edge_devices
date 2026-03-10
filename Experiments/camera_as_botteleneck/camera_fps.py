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
parser.add_argument("--mode", type=str, required=True,
                    choices=["sensor", "capture", "record", "display"])
parser.add_argument("--seconds", type=int, default=10)
parser.add_argument("--output", type=str, default="demo.avi")

args = parser.parse_args()

resW = args.width
resH = args.height
mode = args.mode
duration = args.seconds
output_name = args.output

# -----------------------------
# Camera Setup
# -----------------------------
picam = Picamera2()

config = picam.create_video_configuration(
    main={"size": (resW, resH), "format": "XRGB8888"}
)

picam.configure(config)
picam.start()
time.sleep(2)

print(f"\nResolution: {resW}x{resH}")
print(f"Mode: {mode}")

# ---------------------------------
# 1️⃣ SENSOR-LEVEL FPS
# ---------------------------------
if mode == "sensor":

    picam.capture_array()
    metadata = picam.capture_metadata()
    frame_duration = metadata.get("FrameDuration")

    if frame_duration:
        fps = 1_000_000 / frame_duration
        print(f"Sensor-level FPS: {fps:.2f}")

# ---------------------------------
# 2️⃣ CAPTURE-ONLY FPS
# ---------------------------------
elif mode == "capture":

    start = time.time()
    frames = 0

    while time.time() - start < duration:
        frame = picam.capture_array()
        frames += 1

    fps = frames / duration
    print(f"Capture-only FPS: {fps:.2f}")

# ---------------------------------
# 3️⃣ CAPTURE + RECORD
# ---------------------------------
elif mode == "record":

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(output_name, fourcc, 30, (resW, resH))

    start = time.time()
    frames = 0

    while time.time() - start < duration:
        frame = picam.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        writer.write(frame_bgr)
        frames += 1

    writer.release()

    fps = frames / duration
    print(f"Capture + Record FPS: {fps:.2f}")
    print(f"Saved video: {output_name}")

# ---------------------------------
# 4️⃣ DISPLAY + RECORD
# ---------------------------------
elif mode == "display":

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(output_name, fourcc, 30, (resW, resH))

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

    writer.release()
    cv2.destroyAllWindows()

    fps = frames / duration
    print(f"Display + Record FPS: {fps:.2f}")
    print(f"Saved video: {output_name}")

picam.stop()
print("Done.")
