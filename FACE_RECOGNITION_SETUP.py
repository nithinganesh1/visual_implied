#!/usr/bin/env python3
"""
FACE RECOGNITION SETUP GUIDE
Complete setup for FaceNet-based face recognition
"""

SETUP_GUIDE = """
╔════════════════════════════════════════════════════════════════════╗
║         FACE RECOGNITION SYSTEM SETUP & USAGE                     ║
║              (GPIO 27 Single Press = Face Recognition)            ║
╚════════════════════════════════════════════════════════════════════╝

🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PREPARE IMAGES
   ├─ Create folder: ~/visual_implied/georgy/
   ├─ Add face images (jpg, png, bmp)
   ├─ Clear, frontal faces work best
   └─ Multiple angles per person = better accuracy

2. GENERATE EMBEDDINGS
   ├─ Run: python3 generate_embeddings.py
   ├─ Processes images from georgy/ folder
   ├─ Creates: face_embeddings.json (~1KB per face)
   └─ Optional: Delete georgy/ folder to save space

3. START SYSTEM
   ├─ Run: python3 main.py
   ├─ Face recognition auto-loads embeddings
   └─ GPIO 27 ready for face detection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 HARDWARE BUTTONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GPIO 17 (Primary Button):
├─ Single Press   → Scene Detection (original)
├─ Double Press   → Crossing Safety Check
└─ Press + Hold   → Emergency Alert

GPIO 27 (Face/OCR Button):
├─ Single Press   → FACE RECOGNITION (NEW!)
│  └─ Process: Frame → Face Detection → Embedding → Compare
│     Output: "Found [Name]" or "Unknown person"
│
└─ Double Press   → OCR Text Reading
   └─ Same as before

GPIO 23-24: HC-SR04 Ultrasonic (obstacle detection)
GPIO 26: Passive Buzzer (warning sounds)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 SYSTEM ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FACE RECOGNITION FLOW:
┌─────────────────┐
│   Camera Frame  │
└────────┬────────┘
         ↓
┌─────────────────────────────────┐
│ MediaPipe Face Detection        │ (fast, short-range)
│ Returns: bounding boxes         │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Crop Face Region                │ (128x128 to 160x160)
│ Preprocess & Normalize          │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ FaceNet Model (Embedding)       │ (outputs 128-d vector)
│ outputs: 128-dimensional vector │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Compare with Stored Embeddings  │ (JSON database)
│ Euclidean Distance Metric       │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Decision:                       │
│ Confidence > 60%? → RECOGNIZED  │
│ Else → UNKNOWN                  │
└────────┬────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Audio Output:                   │
│ "Found [Name]" or               │
│ "Unknown person detected"        │
└─────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 FACE EMBEDDINGS DATABASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: face_embeddings.json

Format:
{
  "georgy": [
    [0.123, -0.456, 0.789, ...],  ← 128-d vector
    [0.234, -0.567, 0.890, ...],  ← Another photo
    ...
  ],
  "other_person": [
    [...],
    ...
  ]
}

Features:
✓ Lightweight: ~1KB per face
✓ Human-readable JSON
✓ Can be copied/backed up
✓ No images stored - only embeddings
✓ Compatible with other systems

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 USAGE SCENARIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario 1: Friend Visits
────────────────────────
1. Press GPIO 27 once
2. System announces: "Found georgy"
3. Know who's in front

Scenario 2: Security Check
──────────────────────────
1. Press GPIO 27 once (automatic daily)
2. System announces person's name
3. Log for security audit

Scenario 3: Family Reunion
─────────────────────────
1. Setup with multiple family faces
2. Press GPIO 27 as people approach
3. System identifies each family member

Scenario 4: Combined Navigation
───────────────────────────────
1. Press GPIO 17 single = "Nearby objects?"
2. Press GPIO 27 single = "Who's here?"
3. Press GPIO 27 double = "What text on sign?"
4. All work independently, no conflicts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ CUSTOMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CHANGE CONFIDENCE THRESHOLD
   
   File: main.py
   Location: FaceRecognitionModule initialization
   
   self.face_recognition = FaceRecognitionModule(
       ...
       confidence_threshold=0.6  # ← Change this (0-1)
   )
   
   Higher = Stricter matching (fewer false positives)
   Lower = More lenient (faster recognition)
   Recommended: 0.6 (60%)

2. ADD MORE PEOPLE
   
   a) Create folder: ~/visual_implied/georgy/
   b) Add subfolders: john/, sarah/, etc.
   c) Add their images to subfolders
   d) Run: python3 generate_embeddings.py
   e) Embeddings auto-add to JSON

3. ADJUST FACE DETECTION RANGE
   
   File: face_recognition.py
   In __init__():
   
   self.face_detector = mp.solutions.face_detection.FaceDetection(
       model_selection=0,  # 0=short (<2m), 1=long (>4m)
       min_detection_confidence=0.7  # ← Adjust
   )

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "No persons detected" when person is present
  ✓ Check lighting (face needs to be visible)
  ✓ Ensure person is in front of camera
  ✓ Adjust confidence threshold lower
  ✓ Check face size (should be visible portion of frame)

Issue: Always says "Unknown person" 
  ✓ Run: python3 generate_embeddings.py (to regenerate)
  ✓ Ensure georgy/ folder has clear images
  ✓ Check: python3 -c "import json; print(json.load(open('face_embeddings.json')))"
  ✓ Person might need more varied angle photos

Issue: Face recognition very slow
  ✓ Normal: TensorFlow first run takes 2-3 seconds
  ✓ Subsequent runs: ~0.5-1 second
  ✓ This is background - doesn't block other operations

Issue: "FaceNet model not found"
  ✓ Model optional - system works without it (just face detection)
  ✓ Download from: https://github.com/nyoki-mtali/keras-facenet
  ✓ Place as: facenet_keras.h5
  ✓ Without it: Only detects faces, can't identify people

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 REQUIRED FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated (auto):
✓ face_embeddings.json  (~1-100 KB)

Optional (for accuracy):
○ facenet_keras.h5     (download ~25 MB)

Not included (use MediaPipe):
✓ Face detection       (built-in)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 PRIVACY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ NO IMAGES STORED
  Only 128-dimensional numerical vectors kept
  
✓ LOCAL PROCESSING
  All face recognition runs on RPi5
  No cloud/network transmission
  
✓ ANONYMOUS VECTORS
  Embeddings can't be reversed to images
  Secure against privacy breaches

✓ FAST & PRIVATE
  On-device processing
  ~0.5-1 second per face
  No latency, no upload

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prepare images in ~/visual_implied/georgy/
2. Run: python3 generate_embeddings.py
3. Run: python3 main.py
4. Press GPIO 27 once to test face recognition
5. Use GPIO 27 double-press for OCR text reading
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
