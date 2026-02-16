#!/usr/bin/env python3
"""
Object Detection Module - PC Optimized
YOLOv8 + Live Visualization + FPS + Distance Estimation
"""

import cv2
import time
import torch
from ultralytics import YOLO


class ObjectDetector:

    CLASSES = [
        'vehicle', 'Toilet', 'bench', 'green_pedestrian_light',
        'red_pedestrian_light', 'stair', 'zebra',
        '10', '100', '20', '200', '2000', '50', '500'
    ]

    CURRENCY_CLASSES = {'10', '100', '20', '200', '2000', '50', '500'}

    CONFIDENCE_THRESHOLD = 0.3

    def __init__(self, model_path, camera_index=1, include_currency=False):

        print("Loading YOLO model...")
        self.model = YOLO(model_path)

        # Use GPU if available
        if torch.cuda.is_available():
            print("Using GPU")
            self.model.to("cuda")
        else:
            print("Using CPU")
            self.model.to("cpu")

        # Camera
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Thread-safe camera access
        self.camera_lock = None

        # Whether to include currency classes in detection results
        self.include_currency = bool(include_currency)

        self.prev_time = time.time()

        print("Detector ready")

    # ---------------------------------------------------
    # SET CAMERA LOCK FOR THREAD-SAFE ACCESS
    # ---------------------------------------------------

    def set_camera_lock(self, lock):
        self.camera_lock = lock

    def set_include_currency(self, enabled=True):
        """Enable or disable reporting of currency classes."""
        self.include_currency = bool(enabled)

    # ---------------------------------------------------
    # SINGLE FRAME DETECTION (WITH DRAWING)
    # ---------------------------------------------------

    def detect_frame(self):

        if self.camera_lock:
            self.camera_lock.acquire()

        try:
            ret, frame = self.cap.read()
        finally:
            if self.camera_lock:
                self.camera_lock.release()

        if not ret:
            return [], None

        results = self.model(frame, verbose=False)[0]

        detections = []

        for box in results.boxes:

            confidence = float(box.conf[0])
            if confidence < self.CONFIDENCE_THRESHOLD:
                continue

            class_id = int(box.cls[0])
            class_name = results.names[class_id]

            # Skip currency classes by default unless explicitly enabled
            if class_name in self.CURRENCY_CLASSES and not self.include_currency:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            width = x2 - x1
            height = y2 - y1
            area = width * height

            position = self._determine_position(cx)
            distance = self._estimate_distance(height)

            detections.append({
                "class": class_name,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2],
                "center": (cx, cy),
                "area": area,
                "location": position,
                "distance": distance
            })

            # DRAW BOX
            color = (0, 255, 0)

            if class_name == "vehicle":
                color = (0, 0, 255)
            elif class_name == "zebra":
                color = (255, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            label = f"{class_name} {confidence:.2f} {distance}"
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

            # Draw center
            cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)

        # FPS Counter
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        # Return both detections and the frame for external display
        return detections, frame

    # ---------------------------------------------------
    # MULTI FRAME (FOR MOTION CHECK)
    # ---------------------------------------------------

    def detect_multiple_frames(self, num_frames=5, interval=0.2):

        all_detections = []

        for i in range(num_frames):
            detections, _ = self.detect_frame()
            all_detections.append(detections)

            if i < num_frames - 1:
                time.sleep(interval)

        return all_detections

    # Alias expected by DecisionEngine
    def detect_continuous(self, num_frames=5, interval=0.2):
        return self.detect_multiple_frames(num_frames=num_frames, interval=interval)

    # ---------------------------------------------------
    # VEHICLE MOTION CHECK (Simple Horizontal Movement)
    # ---------------------------------------------------

    def detect_vehicle_movement(self, detections_over_time):

        moving = []

        if len(detections_over_time) < 2:
            return moving

        first_frame = detections_over_time[0]
        last_frame = detections_over_time[-1]

        for vehicle_last in last_frame:
            if vehicle_last["class"] != "vehicle":
                continue

            for vehicle_first in first_frame:
                if vehicle_first["class"] != "vehicle":
                    continue

                dx = abs(
                    vehicle_last["center"][0] -
                    vehicle_first["center"][0]
                )

                if dx > 20:
                    moving.append({
                        "detection": vehicle_last,
                        "movement": dx
                    })

        return moving

    # ---------------------------------------------------
    # POSITION
    # ---------------------------------------------------

    def _determine_position(self, cx):

        third = self.frame_width // 3

        if cx < third:
            return "left"
        elif cx < 2 * third:
            return "center"
        else:
            return "right"

    # ---------------------------------------------------
    # DISTANCE ESTIMATION
    # ---------------------------------------------------

    def _estimate_distance(self, bbox_height):

        ratio = bbox_height / self.frame_height

        if ratio > 0.5:
            return "very_close"
        elif ratio > 0.25:
            return "near"
        else:
            return "far"

    # ---------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------

    def cleanup(self):

        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
        print("Camera released")
