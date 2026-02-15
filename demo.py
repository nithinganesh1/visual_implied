#!/usr/bin/env python3
"""
Smart Assistive Navigation System - Visual Demo
Single file for presentation with imshow visualization

Features:
- Real-time object detection with bounding boxes
- Vehicle motion tracking with trails
- All detections labeled
- Crossing safety analysis
- Distance estimation
- Spatial positioning (Left/Center/Right)
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from collections import defaultdict, deque

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_PATH = "best.pt"
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.6
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# Colors for different object types (BGR format)
COLORS = {
    'vehicle': (0, 0, 255),              # Red
    'zebra': (255, 255, 0),              # Cyan
    'stair': (0, 165, 255),              # Orange
    'bench': (147, 20, 255),             # Deep Pink
    'Toilet': (255, 0, 255),             # Magenta
    'green_pedestrian_light': (0, 255, 0),  # Green
    'red_pedestrian_light': (0, 0, 255),    # Red
    'default': (255, 255, 255)           # White
}

# Currency classes to mark differently
CURRENCY_CLASSES = {'10', '100', '20', '200', '2000', '50', '500'}

# ============================================================================
# VEHICLE TRACKER CLASS
# ============================================================================

class VehicleTracker:
    """Track vehicles across frames to detect motion"""
    
    def __init__(self, max_history=10, iou_threshold=0.3):
        self.tracks = {}  # {track_id: deque of positions}
        self.next_id = 0
        self.max_history = max_history
        self.iou_threshold = iou_threshold
        self.track_colors = {}  # {track_id: color}
        
    def update(self, vehicle_detections):
        """Update tracks with new detections"""
        current_positions = {}
        
        # Match detections to existing tracks
        matched_tracks = set()
        matched_detections = set()
        
        for track_id, positions in self.tracks.items():
            if len(positions) == 0:
                continue
                
            last_bbox = positions[-1]['bbox']
            best_match = None
            best_iou = self.iou_threshold
            best_idx = -1
            
            for idx, det in enumerate(vehicle_detections):
                if idx in matched_detections:
                    continue
                    
                iou = self._calculate_iou(last_bbox, det['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_match = det
                    best_idx = idx
            
            if best_match:
                matched_tracks.add(track_id)
                matched_detections.add(best_idx)
                current_positions[track_id] = best_match
        
        # Create new tracks for unmatched detections
        for idx, det in enumerate(vehicle_detections):
            if idx not in matched_detections:
                track_id = self.next_id
                self.next_id += 1
                current_positions[track_id] = det
                self.tracks[track_id] = deque(maxlen=self.max_history)
                # Assign random color for this track
                self.track_colors[track_id] = (
                    np.random.randint(100, 255),
                    np.random.randint(100, 255),
                    np.random.randint(100, 255)
                )
        
        # Update track positions
        for track_id, det in current_positions.items():
            self.tracks[track_id].append({
                'bbox': det['bbox'],
                'center': det['center'],
                'timestamp': time.time()
            })
        
        # Remove old tracks
        self._cleanup_old_tracks()
        
        return self.tracks
    
    def get_motion_info(self, track_id):
        """Get motion information for a track"""
        if track_id not in self.tracks or len(self.tracks[track_id]) < 3:
            return None
        
        positions = list(self.tracks[track_id])
        
        # Calculate movement
        start_center = positions[0]['center']
        end_center = positions[-1]['center']
        
        dx = end_center[0] - start_center[0]
        dy = end_center[1] - start_center[1]
        
        total_movement = np.sqrt(dx**2 + dy**2)
        
        # Determine direction
        direction = "stationary"
        if total_movement > 30:
            if dy > 10:
                direction = "approaching"
            elif dy < -10:
                direction = "departing"
            elif abs(dx) > 10:
                direction = "crossing"
            else:
                direction = "moving"
        
        return {
            'movement': total_movement,
            'direction': direction,
            'dx': dx,
            'dy': dy,
            'is_moving': total_movement > 30
        }
    
    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _cleanup_old_tracks(self):
        """Remove tracks that haven't been updated"""
        current_time = time.time()
        to_remove = []
        
        for track_id, positions in self.tracks.items():
            if len(positions) == 0:
                to_remove.append(track_id)
            else:
                last_time = positions[-1]['timestamp']
                if current_time - last_time > 2.0:  # 2 seconds timeout
                    to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
            if track_id in self.track_colors:
                del self.track_colors[track_id]

# ============================================================================
# CROSSING SAFETY ANALYZER
# ============================================================================

class CrossingSafetyAnalyzer:
    """Analyze crossing safety based on detections"""
    
    def __init__(self):
        self.last_analysis_time = 0
        self.analysis_cooldown = 1.0  # Analyze every 1 second
    
    def analyze(self, detections, vehicle_tracks):
        """Analyze if it's safe to cross"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_analysis_time < self.analysis_cooldown:
            return None
        
        self.last_analysis_time = current_time
        
        # Check for zebra crossing
        has_zebra = any(det['class'] == 'zebra' for det in detections)
        if not has_zebra:
            return {
                'safe': False,
                'reason': 'No zebra crossing detected',
                'color': (0, 0, 255)
            }
        
        # Check for pedestrian lights
        has_green = any(det['class'] == 'green_pedestrian_light' for det in detections)
        has_red = any(det['class'] == 'red_pedestrian_light' for det in detections)
        
        if has_red:
            return {
                'safe': False,
                'reason': 'RED LIGHT - Do not cross',
                'color': (0, 0, 255)
            }
        
        if not has_green:
            return {
                'safe': False,
                'reason': 'No green light detected',
                'color': (0, 165, 255)
            }
        
        # Check for moving vehicles
        for track_id, positions in vehicle_tracks.items():
            if len(positions) >= 3:
                tracker = VehicleTracker()
                motion = tracker.get_motion_info(track_id)
                if motion and motion['is_moving']:
                    if motion['direction'] == 'approaching':
                        return {
                            'safe': False,
                            'reason': 'VEHICLE APPROACHING - Wait',
                            'color': (0, 0, 255)
                        }
        
        # All checks passed
        return {
            'safe': True,
            'reason': 'SAFE TO CROSS - Green light, no moving vehicles',
            'color': (0, 255, 0)
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def determine_position(cx, frame_width):
    """Determine if object is on left, center, or right"""
    third = frame_width // 3
    if cx < third:
        return 'LEFT'
    elif cx < 2 * third:
        return 'CENTER'
    else:
        return 'RIGHT'

def estimate_distance(bbox_height, frame_height):
    """Estimate distance based on bounding box size"""
    height_ratio = bbox_height / frame_height
    if height_ratio > 0.5:
        return 'VERY CLOSE'
    elif height_ratio > 0.25:
        return 'NEAR'
    else:
        return 'FAR'

def draw_label_with_background(img, text, position, color, font_scale=0.6, thickness=2):
    """Draw text with background for better visibility"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    x, y = position
    
    # Draw background rectangle
    cv2.rectangle(img, 
                  (x, y - text_height - 5),
                  (x + text_width + 5, y + baseline),
                  (0, 0, 0),
                  -1)
    
    # Draw text
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)

def draw_tracking_trail(img, positions, color):
    """Draw motion trail for tracked vehicles"""
    if len(positions) < 2:
        return
    
    points = [pos['center'] for pos in positions]
    
    for i in range(len(points) - 1):
        # Draw line between consecutive points
        cv2.line(img, points[i], points[i + 1], color, 2)
        
        # Draw small circle at each point
        alpha = (i + 1) / len(points)  # Fade effect
        radius = int(3 + alpha * 3)
        cv2.circle(img, points[i], radius, color, -1)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    print("=" * 70)
    print("Smart Assistive Navigation System - Visual Demo")
    print("=" * 70)
    print()
    
    # Load YOLO model
    print(f"Loading YOLOv8 model: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return
    
    # Initialize camera
    print(f"Opening camera (index: {CAMERA_INDEX})")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("✗ Failed to open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)
    
    print("✓ Camera opened successfully")
    print()
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save screenshot")
    print("  - Press 'c' to toggle crossing analysis")
    print()
    
    # Initialize trackers
    vehicle_tracker = VehicleTracker()
    crossing_analyzer = CrossingSafetyAnalyzer()
    
    # Stats
    frame_count = 0
    fps = 0
    fps_start_time = time.time()
    show_crossing_analysis = True
    
    # Create window
    cv2.namedWindow('Smart Navigation Demo', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Smart Navigation Demo', DISPLAY_WIDTH, DISPLAY_HEIGHT)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame")
            break
        
        frame_count += 1
        display_frame = frame.copy()
        h, w = display_frame.shape[:2]
        
        # Run YOLO detection
        results = model(frame, verbose=False)[0]
        
        # Process detections
        all_detections = []
        vehicle_detections = []
        detection_counts = defaultdict(int)
        
        for box in results.boxes:
            confidence = float(box.conf[0])
            
            if confidence < CONFIDENCE_THRESHOLD:
                continue
            
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            bbox_height = y2 - y1
            
            detection = {
                'class': class_name,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2],
                'center': (cx, cy),
                'position': determine_position(cx, w),
                'distance': estimate_distance(bbox_height, h)
            }
            
            all_detections.append(detection)
            detection_counts[class_name] += 1
            
            # Collect vehicle detections for tracking
            if class_name == 'vehicle':
                vehicle_detections.append(detection)
        
        # Update vehicle tracking
        tracks = vehicle_tracker.update(vehicle_detections)
        
        # Draw vehicle tracking trails
        for track_id, positions in tracks.items():
            if len(positions) >= 2:
                color = vehicle_tracker.track_colors.get(track_id, (255, 0, 0))
                draw_tracking_trail(display_frame, positions, color)
        
        # Draw all detections
        for det in all_detections:
            class_name = det['class']
            x1, y1, x2, y2 = det['bbox']
            cx, cy = det['center']
            
            # Get color
            color = COLORS.get(class_name, COLORS['default'])
            
            # Special handling for currency (lighter color)
            if class_name in CURRENCY_CLASSES:
                color = (200, 200, 200)
            
            # Draw bounding box
            thickness = 3 if class_name == 'vehicle' else 2
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Draw center point
            cv2.circle(display_frame, (cx, cy), 5, color, -1)
            
            # Prepare label
            label_parts = [
                class_name.upper(),
                f"{det['confidence']:.2f}",
                det['position'],
                det['distance']
            ]
            
            # Add motion info for vehicles
            if class_name == 'vehicle':
                for track_id, positions in tracks.items():
                    if len(positions) > 0 and positions[-1]['center'] == (cx, cy):
                        motion = vehicle_tracker.get_motion_info(track_id)
                        if motion:
                            label_parts.append(f"[{motion['direction'].upper()}]")
                        break
            
            label = " | ".join(label_parts)
            
            # Draw label
            draw_label_with_background(
                display_frame,
                label,
                (x1, y1 - 10),
                color,
                font_scale=0.5,
                thickness=2
            )
        
        # Analyze crossing safety
        crossing_status = None
        if show_crossing_analysis:
            crossing_status = crossing_analyzer.analyze(all_detections, tracks)
        
        # Draw info panel
        panel_height = 200
        panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
        
        y_offset = 25
        
        # Title
        cv2.putText(panel, "SMART ASSISTIVE NAVIGATION SYSTEM", 
                    (10, y_offset), cv2.FONT_HERSHEY_BOLD, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        # FPS
        if frame_count % 30 == 0:
            elapsed = time.time() - fps_start_time
            fps = 30 / elapsed if elapsed > 0 else 0
            fps_start_time = time.time()
        
        cv2.putText(panel, f"FPS: {fps:.1f} | Detections: {len(all_detections)} | Frame: {frame_count}",
                    (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 25
        
        # Detection summary
        if detection_counts:
            summary = " | ".join([f"{cls}: {cnt}" for cls, cnt in detection_counts.items()])
            cv2.putText(panel, f"Objects: {summary}",
                        (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        else:
            cv2.putText(panel, "No objects detected",
                        (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        y_offset += 30
        
        # Crossing safety status
        if crossing_status:
            cv2.putText(panel, f"CROSSING STATUS: {crossing_status['reason']}",
                        (10, y_offset), cv2.FONT_HERSHEY_BOLD, 0.6, 
                        crossing_status['color'], 2)
            y_offset += 30
            
            # Draw large status indicator
            status_text = "SAFE" if crossing_status['safe'] else "WAIT"
            cv2.putText(panel, status_text,
                        (10, y_offset + 30), cv2.FONT_HERSHEY_BOLD, 1.5,
                        crossing_status['color'], 3)
        
        # Vehicle tracking info
        if tracks:
            active_tracks = len(tracks)
            moving_vehicles = sum(1 for tid in tracks.keys() 
                                 if vehicle_tracker.get_motion_info(tid) and 
                                 vehicle_tracker.get_motion_info(tid)['is_moving'])
            
            cv2.putText(panel, f"Tracked Vehicles: {active_tracks} | Moving: {moving_vehicles}",
                        (10, panel_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Combine frame and panel
        combined = np.vstack([display_frame, panel])
        
        # Display
        cv2.imshow('Smart Navigation Demo', combined)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            filename = f"screenshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, combined)
            print(f"Screenshot saved: {filename}")
        elif key == ord('c'):
            show_crossing_analysis = not show_crossing_analysis
            status = "enabled" if show_crossing_analysis else "disabled"
            print(f"Crossing analysis {status}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\nDemo complete!")
    print(f"Total frames processed: {frame_count}")
    print(f"Average FPS: {fps:.1f}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()