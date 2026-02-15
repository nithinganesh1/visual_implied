# Quick Start Guide

Get your Smart Assistive Navigation System up and running in 5 steps!

## Step 1: Install Dependencies

```bash
chmod +x install.sh
./install.sh
```

This will:
- Update system packages
- Install espeak, OpenCV, and other dependencies
- Install Python packages from requirements.txt
- Set up GPIO and serial port permissions

**⚠️ REBOOT REQUIRED after installation for permissions to take effect:**

```bash
sudo reboot
```

## Step 2: Add Your YOLO Model

Place your trained YOLO model in the project directory:

```bash
cp /path/to/your/best.pt .
```

The model should detect these 14 classes:
- vehicle, Toilet, bench, green_pedestrian_light, red_pedestrian_light, stair, zebra
- 10, 100, 20, 200, 2000, 50, 500

## Step 3: Configure Emergency Contact

Edit `config.py` and update the emergency phone number:

```python
EMERGENCY_PHONE_NUMBER = "+1234567890"  # Replace with your number
```

## Step 4: Test the System

Run the component test to verify everything is working:

```bash
python3 test_system.py
```

This will test:
- ✓ Dependencies
- ✓ Module imports
- ✓ Audio system
- ✓ Mock modules
- ✓ Utilities

## Step 5: Run the System

### With Real Hardware

Connect your hardware:
- Camera → USB port
- Button → GPIO 17 (or configured pin)
- GPS → /dev/ttyUSB0
- GSM → /dev/serial0

Then run:

```bash
python3 main.py
```

### Without Hardware (Testing Mode)

Edit `config.py`:

```python
USE_MOCK_GPS = True
USE_MOCK_GSM = True
```

Then run:

```bash
python3 main.py
```

**Note**: You'll still need a camera for object detection. For camera-less testing, comment out camera initialization in `detector.py`.

## Button Controls

Once running:

**Single Press** → Scan scene once and announce objects

**Double Press** → Confirm crossing safety check (after zebra detected)

**Triple Press** → Send emergency SMS with GPS location

## What You Should Hear

### Normal Scan:
```
"Scanning"
"Vehicle near on left"
"Zebra crossing far in center"
```

### Zebra Detection:
```
"Zebra crossing detected. Do you want to check if it is safe to cross?"
[Double press within 3 seconds]
"Checking crossing safety"
"Safe to cross. Green light and no approaching vehicles"
```

### Emergency Alert:
```
[Triple press]
"Sending emergency alert"
"Emergency alert sent successfully"
```

## Troubleshooting

### "Camera not found"
```bash
ls /dev/video*
# Should show /dev/video0 or similar
```

### "Permission denied" for GPIO
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### "espeak not found"
```bash
sudo apt-get install espeak
```

### GPS not getting fix
- Move outdoors with clear sky view
- Wait 1-2 minutes for initial GPS lock
- Check GPS LED (should blink when locked)

### GSM not sending SMS
- Verify SIM card is inserted
- Check signal strength LED
- Test with: `screen /dev/serial0 9600`
- Type `AT` and press Enter (should reply "OK")

## Hardware Wiring

### Button (Single Button Mode)

```
GPIO 17 ----[Button]---- GND
```

Use internal pull-up (configured in code).

### Button (Two Button Mode)

```
GPIO 17 ----[Scan Button]---- GND
GPIO 27 ----[Emergency Button]---- GND
```

### GPS Module

```
GPS TX → Pi RX (USB Serial Adapter)
GPS RX → Pi TX
GPS GND → Pi GND
GPS VCC → Pi 3.3V or 5V (check module specs)
```

### GSM Module

```
GSM TX → Pi RX (/dev/serial0)
GSM RX → Pi TX
GSM GND → Pi GND
GSM VCC → Pi 5V or external power
```

## Configuration Options

### Single vs Two-Button Mode

**Default**: Single button with press counting

**Two-button mode**: Edit `main.py`:

```python
# Replace
from button_handler import ButtonHandler

# With
from button_handler import TwoButtonHandler as ButtonHandler
```

### Adjust Detection Sensitivity

In `config.py`:

```python
CONFIDENCE_THRESHOLD = 0.6  # Lower = more detections, Higher = fewer false positives
```

### Change Audio Cooldown

In `config.py`:

```python
AUDIO_COOLDOWN_SECONDS = 3  # Prevent repetitive announcements
```

### Camera Resolution

In `config.py`:

```python
CAMERA_WIDTH = 640   # Lower for speed
CAMERA_HEIGHT = 480  # Higher for accuracy
```

## Performance Tips

**For Faster Processing:**
- Use 320x240 camera resolution
- Increase confidence threshold to 0.7
- Reduce crossing analysis frames to 3

**For Better Accuracy:**
- Use 1280x720 camera resolution
- Lower confidence threshold to 0.5
- Increase crossing analysis frames to 7

## Next Steps

✓ System is running  
✓ Tested with button presses  
✓ Emergency SMS working  
✓ GPS getting location  

**Now you can:**
1. Fine-tune detection thresholds
2. Customize audio messages
3. Add additional object classes
4. Implement additional safety features

## Getting Help

Check the full README.md for:
- Detailed architecture explanation
- Module documentation
- Advanced configuration
- Safety considerations

---

**Ready to Go!** Press the button and start navigating safely. 🚶‍♂️
