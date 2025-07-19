import cv2
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from PIL import Image

# Load trained model (e.g. best fold)
model = models.resnet18(pretrained=False)
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.fc.in_features, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, NUM_CLASSES)
)
model.load_state_dict(torch.load("emotion_resnet18_fold1.pth"))
model.to(DEVICE)
model.eval()

# Prepare labels
emotion_labels = dataset.classes

# Webcam inference
def infer_from_webcam():
    cap = cv2.VideoCapture(0)

    preprocess = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = preprocess(img).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = output.max(1)
            label = emotion_labels[predicted.item()]

        cv2.putText(frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Emotion Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run it
# infer_from_webcam()
