from ultralytics import YOLO
import cv2

model = YOLO("best.pt")
cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Camera not opened")
    exit()

# Make window resizable
cv2.namedWindow("Currency Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Currency Detection", 900, 700)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.5)
    annotated_frame = results[0].plot()

    cv2.imshow("Currency Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
