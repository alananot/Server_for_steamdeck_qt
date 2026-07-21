from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, jsonify
import serial

app = Flask(__name__)

model1 = YOLO('runs/detect/light-train-2/weights/best.pt')

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
picam2.set_controls({"ExposureTime": 100, "AnalogueGain": 2.0})

FRAME_W = 640
FRAME_H = 480
LOCK_THRESHOLD = 5
LOCK_LOST_THRESHOLD = 15
MAX_JUMP = 100

latest_frame = None
latest_boxes = []
lock = threading.Lock()

tracked_cx = None
tracked_cy = None
tracked_x1 = 0
tracked_y1 = 0
tracked_x2 = 0
tracked_y2 = 0
lock_counter = 0
lost_counter = 0
is_locked = False
force_unlock = False
unlock_cooldown_until = 0  # Tid då vi börjar leta igen

smooth_cx = 0
smooth_cy = 0

ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=0.01)

def detection_thread():
    global latest_boxes
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        results = model1(frame, conf=0.15, verbose=False, imgsz=256)
        with lock:
            latest_boxes = list(results[0].boxes)

t = threading.Thread(target=detection_thread, daemon=True)
t.start()

def find_closest_box(boxes, cx, cy):
    best_box = None
    best_dist = float('inf')
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        bcx = (x1 + x2) // 2
        bcy = (y1 + y2) // 2
        dist = ((bcx - cx) ** 2 + (bcy - cy) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_box = box
    return best_box, best_dist

def process_frame():
    global tracked_cx, tracked_cy, tracked_x1, tracked_y1, tracked_x2, tracked_y2
    global lock_counter, lost_counter, is_locked, latest_frame, smooth_cx, smooth_cy
    global force_unlock, unlock_cooldown_until

    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    frame = cv2.bitwise_and(frame, mask_3ch)

    with lock:
        latest_frame = frame.copy()
        all_boxes = latest_boxes.copy()

    # Om unlock tryckts — återställ allt och starta cooldown
    if force_unlock:
        tracked_cx = None
        tracked_cy = None
        lock_counter = 0
        lost_counter = 0
        is_locked = False
        force_unlock = False
        unlock_cooldown_until = time.time() + 10

    # Under cooldown — visa ingenting, låt inte kameran låsa
    if time.time() < unlock_cooldown_until:
        return frame

    if len(all_boxes) > 0:
        if tracked_cx is None:
            box = all_boxes[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            tracked_cx = (x1 + x2) // 2
            tracked_cy = (y1 + y2) // 2
            tracked_x1, tracked_y1, tracked_x2, tracked_y2 = x1, y1, x2, y2
            lock_counter = 1
            lost_counter = 0
        else:
            best_box, dist = find_closest_box(all_boxes, tracked_cx, tracked_cy)
            if dist < MAX_JUMP:
                x1, y1, x2, y2 = map(int, best_box.xyxy[0])
                tracked_cx = (x1 + x2) // 2
                tracked_cy = (y1 + y2) // 2
                tracked_x1, tracked_y1, tracked_x2, tracked_y2 = x1, y1, x2, y2
                lock_counter = min(lock_counter + 1, LOCK_THRESHOLD + 1)
                lost_counter = 0
            else:
                lost_counter += 1
    else:
        if tracked_cx is not None:
            lost_counter += 1

    if lost_counter >= LOCK_LOST_THRESHOLD:
        tracked_cx = None
        tracked_cy = None
        lock_counter = 0
        lost_counter = 0
        is_locked = False

    is_locked = lock_counter >= LOCK_THRESHOLD

    # Rita — gul = letar, röd = locked, mindre rektangel
    if tracked_cx is not None and lock_counter > 0:
        margin = 5
        if is_locked:
            color = (255, 0, 0)  # Röd (BGR)
        else:
            color = (0, 255, 255)  # Gul (BGR)

        cv2.rectangle(
            frame,
            (tracked_x1 + margin, tracked_y1 + margin),
            (tracked_x2 - margin, tracked_y2 - margin),
            color, 1
        )
        cv2.circle(frame, (tracked_cx, tracked_cy), 5, color, -1)
        cv2.line(frame, (tracked_cx - 12, tracked_cy), (tracked_cx + 12, tracked_cy), color, 1)
        cv2.line(frame, (tracked_cx, tracked_cy - 12), (tracked_cx, tracked_cy + 12), color, 1)

        smooth_cx = tracked_cx
        smooth_cy = tracked_cy

        data_coord = f"{tracked_cx},{tracked_cy} \n"
        ser.write(data_coord.encode('utf-8'))

    return frame

def generate():
    while True:
        frame = process_frame()
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_frame')
def video_frame():
    frame = process_frame()
    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return Response(jpeg.tobytes(), mimetype='image/jpeg')

@app.route('/status')
def status():
    return jsonify({"locked": is_locked, "cx": smooth_cx, "cy": smooth_cy})

@app.route('/unlock', methods=['POST'])
def unlock():
    global force_unlock
    force_unlock = True
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
