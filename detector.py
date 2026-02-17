#!/usr/bin/env python3
"""
Object Detection Module using YOLOv8n
Optimized for Raspberry Pi 5
"""

import cv2
import numpy as np
from ultralytics import YOLO
from utils import logger

class ObjectDetector:
    """Handles YOLO-based object detection"""
    
    # Detection classes (includes currency)
    CLASSES = [
        'vehicle', 'Toilet', 'bench', 'green_pedestrian_light',
        'red_pedestrian_light', 'stair', 'zebra','10', '100', '20',
        '200', '2000', '50', '500'
    ]
    
    # Currency classes for filtering
    CURRENCY_CLASSES = {'10', '100', '20', '200', '2000', '50', '500'}
    
    # Navigation priority order
    PRIORITY_ORDER = [
        'vehicle',
        'red_pedestrian_light',
        'zebra',
        'bench',
        'stair',
        'Toilet',
        'green_pedestrian_light'
    ]
    
    def __init__(self, model_path="best.pt", confidence_threshold=0.6, camera_index=0, include_currency=False):
        """Initialize detector with YOLO model and camera"""
        self.confidence_threshold = confidence_threshold
        self.include_currency = bool(include_currency)
        
        try:
            # Load YOLO model
            logger.info(f"Loading YOLO model from {model_path}")
            self.model = YOLO(model_path)
            
            # Initialize camera
            logger.info(f"Initializing camera {camera_index}")
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                raise RuntimeError("Failed to open camera")
            
            # Set camera properties for performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Get frame dimensions
            ret, frame = self.camera.read()
            if ret:
                self.frame_height, self.frame_width = frame.shape[:2]
                logger.info(f"Camera initialized: {self.frame_width}x{self.frame_height}")
            else:
                raise RuntimeError("Failed to read from camera")
                
        except Exception as e:
            logger.error(f"Detector initialization failed: {e}")
            raise
    
    def detect_once(self):
        """Perform single frame detection"""
        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return []
        return self._process_frame(frame)
    
    def detect_continuous(self, num_frames=5, interval=0.2):
        """Perform continuous detection over multiple frames"""
        import time
        results = []
        for i in range(num_frames):
            ret, frame = self.camera.read()
            if ret:
                detections = self._process_frame(frame)
                results.append(detections)
            else:
                logger.warning(f"Frame {i} capture failed")
            if i < num_frames - 1:
                time.sleep(interval)
        return results
    
    def _process_frame(self, frame):
        """Process a single frame and return filtered detections"""
        results = self.model(frame, verbose=False)[0]
        detections = []
        
        for box in results.boxes:
            confidence = float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue
            
            class_id = int(box.cls[0])
            class_name = self.CLASSES[class_id] if class_id < len(self.CLASSES) else "unknown"
            
            confidence = float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue
            
            # Skip currency classes unless explicitly enabled
            if class_name in self.CURRENCY_CLASSES and not self.include_currency:
                continue
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            width = x2 - x1
            height = y2 - y1
            
            location = self._get_spatial_location(center_x)
            distance = self._estimate_distance(height)
            
            detection = {
                'class': class_name,
                'confidence': confidence,
                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                'center': (int(center_x), int(center_y)),
                'width': width,
                'height': height,
                'location': location,
                'distance': distance
            }
            
            detections.append(detection)
        
        # Sort by priority
        detections.sort(key=lambda d: self._get_priority(d['class']))
        return detections
    
    def _get_spatial_location(self, center_x):
        """Determine if object is on left, center, or right"""
        third_width = self.frame_width / 3
        if center_x < third_width:
            return "left"
        elif center_x < 2 * third_width:
            return "center"
        else:
            return "right"
    
    def _estimate_distance(self, bbox_height):
        """Estimate distance category based on bounding box height"""
        height_ratio = bbox_height / self.frame_height
        if height_ratio > 0.4:
            return "very close"
        elif height_ratio > 0.15:
            return "near"
        else:
            return "far"
    
    def _get_priority(self, class_name):
        """Get priority index for sorting (lower = higher priority)"""
        try:
            return self.PRIORITY_ORDER.index(class_name)
        except ValueError:
            return len(self.PRIORITY_ORDER)
    
    def detect_vehicle_movement(self, detections_over_time):
        """Detect if vehicles are moving toward the user"""
        if len(detections_over_time) < 2:
            return []
        
        moving_vehicles = []
        vehicle_tracks = {}
        
        for frame_idx, frame_detections in enumerate(detections_over_time):
            for detection in frame_detections:
                if detection['class'] == 'vehicle':
                    center_x, center_y = detection['center']
                    matched = False
                    
                    for track_id, track in vehicle_tracks.items():
                        last_center = track['centers'][-1]
                        distance = np.sqrt((center_x - last_center[0])**2 + 
                                           (center_y - last_center[1])**2)
                        if distance < 100:
                            track['centers'].append((center_x, center_y))
                            track['frames'].append(frame_idx)
                            matched = True
                            break
                    
                    if not matched:
                        track_id = len(vehicle_tracks)
                        vehicle_tracks[track_id] = {
                            'centers': [(center_x, center_y)],
                            'frames': [frame_idx],
                            'detection': detection
                        }
        
        for track in vehicle_tracks.values():
            if len(track['centers']) < 2:
                continue
            y_coords = [c[1] for c in track['centers']]
            y_movement = y_coords[-1] - y_coords[0]
            if y_movement > 20:
                moving_vehicles.append({
                    'detection': track['detection'],
                    'movement': 'approaching',
                    'y_displacement': y_movement
                })
        
        return moving_vehicles
    
    def cleanup(self):
        """Release camera resources"""
        if hasattr(self, 'camera') and self.camera.isOpened():
            self.camera.release()
            logger.info("Camera released")
