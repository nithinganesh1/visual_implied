from ultralytics import YOLO
import cv2

# Load your trained model
model = YOLO("best.pt")   # path to your trained weights

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera not opened")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference with confidence threshold 0.6
    results = model(frame, conf=0.6)

    # Plot results on frame
    annotated_frame = results[0].plot()

    # Show output
    cv2.imshow("YOLO Detection", annotated_frame)

    # Press q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
