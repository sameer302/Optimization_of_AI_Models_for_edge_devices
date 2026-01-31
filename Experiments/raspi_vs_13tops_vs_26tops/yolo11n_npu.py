import os
import sys
import argparse
import glob
import time

import cv2
import numpy as np

from hailo_platform import (
    HEF, VDevice, ConfigureParams,
    InputVStreamParams, OutputVStreamParams,
    InferVStreams
)

# ---------------- ARGUMENTS ----------------
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True, help='Path to .hef model')
parser.add_argument('--source', required=True)
parser.add_argument('--thresh', default=0.5, type=float)
parser.add_argument('--resolution', default=None)
parser.add_argument('--record', action='store_true')
args = parser.parse_args()

# ---------------- CHECK MODEL ----------------
if not os.path.exists(args.model):
    print("ERROR: .hef file not found")
    sys.exit(1)

# ---------------- LABELS (COCO) ----------------
labels = [
    "person","bicycle","car","motorcycle","airplane","bus","train","truck","boat",
    "traffic light","fire hydrant","stop sign","parking meter","bench","bird","cat",
    "dog","horse","sheep","cow","elephant","bear","zebra","giraffe","backpack",
    "umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sports ball",
    "kite","baseball bat","baseball glove","skateboard","surfboard","tennis racket",
    "bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple",
    "sandwich","orange","broccoli","carrot","hot dog","pizza","donut","cake","chair",
    "couch","potted plant","bed","dining table","toilet","tv","laptop","mouse",
    "remote","keyboard","cell phone","microwave","oven","toaster","sink",
    "refrigerator","book","clock","vase","scissors","teddy bear","hair drier",
    "toothbrush"
]

# ---------------- SOURCE PARSING ----------------
img_ext = ['.jpg','.png','.bmp','.jpeg']
vid_ext = ['.mp4','.avi','.mkv']

if os.path.isdir(args.source):
    source_type = 'folder'
elif os.path.isfile(args.source):
    ext = os.path.splitext(args.source)[1]
    source_type = 'image' if ext in img_ext else 'video'
elif args.source.startswith("usb"):
    source_type = 'usb'
    usb_idx = int(args.source[3:])
elif args.source.startswith("rpicam"):
    source_type = 'picamera'
else:
    print("Invalid source")
    sys.exit(1)

# ---------------- RESOLUTION ----------------
resize = False
if args.resolution:
    resize = True
    resW, resH = map(int, args.resolution.split('x'))

# ---------------- RECORDING ----------------
if args.record:
    if not resize:
        print("Recording requires --resolution")
        sys.exit(1)
    recorder = cv2.VideoWriter(
        "demo_npu.avi",
        cv2.VideoWriter_fourcc(*'MJPG'),
        30,
        (resW, resH)
    )

# ---------------- LOAD HEF ----------------
hef = HEF(args.model)

with VDevice() as vdevice:
    network_group = vdevice.configure(
        hef,
        ConfigureParams.create_from_hef(hef)
    )[0]

    input_info = network_group.get_input_vstream_infos()[0]

    in_params = InputVStreamParams.make(network_group)
    out_params = OutputVStreamParams.make(network_group)

    # ---------------- INPUT SOURCE INIT ----------------
    if source_type in ['video', 'usb']:
        cap = cv2.VideoCapture(args.source if source_type == 'video' else usb_idx)

    elif source_type == 'picamera':
        from picamera2 import Picamera2
        cap = Picamera2()
        cap.configure(cap.create_video_configuration(
            main={"format": "XRGB8888", "size": (640, 640)}
        ))
        cap.start()

    elif source_type in ['image', 'folder']:
        imgs = [args.source] if source_type == 'image' else glob.glob(args.source + "/*")

    # ---------------- YOLO POSTPROCESS ----------------
    def postprocess(outputs, img_shape):
        boxes, scores, class_ids = [], [], []

        for out in outputs.values():
            out = out.squeeze(0)
            for det in out:
                obj = det[4]
                if obj < args.thresh:
                    continue

                cls_scores = det[5:]
                cls_id = np.argmax(cls_scores)
                score = obj * cls_scores[cls_id]

                if score < args.thresh:
                    continue

                cx, cy, w, h = det[:4]
                x1 = int((cx - w/2) * img_shape[1])
                y1 = int((cy - h/2) * img_shape[0])
                x2 = int((cx + w/2) * img_shape[1])
                y2 = int((cy + h/2) * img_shape[0])

                boxes.append([x1, y1, x2-x1, y2-y1])
                scores.append(float(score))
                class_ids.append(cls_id)

        idxs = cv2.dnn.NMSBoxes(boxes, scores, args.thresh, 0.45)
        return boxes, scores, class_ids, idxs

    # ---------------- INFERENCE LOOP ----------------
    fps_buf = []

    with InferVStreams(network_group, in_params, out_params) as infer:
        while True:
            t0 = time.perf_counter()

            if source_type in ['video', 'usb']:
                ret, frame = cap.read()
                if not ret:
                    break

            elif source_type == 'picamera':
                frame = cv2.cvtColor(cap.capture_array(), cv2.COLOR_BGRA2BGR)

            else:
                if not imgs:
                    break
                frame = cv2.imread(imgs.pop(0))

            if resize:
                frame = cv2.resize(frame, (resW, resH))

            # -------- PREPROCESS --------
            inp = cv2.resize(frame, (640, 640))
            inp = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
            inp = np.expand_dims(inp, axis=0).astype(np.uint8)

            outputs = infer.infer({input_info.name: inp})

            boxes, scores, class_ids, idxs = postprocess(outputs, frame.shape)

            if len(idxs) > 0:
                for i in idxs.flatten():
                    x,y,w,h = boxes[i]
                    cls = class_ids[i]
                    conf = scores[i]
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    cv2.putText(frame,f"{labels[cls]} {conf:.2f}",
                                (x,y-5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)

            fps = 1.0 / (time.perf_counter() - t0)
            fps_buf.append(fps)
            if len(fps_buf) > 50:
                fps_buf.pop(0)

            cv2.putText(frame,f"FPS: {np.mean(fps_buf):.2f}",
                        (10,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)

            cv2.imshow("YOLOv11n Hailo NPU", frame)
            if args.record:
                recorder.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    if source_type in ['video', 'usb']:
        cap.release()
    elif source_type == 'picamera':
        cap.stop()

    if args.record:
        recorder.release()

cv2.destroyAllWindows()
