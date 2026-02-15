#!/usr/bin/env python3
"""
Configuration File
Centralized settings for the Navigation System
"""

# ============================================================================
# HARDWARE CONFIGURATION
# ============================================================================

# GPIO Pin Assignments (BCM numbering)
PRIMARY_BUTTON_PIN = 17
EMERGENCY_BUTTON_PIN = 27  # Set to None for single-button mode

# Serial Port Configuration
GPS_SERIAL_PORT = '/dev/ttyUSB0'
GPS_BAUDRATE = 9600

GSM_SERIAL_PORT = '/dev/serial0'
GSM_BAUDRATE = 9600

# Camera Configuration
CAMERA_INDEX = 0  # USB camera index
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ============================================================================
# EMERGENCY CONTACT
# ============================================================================

EMERGENCY_PHONE_NUMBER = "+916282670289"  # UPDATE THIS!

# ============================================================================
# DETECTION CONFIGURATION
# ============================================================================

# YOLO Model
YOLO_MODEL_PATH = "best.pt"
CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for detections

# Detection Classes
DETECTION_CLASSES = [
    'vehicle', 'Toilet', 'bench', 'green_pedestrian_light',
    'red_pedestrian_light', 'stair', 'zebra', '10', '100', '20',
    '200', '2000', '50', '500'
]

# Currency classes to ignore for navigation
CURRENCY_CLASSES = ['10', '100', '20', '200', '2000', '50', '500']

# Priority order for announcements (highest to lowest)
PRIORITY_ORDER = [
    'vehicle',
    'red_pedestrian_light',
    'zebra',
    'bench',
    'stair',
    'Toilet',
    'green_pedestrian_light'
]

# ============================================================================
# BUTTON TIMING CONFIGURATION
# ============================================================================

BUTTON_BOUNCE_TIME = 0.05  # Debounce time in seconds
DOUBLE_PRESS_WINDOW = 0.5  # Time window for double press detection
TRIPLE_PRESS_WINDOW = 0.8  # Time window for triple press detection
CONFIRMATION_TIMEOUT = 3.0  # Timeout for crossing confirmation

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

AUDIO_COOLDOWN_SECONDS = 3  # Cooldown per object type
TTS_ENGINE = 'espeak'  # 'espeak' or 'pyttsx3'
ESPEAK_SPEED = 150  # Words per minute
ESPEAK_AMPLITUDE = 200  # Volume (0-200)

# ============================================================================
# CROSSING SAFETY CONFIGURATION
# ============================================================================

# Number of frames to analyze for vehicle motion detection
CROSSING_ANALYSIS_FRAMES = 5

# Time interval between frames (seconds)
CROSSING_FRAME_INTERVAL = 0.2

# Vehicle motion threshold (pixels)
VEHICLE_MOTION_THRESHOLD = 20

# Vehicle proximity threshold for crossing area (pixels)
VEHICLE_CROSSING_PROXIMITY = 200

# ============================================================================
# DISTANCE ESTIMATION THRESHOLDS
# ============================================================================

# Based on bounding box height ratio to frame height
DISTANCE_VERY_CLOSE_THRESHOLD = 0.4  # > 40% of frame
DISTANCE_NEAR_THRESHOLD = 0.15       # 15-40% of frame
# < 15% is considered FAR

# ============================================================================
# SPATIAL AWARENESS CONFIGURATION
# ============================================================================

# Frame is divided into thirds for left/center/right detection
# No configuration needed - handled automatically

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'navigation_system.log'
LOG_TO_CONSOLE = True
LOG_TO_FILE = True

# ============================================================================
# TESTING/DEVELOPMENT MODE
# ============================================================================

# Set to True to use mock modules (for testing without hardware)
USE_MOCK_GPS = False
USE_MOCK_GSM = False

# Enable verbose debug output
DEBUG_MODE = False

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# GPS Settings
GPS_TIMEOUT = 1
GPS_DATA_STALE_THRESHOLD = 10  # Seconds before GPS data considered stale

# GSM Settings
GSM_TIMEOUT = 5
GSM_MAX_RETRY_ATTEMPTS = 2

# Detection Settings
MIN_DETECTION_SIZE = 100  # Minimum bounding box area (pixels)
MAX_DETECTIONS_PER_FRAME = 20  # Limit detections for performance

# Memory Management
FRAME_BUFFER_SIZE = 10  # Number of frames to keep in memory

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_CROSSING_SAFETY_CHECK = True
ENABLE_EMERGENCY_ALERTS = True
ENABLE_SPATIAL_AWARENESS = True
ENABLE_DISTANCE_ESTIMATION = True
ENABLE_VEHICLE_MOTION_TRACKING = True
