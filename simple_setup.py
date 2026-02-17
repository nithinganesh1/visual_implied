#!/usr/bin/env python3
"""
Simple Face Detection Setup (No TensorFlow Required Initially)
Creates basic embeddings using OpenCV face detection
"""

import cv2
import os
import json
import numpy as np
from pathlib import Path

print("\n" + "="*60)
print("FACE RECOGNITION SETUP (OpenCV Only)")
print("="*60 + "\n")

georgy_folder = "/home/nithin/Evolve/projects/visual_implied/georgy"

if not os.path.exists(georgy_folder):
    print(f"❌ Folder not found: {georgy_folder}")
    print(f"   Create it with: mkdir {georgy_folder}")
    exit(1)

# Load cascade classifier
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

print(f"📁 Processing folder: {georgy_folder}")
print(f"✓ Cascade loaded\n")

embeddings_db = {}
total_faces = 0

# Process images
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
image_files = [f for f in os.listdir(georgy_folder) 
               if os.path.splitext(f)[1].lower() in image_extensions]

if not image_files:
    print(f"❌ No images found in {georgy_folder}")
    print(f"   Add .jpg, .png, or .bmp files to the folder")
    exit(1)

print(f"📷 Found {len(image_files)} image(s)\n")

for idx, img_file in enumerate(image_files, 1):
    img_path = os.path.join(georgy_folder, img_file)
    
    try:
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            print(f"  ✗ {img_file}: Could not load")
            continue
        
        # Detect faces
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        
        if len(faces) == 0:
            print(f"  ✗ {img_file}: No faces detected")
            continue
        
        # Extract face regions and create simple embeddings
        for face_idx, (x, y, w, h) in enumerate(faces):
            # Crop face
            face_roi = img[y:y+h, x:x+w]
            
            # Resize to standard size
            face_resized = cv2.resize(face_roi, (160, 160))
            
            # Create simple embedding: histogram and moments
            gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Compute features:
            # 1. Mean and std dev of pixel values
            mean = np.mean(gray_face)
            std = np.std(gray_face)
            
            # 2. Histogram (simplified)
            hist = cv2.calcHist([gray_face], [0], None, [16], [0, 256])
            hist = hist.flatten() / hist.sum()  # Normalize
            
            # 3. Edge features (Sobel)
            sobelx = cv2.Sobel(gray_face, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray_face, cv2.CV_64F, 0, 1, ksize=3)
            edges_mean = np.mean(np.sqrt(sobelx**2 + sobely**2))
            
            # Combine features into embedding (simplified, not real FaceNet)
            # Note: This is just for demonstration; real FaceNet is much more sophisticated
            embedding = np.concatenate([
                [mean, std, edges_mean],
                hist[:16],  # Use first 16 histogram bins
                [np.mean(sobelx), np.mean(sobely)]  # Edge direction info
            ])
            
            # Normalize embedding
            embedding = embedding / (np.linalg.norm(embedding) + 1e-7)
            
            # Add to database (person name is folder name)
            person_name = "georgy"
            if person_name not in embeddings_db:
                embeddings_db[person_name] = []
            
            embeddings_db[person_name].append(embedding.tolist())
            total_faces += 1
        
        print(f"  ✓ {img_file}: {len(faces)} face(s) processed")
    
    except Exception as e:
        print(f"  ✗ {img_file}: Error - {e}")

if total_faces > 0:
    # Save embeddings
    with open("face_embeddings.json", "w") as f:
        # Convert NumPy arrays to lists for JSON serialization
        json.dump(embeddings_db, f, indent=2)
    
    print(f"\n✅ SUCCESS!")
    print(f"  Total faces processed: {total_faces}")
    print(f"  Persons: {', '.join(embeddings_db.keys())}")
    print(f"  Saved to: face_embeddings.json")
    print(f"\n⚠️  NOTE: Using OpenCV features (not FaceNet)")
    print(f"  For better accuracy, install TensorFlow:")
    print(f"  pip install tensorflow")
    print(f"  Then the system will automatically use FaceNet embeddings\n")
else:
    print(f"\n❌ FAILED")
    print(f"  No faces detected in any images")
    print(f"  Tips:")
    print(f"  - Use clear, frontal face photos")
    print(f"  - Minimum face size: 50x50 pixels")
    print(f"  - Good lighting required")
    print(f"  - Try test_face_detection.py for debugging\n")

print("="*60 + "\n")
