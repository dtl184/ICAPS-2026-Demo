import cv2
from pupil_apriltags import Detector

# --- Configure the AprilTag detector ---
detector = Detector(
    families="tag25h9",   # common AprilTag family
    nthreads=4,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

# --- Open webcam ---
cap = cv2.VideoCapture(2, cv2.CAP_V4L2) 

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit(1)

print("Press Ctrl+C or close the window to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags
    results = detector.detect(gray)

    # Draw detections
    for r in results:
        (ptA, ptB, ptC, ptD) = r.corners
        ptA = tuple(map(int, ptA))
        ptB = tuple(map(int, ptB))
        ptC = tuple(map(int, ptC))
        ptD = tuple(map(int, ptD))

        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

        # Draw center
        cX, cY = int(r.center[0]), int(r.center[1])
        cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

        # Put tag ID text
        cv2.putText(frame, f"ID: {r.tag_id}",
                    (ptA[0], ptA[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

    cv2.imshow("AprilTag Detection", frame)

    if cv2.waitKey(1) == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
