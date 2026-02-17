#!/usr/bin/env python3
"""
QUICK REFERENCE - Face Recognition System
"""

QUICK_REF = """
╔════════════════════════════════════════════════════════════════════╗
║         QUICK REFERENCE - FACE RECOGNITION SYSTEM                 ║
╚════════════════════════════════════════════════════════════════════╝

🔴 SETUP (RUN ONCE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. pip install -r requirements.txt
2. mkdir ~/visual_implied/georgy
3. Copy face images to georgy/
4. python3 generate_embeddings.py
5. [Optional] Delete georgy/ to save space


🟢 DAILY USE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python3 main.py


🟡 GPIO 27 BUTTON USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SINGLE PRESS (0.5s):
  👤 FACE RECOGNITION
  "Found georgy" or "Unknown person"

DOUBLE PRESS (within 1s):
  📄 OCR TEXT READING
  "Text found: ..."


🔵 EXPECTED OUTPUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No faces:
  ✗ "No person detected"

Recognized person:
  ✓ "Found georgy"

Unknown person:
  ⚠ "Unknown person detected"

Error:
  ✗ "Face recognition error"


🟣 FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/home/nithin/Evolve/projects/visual_implied/
├── main.py                          (main system)
├── face_recognition.py              (recognition module)
├── generate_embeddings.py           (setup script)
├── face_embeddings.json             (generated - keep safe!)
├── georgy/                          (input images - can delete after)
│   └── image1.jpg, image2.jpg, ...
└── ...other files...


⚡ PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

First run:    2-3 seconds (TensorFlow load)
Normal run:   0.5-1 second per face
Memory:       ~50-100 MB
Storage:      ~1 KB per face (embeddings only)


🎯 KEY FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Lightweight (FaceNet 128-d embeddings)
✓ Fast (0.5-1 second)
✓ Private (no cloud, all on-device)
✓ Secure (only vectors, not images)
✓ Integrates with existing system (no conflicts)
✓ Runs in background threads (non-blocking)
✓ Works alongside OCR, navigation, obstacle detection


⚠️ IMPORTANT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• System needs setup with generate_embeddings.py FIRST
• Don't delete face_embeddings.json (or regenerate)
• Face images should be clear, frontal, well-lit
• Multiple angles per person = better accuracy
• Confidence threshold at 0.6 (60%) is recommended
• TensorFlow slow first time - normal behavior
• All other code continues working (threads independent)


📱 TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test face recognition:
  python3 generate_embeddings.py
  (manually add test images)

Test individual components:
  python3 test_sensors.py
  (buzzer, ultrasonic, etc.)

Full system:
  python3 main.py
  (press GPIO 27 single to test faces)


🔗 FILES TO READ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python3 FACE_RECOGNITION_SETUP.py
  → Full setup guide

python3 HARDWARE_SETUP.py
  → Hardware connections

Requirements.txt
  → Dependency list
"""

if __name__ == "__main__":
    print(QUICK_REF)
