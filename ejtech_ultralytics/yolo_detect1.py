import os
import threading
import queue

NUM_THREADS = 2

os.environ["OMP_NUM_THREADS"] = str(NUM_THREADS)
os.environ["OPENBLAS_NUM_THREADS"] = str(NUM_THREADS)
os.environ["MKL_NUM_THREADS"] = str(NUM_THREADS)
os.environ["NUMEXPR_NUM_THREADS"] = str(NUM_THREADS)

import torch
torch.set_num_threads(NUM_THREADS)
torch.set_num_interop_threads(1)

import sys
import argparse
import glob
import time
import csv

import cv2
cv2.setNumThreads(NUM_THREADS)

import numpy as np
from ultralytics import YOLO
from datetime import datetime

# ─────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True,
                    help='Path to YOLO model file (e.g. yolo11n.pt)')
parser.add_argument('--source', required=True,
                    help='Image source: file, folder, video, usb0, picamera0')
parser.add_argument('--thresh', default=0.5,
                    help='Confidence threshold (default 0.5)')
parser.add_argument('--output_resolution', default=None,
                    help='Display resolution WxH (e.g. 640x480)')
parser.add_argument('--capture_resolution', default=None,
                    help='Capture resolution WxH (e.g. 640x480)')
parser.add_argument('--record', action='store_true',
                    help='Record output to demo1.avi (requires --output_resolution)')
parser.add_argument('--csv', required=True,
                    help='Path to CSV file for FPS logging')
args = parser.parse_args()

# ─────────────────────────────────────────────
# Parse arguments
# ─────────────────────────────────────────────
model_path        = args.model
img_source        = args.source
min_thresh        = float(args.thresh)
user_res          = args.output_resolution
capture_res       = args.capture_resolution
record            = args.record
csv_path          = args.csv

# ─────────────────────────────────────────────
# CSV setup
# ─────────────────────────────────────────────
csv_file   = open(csv_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['timestamp', 'frame_count', 'fps', 'latency_ms'])

# ─────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────
if not os.path.exists(model_path):
    print('ERROR: Model path is invalid or model was not found.')
    sys.exit(0)

model  = YOLO(model_path, task='detect')
labels = model.names

# ─────────────────────────────────────────────
# Source type detection
# ─────────────────────────────────────────────
img_ext_list = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp', '.BMP']
vid_ext_list = ['.avi', '.mov', '.mp4', '.mkv', '.wmv']

if os.path.isdir(img_source):
    source_type = 'folder'
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = 'image'
    elif ext in vid_ext_list:
        source_type = 'video'
    else:
        print(f'Unsupported file extension: {ext}')
        sys.exit(0)
elif 'usb' in img_source:
    source_type = 'usb'
    usb_idx = int(img_source[3:])
elif 'picamera' in img_source:
    source_type = 'picamera'
    picam_idx = int(img_source[8:])
else:
    print(f'Invalid source: {img_source}')
    sys.exit(0)

# ─────────────────────────────────────────────
# Resolution setup
# ─────────────────────────────────────────────
resize_output = False
if user_res:
    resize_output = True
    resW, resH = int(user_res.split('x')[0]), int(user_res.split('x')[1])

cap_resW, cap_resH = None, None
if capture_res:
    cap_resW, cap_resH = int(capture_res.split('x')[0]), int(capture_res.split('x')[1])

# ─────────────────────────────────────────────
# Recording setup
# ─────────────────────────────────────────────
if record:
    if source_type not in ['video', 'usb']:
        print('Recording only works for video and camera sources.')
        sys.exit(0)
    if not user_res:
        print('Please specify --output_resolution to record.')
        sys.exit(0)
    record_name = 'demo1.avi'
    record_fps  = 30
    recorder    = cv2.VideoWriter(record_name, cv2.VideoWriter_fourcc(*'MJPG'), record_fps, (resW, resH))

# ─────────────────────────────────────────────
# Source initialisation
# ─────────────────────────────────────────────
if source_type == 'image':
    imgs_list = [img_source]

elif source_type == 'folder':
    imgs_list = [f for f in glob.glob(img_source + '/*')
                 if os.path.splitext(f)[1] in img_ext_list]

elif source_type in ['video', 'usb']:
    cap_arg = img_source if source_type == 'video' else usb_idx
    cap = cv2.VideoCapture(cap_arg)
    if capture_res:
        cap.set(3, cap_resW)
        cap.set(4, cap_resH)

elif source_type == 'picamera':
    from picamera2 import Picamera2
    cap   = Picamera2(picam_idx)
    pic_w = cap_resW if cap_resW else (resW if resize_output else 640)
    pic_h = cap_resH if cap_resH else (resH if resize_output else 480)
    cap.configure(cap.create_video_configuration(
        main={"format": 'XRGB8888', "size": (pic_w, pic_h)}))
    cap.start()

    # ── Producer-Consumer: capture thread ──────────────────────────────────
    # Runs on whichever core the OS assigns (ideally core 3 via taskset).
    # Inference (main thread) runs on the other core.
    # Queue size = 4: capture can run up to 4 frames ahead of inference,
    # keeping the capture thread busy even when inference is slightly slower.
    # put_nowait drops frames instead of blocking — this is intentional:
    # we never want the capture thread waiting on inference.
    # ──────────────────────────────────────────────────────────────────────
    frame_queue     = queue.Queue(maxsize=4)
    capture_running = threading.Event()
    capture_running.set()

    def picamera_capture_worker():
        """
        Dedicated capture thread — decoupled from inference.
        Converts BGRA → BGR and drops frames when queue is full
        so capture never blocks on a slow inference loop.
        """
        while capture_running.is_set():
            frame_bgra = cap.capture_array()
            frame_bgr  = cv2.cvtColor(np.copy(frame_bgra), cv2.COLOR_BGRA2BGR)
            if frame_bgr is None:
                print('[Capture] Picamera read failed.')
                capture_running.clear()
                break
            try:
                frame_queue.put_nowait(frame_bgr)   # non-blocking: drop if full
            except queue.Full:
                pass                                 # inference is behind — drop frame

    capture_thread = threading.Thread(
        target=picamera_capture_worker,
        name='PiCapture',
        daemon=True
    )
    capture_thread.start()
    print(f'[Info] Capture thread started: {capture_thread.name} (TID will appear in htop)')

# ─────────────────────────────────────────────
# Misc setup
# ─────────────────────────────────────────────
bbox_colors = [
    (164, 120,  87), ( 68, 148, 228), ( 93,  97, 209), (178, 182, 133),
    ( 88, 159, 106), ( 96, 202, 231), (159, 124, 168), (169, 162, 241),
    ( 98, 118, 150), (172, 176, 184)
]

avg_frame_rate  = 0
frame_rate_buffer = []
latency_buffer    = []
fps_avg_len       = 10
img_count         = 0
frame_count       = 0

# ─────────────────────────────────────────────
# Main inference loop
# ─────────────────────────────────────────────
print('[Info] Starting inference loop...')

while True:
    frame_count += 1
    t_start = time.perf_counter()

    # ── Frame acquisition ──────────────────────────────────────────────────
    if source_type in ['image', 'folder']:
        if img_count >= len(imgs_list):
            print('All images processed. Exiting.')
            break
        frame = cv2.imread(imgs_list[img_count])
        img_count += 1

    elif source_type == 'video':
        ret, frame = cap.read()
        if not ret:
            print('End of video. Exiting.')
            break

    elif source_type == 'usb':
        ret, frame = cap.read()
        if frame is None or not ret:
            print('Camera read failed. Exiting.')
            break

    elif source_type == 'picamera':
        # ── Consumer side ─────────────────────────────────────────────────
        # Blocks for up to 2 s waiting for the capture thread to produce a
        # frame. Under normal operation this returns almost immediately.
        # ──────────────────────────────────────────────────────────────────
        try:
            frame = frame_queue.get(timeout=2.0)
        except queue.Empty:
            print('[Inference] No frames received — capture thread may have died. Exiting.')
            break
        if not capture_running.is_set():
            print('[Inference] Capture thread stopped. Exiting.')
            break

    # ── Log resolution on first frame ─────────────────────────────────────
    if frame_count == 1:
        inf_h, inf_w = frame.shape[:2]
        print(f'[Info] Inference resolution: {inf_w} x {inf_h}')

    # ── YOLO inference ────────────────────────────────────────────────────
    results = model(frame, verbose=False)

    # ── Optional resize for display ───────────────────────────────────────
    if resize_output:
        frame = cv2.resize(frame, (resW, resH))

    # ── Draw detections ───────────────────────────────────────────────────
    detections   = results[0].boxes
    object_count = 0

    for i in range(len(detections)):
        xyxy      = detections[i].xyxy.cpu().numpy().squeeze()
        xmin, ymin, xmax, ymax = xyxy.astype(int)

        if resize_output:
            src_h, src_w = results[0].orig_shape
            xmin = int(xmin * resW / src_w)
            ymin = int(ymin * resH / src_h)
            xmax = int(xmax * resW / src_w)
            ymax = int(ymax * resH / src_h)

        classidx  = int(detections[i].cls.item())
        classname = labels[classidx]
        conf      = detections[i].conf.item()

        if conf > min_thresh:
            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

            label     = f'{classname}: {int(conf * 100)}%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(frame,
                          (xmin, label_ymin - labelSize[1] - 10),
                          (xmin + labelSize[0], label_ymin + baseLine - 10),
                          color, cv2.FILLED)
            cv2.putText(frame, label, (xmin, label_ymin - 7),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            object_count += 1

    # ── Overlay stats ─────────────────────────────────────────────────────
    if source_type in ['video', 'usb', 'picamera']:
        cv2.putText(frame, f'FPS: {avg_frame_rate:0.2f}',
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)

    # Show queue depth for picamera — useful for tuning
    if source_type == 'picamera':
        q_depth = frame_queue.qsize()
        cv2.putText(frame, f'Queue: {q_depth}',
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 200, 100), 2)

    cv2.putText(frame, f'Objects: {object_count}',
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)
    cv2.imshow('YOLO detection results', frame)

    if record:
        recorder.write(frame)

    # ── Key handling ──────────────────────────────────────────────────────
    wait_ms = 0 if source_type in ['image', 'folder'] else 5
    key = cv2.waitKey(wait_ms)
    if key in [ord('q'), ord('Q')]:
        break
    elif key in [ord('s'), ord('S')]:
        cv2.waitKey()
    elif key in [ord('p'), ord('P')]:
        cv2.imwrite('capture.png', frame)

    # ── FPS / latency calculation ─────────────────────────────────────────
    t_stop         = time.perf_counter()
    frame_rate_calc = 1.0 / (t_stop - t_start)
    latency_ms     = (t_stop - t_start) * 1000

    if len(frame_rate_buffer) >= fps_avg_len:
        frame_rate_buffer.pop(0)
    frame_rate_buffer.append(frame_rate_calc)
    avg_frame_rate = np.mean(frame_rate_buffer)

    if len(latency_buffer) >= fps_avg_len:
        latency_buffer.pop(0)
    latency_buffer.append(latency_ms)
    avg_latency = np.mean(latency_buffer)

    # ── CSV logging every N frames ────────────────────────────────────────
    if frame_count % fps_avg_len == 0:
        csv_writer.writerow([
            datetime.now().isoformat(),
            frame_count,
            round(avg_frame_rate, 3),
            round(avg_latency, 3)
        ])
        csv_file.flush()

# ─────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────
print('[Info] Cleaning up...')
csv_file.close()

if source_type == 'picamera':
    capture_running.clear()         # signal capture thread to exit
    capture_thread.join(timeout=2)  # wait for it to finish
    cap.stop()
elif source_type in ['video', 'usb']:
    cap.release()

if record:
    recorder.release()

cv2.destroyAllWindows()
print('[Info] Done.')