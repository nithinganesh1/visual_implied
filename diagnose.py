#!/usr/bin/env python3
"""
Diagnostic script to check face recognition setup
"""

import sys
import os

print("\n" + "="*60)
print("FACE RECOGNITION DIAGNOSTIC")
print("="*60 + "\n")

# Check Python version
print("Python version:", sys.version)

# Check imports
print("\n--- Checking Dependencies ---\n")

dependencies = {
    "cv2": "OpenCV",
    "numpy": "NumPy",
    "tensorflow": "TensorFlow",
    "mediapipe": "MediaPipe",
}

for module_name, display_name in dependencies.items():
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {display_name:15} installed (v{version})")
    except ImportError as e:
        print(f"✗ {display_name:15} NOT installed - {e}")

# Check MediaPipe specifically
print("\n--- MediaPipe Detailed Check ---\n")

try:
    import mediapipe as mp
    print("✓ MediaPipe imported successfully")
    print(f"  Version: {mp.__version__}")
    print(f"  Location: {mp.__file__}")
    
    # Try to access solutions
    try:
        from mediapipe import solutions
        print("✓ mediapipe.solutions available")
        
        # Try face detection
        from mediapipe.solutions import face_detection
        print("✓ mediapipe.solutions.face_detection available")
    except Exception as e:
        print(f"✗ mediapipe.solutions issue: {e}")
        print("\n  Trying Tasks API...")
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            print("✓ mediapipe.tasks API available (using this instead)")
        except Exception as e2:
            print(f"✗ mediapipe.tasks also unavailable: {e2}")

except ImportError as e:
    print(f"✗ MediaPipe import failed: {e}")

# Check for georgy folder
print("\n--- Input Data Check ---\n")

georgy_path = "/home/nithin/Evolve/projects/visual_implied/georgy"
if os.path.exists(georgy_path):
    print(f"✓ georgy folder exists: {georgy_path}")
    
    # Count images
    image_count = 0
    for f in os.listdir(georgy_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_count += 1
    
    if image_count > 0:
        print(f"✓ Found {image_count} image(s)")
    else:
        print(f"✗ No images found in georgy folder")
else:
    print(f"✗ georgy folder not found: {georgy_path}")
    print(f"  Create it with: mkdir {georgy_path}")

# Check for embeddings file
print("\n--- Output Data Check ---\n")

if os.path.exists("face_embeddings.json"):
    print("✓ face_embeddings.json exists")
    import json
    try:
        with open("face_embeddings.json") as f:
            data = json.load(f)
        print(f"  Persons: {list(data.keys())}")
        total_embeds = sum(len(v) for v in data.values())
        print(f"  Total embeddings: {total_embeds}")
    except Exception as e:
        print(f"✗ Error reading file: {e}")
else:
    print("- face_embeddings.json not yet created")

# Recommendation
print("\n--- RECOMMENDATION ---\n")

try:
    from mediapipe import solutions
    print("✓ Your setup looks good! Try running:")
    print("  python3 generate_embeddings.py")
except:
    print("⚠️  MediaPipe needs to be fixed. Try:")
    print("\n  Option 1: Reinstall MediaPipe")
    print("  pip uninstall mediapipe")
    print("  pip install mediapipe==0.10.2")
    print("\n  Option 2: Install with exact version")
    print("  pip install mediapipe==0.10.32 --force-reinstall")
    print("\n  Option 3: Check pip status")
    print("  pip list | grep mediapipe")
    print("  pip install --upgrade pip setuptools")

print("\n" + "="*60 + "\n")
