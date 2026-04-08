# Smart Assistive Navigation System for Visually Impaired Users

A production-ready, modular navigation system built for Raspberry Pi 5 using YOLOv8 object detection, GPS tracking, and GSM emergency alerts.

## Features

- **Real-time Object Detection**: Custom YOLOv8n model detecting 14 classes including vehicles, pedestrian lights, zebra crossings, and obstacles
- **Intelligent Button Control**: Single/double/triple press detection using gpiozero
- **Crossing Safety Analysis**: Multi-frame vehicle motion detection to determine crossing safety
- **GPS Location Tracking**: Continuous GPS parsing for emergency location reporting
- **Emergency SMS Alerts**: GSM-based SMS with GPS coordinates and Google Maps link
- **Offline Text-to-Speech**: Priority-based audio feedback with cooldown management
- **Optimized Performance**: Designed specifically for Raspberry Pi 5

## Hardware Requirements

- Raspberry Pi 5
- USB Camera
- Push button(s) connected via GPIO
- GSM Module (UART/USB)
- GPS Module (UART/USB)
- Speaker for audio output

## Detection Classes

The system detects the following objects:

**Navigation Objects:**
- vehicle
- Toilet (restroom)
- bench
- green_pedestrian_light
- red_pedestrian_light
- stair
- zebra (crossing)

**Currency Classes (ignored for navigation):**
- 10, 20, 50, 100, 200, 500, 2000

## System Architecture

```
main.py                 # Main orchestrator
├── detector.py         # YOLO object detection
├── button_handler.py   # GPIO button management
├── decision_engine.py  # Scene analysis and crossing safety
├── audio_manager.py    # TTS with priority queue
├── gps_module.py       # GPS parsing and location
├── gsm_module.py       # SMS emergency alerts
└── utils.py            # Logging and utilities
```

## Installation

### 1. System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y espeak python3-pip python3-opencv
sudo apt-get install -y libatlas-base-dev libopenblas-dev
```

### 2. Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Model File

Place your custom YOLO model `best.pt` in the project root directory.

### 4. GPIO Setup

Default pin configuration:
- **Primary Button**: GPIO 17
- **Emergency Button** (optional): GPIO 27

Modify in `main.py` if using different pins.

### 5. Serial Ports

Default configuration:
- **GPS Module**: `/dev/ttyUSB0` @ 9600 baud
- **GSM Module**: `/dev/serial0` @ 9600 baud

Modify in respective module files if needed.

### 6. Emergency Contact

Edit the phone number in `main.py`:

```python
self.gsm = GSMModule(phone_number="+916282670289")
```

## Usage

### Running the System

```bash
python3 main.py
```

### Button Controls

**Single Press:**
- Performs one-time scene scan
- Announces detected objects with priority:
  1. Vehicles (with location and distance)
  2. Red/Green pedestrian lights
  3. Zebra crossings
  4. Obstacles (stairs, benches, restrooms)

**Double Press (within 0.5 seconds):**
- Confirms crossing safety check (only after zebra detection)
- System analyzes:
  - Presence of green light
  - Absence of red light
  - No approaching vehicles
- Speaks result: "Safe to cross" or "Not safe to cross"

**Triple Press (within 0.8 seconds) OR Emergency Button:**
- Sends emergency SMS with GPS location
- Includes Google Maps link
- Speaks confirmation

## Configuration Options

### Single vs Two-Button Mode

**Single Button Mode** (default in `main.py`):
- Uses press counting: single/double/triple

**Two Button Mode** (alternative in `button_handler.py`):
- Button 1: Scan/Confirm
- Button 2: Emergency

To use two-button mode, modify `main.py` to import and use `TwoButtonHandler` instead of `ButtonHandler`.

### Audio Settings

In `audio_manager.py`:

```python
self.cooldown_seconds = 3  # Cooldown per object type
```

Adjust cooldown to prevent repetitive announcements.

### Detection Confidence

In `detector.py`:

```python
self.confidence_threshold = 0.6  # Minimum confidence for detections
```

Lower for more detections, raise for higher precision.

### Camera Resolution

In `detector.py`:

```python
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

Adjust for performance vs quality trade-off.

## Crossing Safety Logic

The system determines crossing safety using:

1. **Zebra Crossing Present**: Must detect zebra marking
2. **Green Light Active**: Must detect green pedestrian light
3. **No Red Light**: Must not detect red pedestrian light
4. **No Approaching Vehicles**: Analyzes 5 frames over 1 second to detect vehicle motion toward crossing

Vehicle motion is detected by tracking bounding box Y-coordinate changes across frames. Vehicles moving downward (toward user) are flagged as approaching.

## Spatial Awareness

The camera frame is divided into three zones:

- **Left**: Objects in left third of frame
- **Center**: Objects in center third
- **Right**: Objects in right third

Announcements include directional information:
- "Vehicle on left"
- "Obstacle ahead in center"
- "Stairs on right"

## Distance Estimation

Distance categories based on bounding box height:

- **Very Close**: Box height > 40% of frame height
- **Near**: Box height 15-40% of frame height
- **Far**: Box height < 15% of frame height

## Testing Without Hardware

The system includes mock modules for testing:

### Mock GPS

Replace in `main.py`:

```python
from gps_module import MockGPSModule as GPSModule
```

### Mock GSM

Replace in `main.py`:

```python
from gsm_module import MockGSMModule as GSMModule
```

Mock modules simulate functionality without requiring actual hardware.

## Logging

Logs are written to:
- **Console**: INFO level and above
- **File**: `navigation_system.log` (all levels)

Adjust logging level in `utils.py`:

```python
logger = setup_logger(
    name='NavigationSystem',
    level=logging.DEBUG,  # Change to DEBUG for verbose logs
    log_file='navigation_system.log'
)
```

## Troubleshooting

### Camera Not Opening

```bash
# Check camera detection
ls /dev/video*

# Test camera
raspistill -o test.jpg
```

### GPIO Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot required
sudo reboot
```

### espeak Not Found

```bash
sudo apt-get install espeak
```

### Serial Port Access Denied

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot required
sudo reboot
```

### GPS Not Getting Fix

- Ensure GPS module has clear view of sky
- Wait 1-2 minutes for initial fix
- Check GPS LED indicator (should blink when fix acquired)

### GSM SMS Not Sending

- Verify SIM card is inserted and activated
- Check GSM signal strength (LED should blink)
- Ensure correct serial port configuration
- Test with AT commands manually:

```bash
screen /dev/serial0 9600
# Type: AT
# Should respond: OK
```

## Performance Optimization

### For Better Speed

1. **Reduce Camera Resolution**:
   ```python
   self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
   self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
   ```

2. **Increase Confidence Threshold**:
   ```python
   self.confidence_threshold = 0.7
   ```

3. **Use Smaller YOLO Model**: Ensure `best.pt` is YOLOv8n (nano)

### For Better Accuracy

1. **Increase Camera Resolution**:
   ```python
   self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
   self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
   ```

2. **Lower Confidence Threshold**:
   ```python
   self.confidence_threshold = 0.5
   ```

3. **More Frames for Motion Detection**:
   ```python
   detections_over_time = detector.detect_continuous(
       num_frames=10,
       interval=0.15
   )
   ```

## Safety Considerations

- **Always supervise the system**: This is an assistive tool, not a replacement for human judgment
- **Test thoroughly** in controlled environments before real-world use
- **Verify GPS accuracy** regularly
- **Keep emergency contacts updated**
- **Ensure adequate lighting** for camera-based detection
- **Regular battery checks** for portable deployment

## License

This project is intended for educational and assistive technology purposes.

## Contributing

Contributions are welcome! Areas for improvement:

- Enhanced vehicle trajectory prediction
- Support for additional object classes
- Multi-camera support
- Cloud backup of GPS tracks
- Voice command integration
- Haptic feedback support

## Contact

For issues or questions, refer to project documentation.

---

**Version**: 1.0  
**Platform**: Raspberry Pi 5  
**Python**: 3.9+  
**Last Updated**: 2025
# visual_implied
# visual_implied
