import numpy as np
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--width", type=int, required=True)
parser.add_argument("--height", type=int, required=True)
parser.add_argument("--seconds", type=int, default=5)
args = parser.parse_args()

W = args.width
H = args.height
duration = args.seconds

print(f"\nResolution: {W}x{H}")
print(f"Duration: {duration}s")

# Simulated camera DMA buffer (already in RAM)
buffer = np.empty((H, W, 4), dtype=np.uint8)

# -----------------------------
# Capture-equivalent benchmark
# -----------------------------
start = time.time()
frames = 0

while time.time() - start < duration:
    frame = buffer.copy()   # simulate capture_array() memory copy
    frames += 1

elapsed = time.time() - start
fps = frames / elapsed

print("\n===== CPU Capture-Equivalent Throughput =====")
print(f"Memory Copy FPS: {fps:.2f}")
print("Done.")