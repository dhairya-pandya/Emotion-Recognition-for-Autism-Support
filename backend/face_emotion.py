import cv2
from deepface import DeepFace
from collections import deque, Counter

# Initialize webcam
cap = cv2.VideoCapture(0)

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Buffer to store the last 5 emotion predictions
emotion_buffer = deque(maxlen=5)

# Function to compute mode of emotions
def get_mode_emotion(buffer):
    if not buffer:
        return ""
    emotion_counts = Counter(buffer)
    return emotion_counts.most_common(1)[0][0]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale and RGB
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_roi = rgb[y:y+h, x:x+w]

        try:
            # Analyze emotion using DeepFace
            result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
            current_emotion = result[0]['dominant_emotion']

            # Update the buffer
            emotion_buffer.append(current_emotion)

            # Get mode of buffer
            smoothed_emotion = get_mode_emotion(emotion_buffer)

            # Draw bounding box and emotion label
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, smoothed_emotion, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        except Exception as e:
            print("Analysis error:", e)

    # Display the frame
    cv2.imshow("Facial Emotion Recognition", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()