import cv2

# Open default camera (0)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Camera not opened")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Camera", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
