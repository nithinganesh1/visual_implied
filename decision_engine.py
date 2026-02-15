#!/usr/bin/env python3
"""
Decision Engine Module
Handles scene analysis and crossing safety logic
"""

from utils import logger

class DecisionEngine:
    """Analyzes detections and makes navigation decisions"""
    
    def __init__(self, audio_manager):
        """
        Initialize decision engine
        
        Args:
            audio_manager: Audio manager instance for speech output
        """
        self.audio = audio_manager
    
    def analyze_scene(self, detections):
        """
        Analyze scene detections and provide verbal summary
        
        Args:
            detections: List of detection dictionaries
        
        Returns:
            Summary string (also speaks via audio manager)
        """
        if not detections:
            return "No significant objects detected"
        
        # Group detections by type
        objects_by_type = {}
        for det in detections:
            class_name = det['class']
            if class_name not in objects_by_type:
                objects_by_type[class_name] = []
            objects_by_type[class_name].append(det)
        
        # Build priority-based announcements
        announcements = []
        
        # 1. Moving vehicles (highest priority)
        if 'vehicle' in objects_by_type:
            for vehicle in objects_by_type['vehicle']:
                location = vehicle['location']
                distance = vehicle['distance']
                announcement = f"Vehicle {distance} on {location}"
                announcements.append(announcement)
                self.audio.speak_with_priority(announcement, priority=1, obj_type='vehicle')
        
        # 2. Red pedestrian light
        if 'red_pedestrian_light' in objects_by_type:
            light = objects_by_type['red_pedestrian_light'][0]
            announcement = "Red pedestrian light detected"
            announcements.append(announcement)
            self.audio.speak_with_priority(announcement, priority=2, obj_type='red_light')
        
        # 3. Green pedestrian light (if no red)
        elif 'green_pedestrian_light' in objects_by_type:
            light = objects_by_type['green_pedestrian_light'][0]
            announcement = "Green pedestrian light detected"
            announcements.append(announcement)
            self.audio.speak_with_priority(announcement, priority=3, obj_type='green_light')
        
        # 4. Zebra crossing
        if 'zebra' in objects_by_type:
            zebra = objects_by_type['zebra'][0]
            location = zebra['location']
            distance = zebra['distance']
            announcement = f"Zebra crossing {distance} in {location}"
            announcements.append(announcement)
            self.audio.speak_with_priority(announcement, priority=4, obj_type='zebra')
        
        # 5. Obstacles
        obstacle_types = ['bench', 'stair', 'Toilet']
        for obstacle_type in obstacle_types:
            if obstacle_type in objects_by_type:
                obstacle = objects_by_type[obstacle_type][0]
                location = obstacle['location']
                distance = obstacle['distance']
                
                # Use friendlier names
                friendly_name = {
                    'Toilet': 'restroom',
                    'bench': 'bench',
                    'stair': 'stairs'
                }.get(obstacle_type, obstacle_type)
                
                announcement = f"{friendly_name.capitalize()} {distance} on {location}"
                announcements.append(announcement)
                self.audio.speak_with_priority(announcement, priority=5, obj_type=obstacle_type)
        
        return ". ".join(announcements)
    
    def check_crossing_safety(self, detector, num_frames=5, interval=0.2):
        """
        Check if it's safe to cross zebra crossing
        
        Logic:
        1. Must detect zebra crossing
        2. Must detect green pedestrian light (no red)
        3. Must not detect vehicles moving toward crossing
        
        Args:
            detector: ObjectDetector instance
            num_frames: Number of frames to analyze for vehicle motion
            interval: Time between frames
        
        Returns:
            Tuple (is_safe: bool, reason: str)
        """
        logger.info("Starting crossing safety analysis...")
        
        # Capture multiple frames for motion detection
        detections_over_time = detector.detect_continuous(
            num_frames=num_frames,
            interval=interval
        )
        
        # Analyze latest frame for static conditions
        latest_detections = detections_over_time[-1] if detections_over_time else []
        
        # Check 1: Zebra crossing must be present
        zebra_detected = any(d['class'] == 'zebra' for d in latest_detections)
        if not zebra_detected:
            return False, "No zebra crossing detected"
        
        # Check 2: Green light must be present (no red light)
        red_light_detected = any(d['class'] == 'red_pedestrian_light' for d in latest_detections)
        green_light_detected = any(d['class'] == 'green_pedestrian_light' for d in latest_detections)
        
        if red_light_detected:
            return False, "Red pedestrian light detected"
        
        if not green_light_detected:
            return False, "No green pedestrian light detected"
        
        # Check 3: No vehicles moving toward crossing
        moving_vehicles = detector.detect_vehicle_movement(detections_over_time)
        
        if moving_vehicles:
            # Check if any vehicle is near the zebra crossing
            zebra_detections = [d for d in latest_detections if d['class'] == 'zebra']
            if zebra_detections:
                zebra_center = zebra_detections[0]['center']
                
                for mv in moving_vehicles:
                    vehicle_center = mv['detection']['center']
                    
                    # Check if vehicle is in same horizontal region as zebra
                    horizontal_distance = abs(vehicle_center[0] - zebra_center[0])
                    
                    if horizontal_distance < 200:  # Within crossing area
                        return False, "Vehicle approaching crossing"
        
        # All checks passed
        return True, "Green light and no approaching vehicles"
    
    def get_obstacle_warnings(self, detections):
        """
        Get list of obstacle warnings for navigation
        
        Args:
            detections: List of detection dictionaries
        
        Returns:
            List of warning strings
        """
        warnings = []
        
        obstacle_classes = ['bench', 'stair', 'Toilet']
        
        for det in detections:
            if det['class'] in obstacle_classes:
                class_name = det['class']
                location = det['location']
                distance = det['distance']
                
                friendly_name = {
                    'Toilet': 'restroom',
                    'bench': 'bench',
                    'stair': 'stairs'
                }.get(class_name, class_name)
                
                if distance == 'very close':
                    warning = f"Warning: {friendly_name} very close on {location}"
                    warnings.append(warning)
        
        return warnings
    
    def should_wait_at_crossing(self, detections):
        """
        Quick check if user should wait before crossing
        
        Args:
            detections: List of current detections
        
        Returns:
            Tuple (should_wait: bool, reason: str)
        """
        # Check for red light
        if any(d['class'] == 'red_pedestrian_light' for d in detections):
            return True, "Red light"
        
        # Check for nearby vehicles
        vehicles = [d for d in detections if d['class'] == 'vehicle']
        for vehicle in vehicles:
            if vehicle['distance'] in ['very close', 'near']:
                return True, "Vehicle nearby"
        
        return False, "Clear"
