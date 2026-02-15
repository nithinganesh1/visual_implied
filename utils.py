#!/usr/bin/env python3
"""
Utility Functions and Logging Configuration
"""

import logging
import sys
from datetime import datetime

def setup_logger(name='NavigationSystem', level=logging.INFO, log_file=None):
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
    
    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    return logger

# Global logger instance
logger = setup_logger(
    name='NavigationSystem',
    level=logging.INFO,
    log_file='navigation_system.log'
)


def format_timestamp():
    """Get formatted timestamp string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: Tuple (x1, y1)
        point2: Tuple (x2, y2)
    
    Returns:
        float: Distance
    """
    import math
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def get_bounding_box_area(bbox):
    """
    Calculate area of bounding box
    
    Args:
        bbox: Tuple (x1, y1, x2, y2)
    
    Returns:
        float: Area in pixels
    """
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def bboxes_overlap(bbox1, bbox2):
    """
    Check if two bounding boxes overlap
    
    Args:
        bbox1: Tuple (x1, y1, x2, y2)
        bbox2: Tuple (x1, y1, x2, y2)
    
    Returns:
        bool: True if boxes overlap
    """
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # Check if one box is to the left of the other
    if x2_1 < x1_2 or x2_2 < x1_1:
        return False
    
    # Check if one box is above the other
    if y2_1 < y1_2 or y2_2 < y1_1:
        return False
    
    return True


def get_horizontal_overlap(bbox1, bbox2):
    """
    Calculate horizontal overlap between two boxes
    
    Args:
        bbox1: Tuple (x1, y1, x2, y2)
        bbox2: Tuple (x1, y1, x2, y2)
    
    Returns:
        float: Horizontal overlap distance (0 if no overlap)
    """
    x1_1, _, x2_1, _ = bbox1
    x1_2, _, x2_2, _ = bbox2
    
    overlap_start = max(x1_1, x1_2)
    overlap_end = min(x2_1, x2_2)
    
    if overlap_start < overlap_end:
        return overlap_end - overlap_start
    
    return 0


def retry_on_failure(func, max_attempts=3, delay=1):
    """
    Retry a function on failure
    
    Args:
        func: Function to call
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
    
    Returns:
        Function result or None if all attempts fail
    """
    import time
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    
    return None


class RateLimiter:
    """Simple rate limiter for function calls"""
    
    def __init__(self, max_calls, time_window):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def is_allowed(self):
        """
        Check if call is allowed under rate limit
        
        Returns:
            bool: True if call is allowed
        """
        import time
        
        current_time = time.time()
        
        # Remove old calls outside time window
        self.calls = [t for t in self.calls if current_time - t < self.time_window]
        
        # Check if under limit
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        
        return False


class MovingAverage:
    """Calculate moving average for smoothing values"""
    
    def __init__(self, window_size=5):
        """
        Initialize moving average
        
        Args:
            window_size: Number of values to average
        """
        self.window_size = window_size
        self.values = []
    
    def add(self, value):
        """Add new value and return current average"""
        self.values.append(value)
        
        # Keep only last window_size values
        if len(self.values) > self.window_size:
            self.values.pop(0)
        
        return self.get_average()
    
    def get_average(self):
        """Get current average"""
        if not self.values:
            return 0
        
        return sum(self.values) / len(self.values)
    
    def reset(self):
        """Reset the moving average"""
        self.values = []


def validate_detection(detection, min_confidence=0.5, min_size=100):
    """
    Validate detection meets minimum criteria
    
    Args:
        detection: Detection dictionary
        min_confidence: Minimum confidence threshold
        min_size: Minimum bounding box area
    
    Returns:
        bool: True if detection is valid
    """
    # Check confidence
    if detection.get('confidence', 0) < min_confidence:
        return False
    
    # Check size
    bbox = detection.get('bbox')
    if bbox:
        area = get_bounding_box_area(bbox)
        if area < min_size:
            return False
    
    return True
