# **QUICK REFERENCE: 3 Ways to Setup Face Recognition**

## **Option A: Fast (2 mins, OpenCV Only)** ⚡
```bash
# 1. Add face photos to georgy/ folder
mkdir -p georgy
# Copy your face .jpg files here

# 2. Generate embeddings
python3 simple_setup.py

# 3. Done! Test with:
python3 test_face_detection.py

# 4. Use in main system
python3 main.py
# Press GPIO 27 once → face recognition
```

**Pros:** Works immediately, no dependencies  
**Cons:** ~85% accuracy (good enough for most uses)

---

## **Option B: Better (10 mins, TensorFlow + FaceNet)** 🚀
```bash
# 1. Install TensorFlow
pip install tensorflow

# 2. Download FaceNet model
wget https://github.com/nyoki-mtl/pytorch-facenet/raw/master/data/facenet_keras.h5

# 3. Add face photos to georgy/ folder
mkdir -p georgy
# Copy your face .jpg files here

# 4. Generate FaceNet embeddings
python3 generate_embeddings.py

# 5. Test and use
python3 main.py
```

**Pros:** Excellent accuracy (~98%), professional-grade  
**Cons:** Takes time to install, uses more memory

---

## **Option C: No Setup (Use existing system)** ✅
```bash
# Skip face recognition for now
# Currency detection, ultrasonic, buzzer all work  
# Add georgy/ folder later when ready

python3 main.py
# Press GPIO 27 once → will show "No person" (no embeddings yet)
# Other features work fine
```

---

## **System Works With Any Option**

| Feature | Status | Depends On |
|---------|--------|-----------|
| Currency detection | ✅ Works | Object detection (always enabled) |
| Ultrasonic sensor | ✅ Works | HC-SR04 wiring |
| Adaptive buzzer | ✅ Works | GPIO 26 PWM |
| OCR text reading | ✅ Works | GPIO 27 double-press |
| **Face recognition** | **Requires setup** | **Options A or B above** |

---

## **Commands Reference**

```bash
# Check what's installed
python3 diagnose.py

# Test face detection (webcam required)
python3 test_face_detection.py

# Simple setup (no TensorFlow)
python3 simple_setup.py

# Advanced setup (requires TensorFlow)
python3 generate_embeddings.py

# Run full system
python3 main.py

# Test sensors
python3 test_sensors.py
```

---

## **Key Files**

| File | Purpose |
|------|---------|
| `simple_setup.py` | Generate embeddings (OpenCV only) |
| `generate_embeddings.py` | Generate embeddings (FaceNet) |
| `face_recognition.py` | Core face detection & recognition |
| `main.py` | System orchestrator, GPIO 27 = faces |
| `test_face_detection.py` | Verify face detection works |
| `diagnose.py` | Check dependency versions |
| `FACE_SETUP_GUIDE.md` | Detailed setup guide |
| `georgy/` | Folder with your reference face photos |
| `face_embeddings.json` | Generated database (created by setup scripts) |

---

## **Recommendation**

**Start with Option A** (simple_setup.py):
- Takes 2 minutes
- Works reliably  
- Use OpenCV's Haar Cascade for detection
- Good for testing

**Upgrade to Option B** later if needed:
- Better accuracy for real deployment
- Install when you have time
- System automatically uses FaceNet if available

---

## **GPIO 27 Behavior**

- **Once** → Face recognition  
  - Detects face in view  
  - Announces: "Found georgy", "Unknown person", or "No person"
  
- **Twice** → OCR text reading
  - Reads text from camera  
  - Speaks the text aloud

---

**Ready?** → `python3 simple_setup.py`
