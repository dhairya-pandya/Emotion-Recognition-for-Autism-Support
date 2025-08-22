# deepface_api.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# This function contains the core logic for emotion analysis
def analyze_emotion(image_file):
    """
    Analyzes the emotion from an image file stream.
    """
    # Read the image file stream into a numpy array
    filestr = image_file.read()
    npimg = np.fromstring(filestr, np.uint8)
    
    # Decode the image array using OpenCV
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    try:
        # Use DeepFace to analyze the image
        # The 'enforce_detection=False' flag allows the model to analyze faces
        # even if it thinks the detection quality is low.
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        
        # The result is a list, we take the first detected face's result
        dominant_emotion = result[0]['dominant_emotion']
        return dominant_emotion

    except Exception as e:
        # This can happen if DeepFace doesn't detect a face
        print(f"Error during analysis: {e}")
        return "neutral" # Return a default value if no face is found


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected for uploading'}), 400
    
    try:
        emotion = analyze_emotion(file)
        return jsonify({'emotion': emotion})
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': 'Failed to process image on server'}), 500


if __name__ == '__main__':
    print("Starting Flask server for DeepFace API...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))