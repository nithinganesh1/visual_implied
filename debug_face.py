import cv2, sys, os
cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade)

cap = cv2.VideoCapture(0)        # try 0, or 1 if 0 is wrong
ret, frame = cap.read()
cap.release()
if not ret or frame is None:
    print("❌ Camera read failed")
    sys.exit(1)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
print("Faces detected:", len(faces))
for (x,y,w,h) in faces:
    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

out = "face_debug.jpg"
cv2.imwrite(out, frame)
print("Saved annotated frame to", out)