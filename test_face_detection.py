import cv2
import os

image_path = "/home/nithin/Evolve/projects/visual_implied/georgy/20260120_145051(0).jpg"

img = cv2.imread(image_path)

if img is None:
    print("Failed to load image")
    exit()

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=8,   # increased to reduce false positives
    minSize=(60, 60)  # ignore tiny detections
)

print("✅ Haar Detection worked!")
print(f"   Faces detected: {len(faces)}")
print(f"   Ready for main.py")
