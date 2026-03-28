import os
import sys
import argparse
import time
import csv
import ctypes
import glob

from multiprocessing import Process, shared_memory, Value, Event

NUM_THREADS = 2

os.environ["OMP_NUM_THREADS"] = str(NUM_THREADS)
os.environ["OPENBLAS_NUM_THREADS"] = str(NUM_THREADS)
os.environ["MKL_NUM_THREADS"] = str(NUM_THREADS)
os.environ["NUMEXPR_NUM_THREADS"] = str(NUM_THREADS)

import torch
torch.set_num_threads(NUM_THREADS)
torch.set_num_interop_threads(1)

import cv2
cv2.setNumThreads(NUM_THREADS)

import numpy as np
from ultralytics import YOLO
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Helper: pin current process to a specific core
# ─────────────────────────────────────────────────────────────────────────────
def pin_to_core(core_id: int):
    """
    Uses libc sched_setaffinity to pin the calling process to a single core.
    Called independently inside each process so each one lands on its own core.
    """
    libc = ctypes.CDLL('libc.so.6', use_errno=True)
    mask = ctypes.c_ulong(1 << core_id)
    ret  = libc.sched_setaffinity(0, ctypes.sizeof(mask), ctypes.byref(mask))
    if ret != 0:
        print(f'[Warning] sched_setaffinity failed for core {core_id}, errno={ctypes.get_errno()}')
    else:
        print(f'[Info] Process {os.getpid()} pinned to core {core_id}')


# ─────────────────────────────────────────────────────────────────────────────
# Capture process  (runs on CORE 3)
# ─────────────────────────────────────────────────────────────────────────────
def capture_process(
    shm_name:    str,
    frame_shape: tuple,
    ready_flag:  Value,   # 0 = capture may write, 1 = inference may read
    stop_event:  Event,
    pic_w:       int,
    pic_h:       int,
    capture_core: int,
):
    """
    Dedicated capture process.
    - Pinned to capture_core (core 3 by default).
    - Has its OWN GIL — runs truly in parallel with inference.
    - Writes BGR frames into shared memory and sets ready_flag = 1.
    - Drops the frame silently if inference hasn't consumed the previous one
      (ready_flag still == 1), so capture never blocks on inference speed.
    """
    # ── Pin this process to its core ─────────────────────────────────────────
    pin_to_core(capture_core)

    # ── Per-process thread limits ─────────────────────────────────────────────
    import cv2
    import numpy as np
    cv2.setNumThreads(1)          # capture process only needs 1 thread

    # ── Attach to shared memory ───────────────────────────────────────────────
    shm  = shared_memory.SharedMemory(name=shm_name)
    buf  = np.ndarray(frame_shape, dtype=np.uint8, buffer=shm.buf)

    # ── Open Picamera2 ────────────────────────────────────────────────────────
    from picamera2 import Picamera2
    cap = Picamera2(0)
    cap.configure(cap.create_video_configuration(
        main={"format": 'XRGB8888', "size": (pic_w, pic_h)}))
    cap.start()
    print(f'[Capture] Picamera2 started at {pic_w}x{pic_h}')

    # ── Capture loop ──────────────────────────────────────────────────────────
    while not stop_event.is_set():
        frame_bgra = cap.capture_array()
        frame_bgr  = cv2.cvtColor(np.copy(frame_bgra), cv2.COLOR_BGRA2BGR)

        if frame_bgr is None:
            print('[Capture] capture_array() returned None — camera error.')
            stop_event.set()
            break

        # Only write when inference has consumed the last frame.
        # If ready_flag == 1 inference is still busy — drop this frame
        # to keep capture running at full speed without ever blocking.
        if ready_flag.value == 0:
            np.copyto(buf, frame_bgr)   # zero-copy write into shared memory
            ready_flag.value = 1        # signal: new frame is ready

    cap.stop()
    shm.close()
    print('[Capture] Process exiting.')


# ─────────────────────────────────────────────────────────────────────────────
# Main  (inference process, runs on CORE 2)
# ─────────────────────────────────────────────────────────────────────────────
def main():

    # ── Argument parsing ──────────────────────────────────────────────────────
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',  required=True,
                        help='Path to YOLO model file (e.g. yolo11n.pt)')
    parser.add_argument('--source', required=True,
                        help='Source: image, folder, video, usb0, picamera0')
    parser.add_argument('--thresh', default=0.5,
                        help='Confidence threshold (default 0.5)')
    parser.add_argument('--output_resolution',  default=None,
                        help='Display resolution WxH (e.g. 640x480)')
    parser.add_argument('--capture_resolution', default=None,
                        help='Capture resolution WxH (e.g. 640x480)')
    parser.add_argument('--record', action='store_true',
                        help='Record output to demo1.avi (needs --output_resolution)')
    parser.add_argument('--csv',    required=True,
                        help='Path to CSV file for FPS logging')
    parser.add_argument('--inference_core', type=int, default=2,
                        help='CPU core for inference process (default: 2)')
    parser.add_argument('--capture_core',   type=int, default=3,
                        help='CPU core for capture process  (default: 3)')
    args = parser.parse_args()

    model_path    = args.model
    img_source    = args.source
    min_thresh    = float(args.thresh)
    user_res      = args.output_resolution
    capture_res   = args.capture_resolution
    record        = args.record
    csv_path      = args.csv
    inf_core      = args.inference_core
    cap_core      = args.capture_core

    # ── Pin inference (main) process to its core ──────────────────────────────
    pin_to_core(inf_core)

    # ── CSV ───────────────────────────────────────────────────────────────────
    csv_file   = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp', 'frame_count', 'fps', 'latency_ms'])

    # ── Model ─────────────────────────────────────────────────────────────────
    if not os.path.exists(model_path):
        print('ERROR: Model not found.')
        sys.exit(1)
    model  = YOLO(model_path, task='detect')
    labels = model.names

    # ── Source type ───────────────────────────────────────────────────────────
    img_ext_list = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp', '.BMP']
    vid_ext_list = ['.avi', '.mov', '.mp4', '.mkv', '.wmv']

    if os.path.isdir(img_source):
        source_type = 'folder'
    elif os.path.isfile(img_source):
        _, ext = os.path.splitext(img_source)
        source_type = 'image' if ext in img_ext_list else \
                      'video' if ext in vid_ext_list else None
        if source_type is None:
            print(f'Unsupported extension: {ext}')
            sys.exit(1)
    elif 'usb' in img_source:
        source_type = 'usb'
        usb_idx = int(img_source[3:])
    elif 'picamera' in img_source:
        source_type = 'picamera'
    else:
        print(f'Invalid source: {img_source}')
        sys.exit(1)

    # ── Resolution ────────────────────────────────────────────────────────────
    resize_output = False
    resW = resH = None
    if user_res:
        resize_output = True
        resW, resH = int(user_res.split('x')[0]), int(user_res.split('x')[1])

    cap_resW = cap_resH = None
    if capture_res:
        cap_resW, cap_resH = int(capture_res.split('x')[0]), int(capture_res.split('x')[1])

    # ── Recording ─────────────────────────────────────────────────────────────
    recorder = None
    if record:
        if source_type not in ['video', 'usb']:
            print('Recording only supported for video/usb.')
            sys.exit(1)
        if not user_res:
            print('Specify --output_resolution to record.')
            sys.exit(1)
        recorder = cv2.VideoWriter('demo1.avi',
                                   cv2.VideoWriter_fourcc(*'MJPG'), 30, (resW, resH))

    # ── Non-picamera source init ──────────────────────────────────────────────
    cap = None
    imgs_list = []

    if source_type == 'image':
        imgs_list = [img_source]
    elif source_type == 'folder':
        imgs_list = [f for f in glob.glob(img_source + '/*')
                     if os.path.splitext(f)[1] in img_ext_list]
    elif source_type in ['video', 'usb']:
        cap = cv2.VideoCapture(img_source if source_type == 'video' else usb_idx)
        if capture_res:
            cap.set(3, cap_resW)
            cap.set(4, cap_resH)

    # ── Picamera: shared memory + capture process ─────────────────────────────
    shm          = None
    cap_proc     = None
    stop_event   = None
    ready_flag   = None
    shared_frame = None

    if source_type == 'picamera':
        pic_w = cap_resW if cap_resW else (resW if resize_output else 640)
        pic_h = cap_resH if cap_resH else (resH if resize_output else 480)

        frame_shape = (pic_h, pic_w, 3)      # BGR uint8
        frame_bytes = int(np.prod(frame_shape))

        # Allocate shared memory — one frame buffer, no serialisation overhead
        shm          = shared_memory.SharedMemory(create=True, size=frame_bytes)
        shared_frame = np.ndarray(frame_shape, dtype=np.uint8, buffer=shm.buf)

        # ready_flag: 0 = capture may write, 1 = inference may read
        ready_flag = Value('i', 0)
        stop_event = Event()

        cap_proc = Process(
            target=capture_process,
            args=(shm.name, frame_shape, ready_flag, stop_event,
                  pic_w, pic_h, cap_core),
            daemon=True,
            name='CaptureProcess'
        )
        cap_proc.start()
        print(f'[Inference] Capture  process PID: {cap_proc.pid} → core {cap_core}')
        print(f'[Inference] Inference process PID: {os.getpid()} → core {inf_core}')

        # Wait for first frame before entering inference loop
        print('[Inference] Waiting for first frame from capture process...')
        timeout = time.time() + 10.0
        while ready_flag.value == 0:
            if time.time() > timeout:
                print('[Inference] Timeout — capture process never produced a frame.')
                stop_event.set()
                cap_proc.join(timeout=2)
                sys.exit(1)
            time.sleep(0.01)
        print('[Inference] First frame received. Starting inference loop.')

    # ── Misc ──────────────────────────────────────────────────────────────────
    bbox_colors = [
        (164, 120,  87), ( 68, 148, 228), ( 93,  97, 209), (178, 182, 133),
        ( 88, 159, 106), ( 96, 202, 231), (159, 124, 168), (169, 162, 241),
        ( 98, 118, 150), (172, 176, 184)
    ]

    avg_frame_rate    = 0.0
    frame_rate_buffer = []
    latency_buffer    = []
    fps_avg_len       = 10
    img_count         = 0
    frame_count       = 0

    # ── Inference loop ────────────────────────────────────────────────────────
    print('[Inference] Loop started.')

    while True:
        frame_count += 1
        t_start = time.perf_counter()

        # ── Frame acquisition ─────────────────────────────────────────────────
        if source_type in ['image', 'folder']:
            if img_count >= len(imgs_list):
                print('All images processed.')
                break
            frame = cv2.imread(imgs_list[img_count])
            img_count += 1

        elif source_type == 'video':
            ret, frame = cap.read()
            if not ret:
                print('End of video.')
                break

        elif source_type == 'usb':
            ret, frame = cap.read()
            if frame is None or not ret:
                print('Camera read failed.')
                break

        elif source_type == 'picamera':
            # ── Consumer side ─────────────────────────────────────────────────
            # Spin-wait until capture process signals a new frame.
            # sleep(0.5ms) yields the core briefly instead of burning it
            # on a pure busy-wait — keeps spin overhead under 2% CPU.
            spin_start = time.time()
            while ready_flag.value == 0:
                if time.time() - spin_start > 2.0:
                    print('[Inference] No frame for 2s — capture may have died.')
                    stop_event.set()
                    break
                time.sleep(0.0005)

            if stop_event.is_set():
                break

            frame = shared_frame.copy()   # copy out before capture overwrites
            ready_flag.value = 0          # release: capture may write next frame

        # ── Log resolution once ───────────────────────────────────────────────
        if frame_count == 1:
            h, w = frame.shape[:2]
            print(f'[Inference] Frame resolution: {w}x{h}')

        # ── YOLO inference ────────────────────────────────────────────────────
        results = model(frame, verbose=False)

        # ── Optional resize for display ───────────────────────────────────────
        if resize_output:
            frame = cv2.resize(frame, (resW, resH))

        # ── Draw detections ───────────────────────────────────────────────────
        detections   = results[0].boxes
        object_count = 0

        for i in range(len(detections)):
            xyxy = detections[i].xyxy.cpu().numpy().squeeze()
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

                label      = f'{classname}: {int(conf * 100)}%'
                lsize, bas = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                ly         = max(ymin, lsize[1] + 10)
                cv2.rectangle(frame,
                              (xmin, ly - lsize[1] - 10),
                              (xmin + lsize[0], ly + bas - 10),
                              color, cv2.FILLED)
                cv2.putText(frame, label, (xmin, ly - 7),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                object_count += 1

        # ── Overlay ───────────────────────────────────────────────────────────
        if source_type in ['video', 'usb', 'picamera']:
            cv2.putText(frame, f'FPS: {avg_frame_rate:0.2f}',
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)

        cv2.putText(frame, f'Objects: {object_count}',
                    (10, 45), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)

        cv2.imshow('YOLO detection results', frame)
        if recorder:
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

        # ── FPS / latency ─────────────────────────────────────────────────────
        t_stop          = time.perf_counter()
        frame_rate_calc = 1.0 / (t_stop - t_start)
        latency_ms      = (t_stop - t_start) * 1000

        if len(frame_rate_buffer) >= fps_avg_len:
            frame_rate_buffer.pop(0)
        frame_rate_buffer.append(frame_rate_calc)
        avg_frame_rate = np.mean(frame_rate_buffer)

        if len(latency_buffer) >= fps_avg_len:
            latency_buffer.pop(0)
        latency_buffer.append(latency_ms)
        avg_latency = np.mean(latency_buffer)

        if frame_count % fps_avg_len == 0:
            csv_writer.writerow([
                datetime.now().isoformat(),
                frame_count,
                round(avg_frame_rate, 3),
                round(avg_latency, 3)
            ])
            csv_file.flush()

    # ── Cleanup ───────────────────────────────────────────────────────────────
    print('[Inference] Cleaning up...')
    csv_file.close()

    if source_type == 'picamera':
        stop_event.set()
        cap_proc.join(timeout=3)
        if cap_proc.is_alive():
            cap_proc.terminate()
        shm.close()
        shm.unlink()           # free shared memory block from OS

    elif source_type in ['video', 'usb']:
        cap.release()

    if recorder:
        recorder.release()

    cv2.destroyAllWindows()
    print('[Inference] Done.')


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# IMPORTANT: multiprocessing on Linux requires the if __name__ == '__main__'
# guard — without it, spawning a child process re-imports this file and
# tries to launch another child, causing infinite recursive spawning.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()