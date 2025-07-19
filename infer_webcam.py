import cv2
import torch
import torch.nn as nn
from torchvision import transforms, models, datasets
from PIL import Image
import os

DATA_DIR = "dataset/train"
NUM_CLASSES = len(os.listdir(DATA_DIR))
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define transform
preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Load class names from folder
dataset = datasets.ImageFolder(DATA_DIR, transform=transforms.ToTensor())
emotion_labels = dataset.classes

# Define and load model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.fc.in_features, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, NUM_CLASSES)
)
model.load_state_dict(torch.load("emotion_resnet18_fold2.pth", map_location=DEVICE,weights_only=True))
model.to(DEVICE)
model.eval()

# Webcam inference
def infer_from_webcam():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Webcam not accessible")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = preprocess(img_rgb).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, predicted = torch.max(probabilities, 0)
            label = emotion_labels[predicted.item()]

        # Display prediction and confidence
        text = f"{label}: {confidence.item()*100:.1f}%"
        cv2.putText(frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Emotion Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    infer_from_webcam()
