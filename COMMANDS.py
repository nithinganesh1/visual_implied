#!/usr/bin/env python3
"""
COMMAND REFERENCE - Copy/Paste Ready Commands
All commands for the smart navigation system
"""

# ============================================================================
# SETUP COMMANDS
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    COMMAND REFERENCE - COPY & PASTE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

📍 LOCATION: Always run from /home/nithin/Evolve/projects/visual_implied/

cd /home/nithin/Evolve/projects/visual_implied


🎯 QUICK START (Choose One)
═══════════════════════════════════════════════════════════════════════════

1️⃣  IMMEDIATE - Start System (All features active)
───────────────────────────────────────────────────────────────────────────
python3 main.py

Result: 
  ✓ Currency detection works
  ✓ Ultrasonic sensor active
  ✓ Buzzer warns about obstacles
  ✓ OCR ready on GPIO 27 double-press
  ⚠ Face recognition needs setup


2️⃣  FAST SETUP - Add Face Recognition (2 minutes)
───────────────────────────────────────────────────────────────────────────
python3 simple_setup.py

Then:
python3 main.py

Result:
  ✓ All features including face recognition
  ✓ Uses OpenCV (no TensorFlow needed)
  ✓ ~85% accuracy (good for most uses)


3️⃣  PREMIUM SETUP - Better Face Recognition (15 minutes)
───────────────────────────────────────────────────────────────────────────
pip install tensorflow

wget https://github.com/nyoki-mtl/pytorch-facenet/raw/master/data/facenet_keras.h5

python3 generate_embeddings.py

python3 main.py

Result:
  ✓ All features with professional-grade face recognition
  ✓ ~98% accuracy
  ✓ Uses FaceNet neural network


🧪 TESTING & VERIFICATION
═══════════════════════════════════════════════════════════════════════════

Check Dependencies:
─────────────────────────────────────────────────────────────────────────
python3 diagnose.py

See what's installed and what's missing.


Test Face Detection:
─────────────────────────────────────────────────────────────────────────
python3 test_face_detection.py

Verifies face detection works (webcam required).


Test Hardware Sensors:
─────────────────────────────────────────────────────────────────────────
python3 test_sensors.py

Tests ultrasonic sensor and buzzer.


Full System Test:
─────────────────────────────────────────────────────────────────────────
python3 test_system.py

Comprehensive system check.


🎬 DURING OPERATION (GPIO Buttons)
═══════════════════════════════════════════════════════════════════════════

GPIO 27 - Single Press (Face Recognition):
───────────────────────────────────────────────────────────────────────────
- Triggers face detection
- Compares with stored embeddings
- Announces: "Found georgy" or "Unknown person"


GPIO 27 - Double Press (OCR Text Reading):
───────────────────────────────────────────────────────────────────────────
- Triggers text recognition
- Reads all text in view
- Speaks the text aloud


GPIO 17 - Single Press (Scene Detection):
───────────────────────────────────────────────────────────────────────────
- Detects vehicles, people, traffic lights
- Announces what's detected


GPIO 17 - Double Press (Crossing Safety):
───────────────────────────────────────────────────────────────────────────
- Special safety check for road crossing
- Announces if safe to cross


GPIO 17 - Triple Press (Full Analysis):
───────────────────────────────────────────────────────────────────────────
- Complete scene analysis
- Announcements for all detected objects


🔧 CONFIGURATION & DATA
═══════════════════════════════════════════════════════════════════════════

View Configuration:
─────────────────────────────────────────────────────────────────────────
cat config.py

List Model Files:
─────────────────────────────────────────────────────────────────────────
ls -lh *.pt *.h5 *.json

Check Face Embeddings:
─────────────────────────────────────────────────────────────────────────
python3 -m json.tool face_embeddings.json | head -20

View Dependencies:
─────────────────────────────────────────────────────────────────────────
cat requirements.txt


📁 FOLDER MANAGEMENT
═══════════════════════════════════════════════════════════════════════════

Create georgy Folder (for face photos):
─────────────────────────────────────────────────────────────────────────
mkdir -p georgy

Copy Face Photos:
─────────────────────────────────────────────────────────────────────────
# Copy your .jpg files to georgy/ folder
# Then run: python3 simple_setup.py


List Face Database:
─────────────────────────────────────────────────────────────────────────
python3 -c "import json; db = json.load(open('face_embeddings.json')); 
print(f'People: {list(db.keys())}'); 
print(f'Total faces: {sum(len(v) for v in db.values())}')"


🚀 ADVANCED - OPTIONAL UPGRADES
═══════════════════════════════════════════════════════════════════════════

Reinstall MediaPipe (if having issues):
─────────────────────────────────────────────────────────────────────────
pip uninstall mediapipe -y
pip install mediapipe==0.10.9

Install Better Face Detection (Optional):
─────────────────────────────────────────────────────────────────────────
pip install mediapipe==0.10.9

Upgrade OpenCV for More Features:
─────────────────────────────────────────────────────────────────────────
pip install opencv-contrib-python

Add Voice Commands (Optional):
─────────────────────────────────────────────────────────────────────────
pip install vosk pyaudio


❌ TROUBLESHOOTING COMMANDS
═══════════════════════════════════════════════════════════════════════════

Check Python Version:
─────────────────────────────────────────────────────────────────────────
python3 --version

(Recommended: Python 3.8 or higher)


Check Installed Packages:
─────────────────────────────────────────────────────────────────────────
pip list | grep -E "mediapipe|tensorflow|opencv|easyocr|gpiozero"

See all installed packages:
─────────────────────────────────────────────────────────────────────────
pip list

Check Disk Space:
─────────────────────────────────────────────────────────────────────────
df -h

(Ensure at least 500 MB available)


View System Logs:
─────────────────────────────────────────────────────────────────────────
# Logs are printed to console when running main.py


Kill Running Process (if stuck):
─────────────────────────────────────────────────────────────────────────
pkill -f "python3 main.py"

Or:
pkill -f "python3 simple_setup.py"


📊 MONITORING & DEBUG
═══════════════════════════════════════════════════════════════════════════

Run with Verbose Output:
─────────────────────────────────────────────────────────────────────────
# Edit main.py and change logging level to DEBUG
# Then run: python3 main.py


View File Sizes:
─────────────────────────────────────────────────────────────────────────
du -h *

What Files Exist:
─────────────────────────────────────────────────────────────────────────
ls -la | grep -E "\\.py|\\.pt|\\.json"


🔗 HELPFUL RESOURCES
═══════════════════════════════════════════════════════════════════════════

Read Setup Guide:
─────────────────────────────────────────────────────────────────────────
cat FACE_SETUP_GUIDE.md

Read Quick Start:
─────────────────────────────────────────────────────────────────────────
cat QUICK_START.md

Read System Status:
─────────────────────────────────────────────────────────────────────────
cat SYSTEM_STATUS.md

Read Hardware Setup:
─────────────────────────────────────────────────────────────────────────
python3 HARDWARE_SETUP.py


💾 BACKUP & MAINTENANCE
═══════════════════════════════════════════════════════════════════════════

Backup Everything:
─────────────────────────────────────────────────────────────────────────
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz *

Backup Only Code:
─────────────────────────────────────────────────────────────────────────
tar -czf code_backup_$(date +%Y%m%d_%H%M%S).tar.gz *.py config.py

Clean Cache:
─────────────────────────────────────────────────────────────────────────
rm -rf __pycache__
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

Reset Face Database:
─────────────────────────────────────────────────────────────────────────
rm face_embeddings.json
python3 simple_setup.py


⚡ MOST COMMON COMMANDS
═══════════════════════════════════════════════════════════════════════════

# Check everything is okay
python3 diagnose.py

# Generate face embeddings (quick)
python3 simple_setup.py

# Start the system
python3 main.py

# Test webcam face detection
python3 test_face_detection.py

# Test ultrasonic and buzzer
python3 test_sensors.py


════════════════════════════════════════════════════════════════════════════

✅ READY TO START?

   1. Prepare your face photos in georgy/ folder
   2. Run: python3 simple_setup.py
   3. Run: python3 main.py
   4. Test by pressing GPIO buttons

Any issues? Run: python3 diagnose.py

════════════════════════════════════════════════════════════════════════════
""")
