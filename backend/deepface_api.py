# deepface_api.py

import os
import traceback
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np

# --- IMPROVEMENT 3: Configure proper logging ---
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Allow requests specifically from your frontend's Render domain
CORS(app, resources={r"/predict": {"origins": "https://emotion-recognition-for-autism-support.onrender.com"}})  # Enable Cross-Origin Resource Sharing

# --- IMPROVEMENT 1: Pre-load the AI model on startup ---
try:
    app.logger.info("Pre-loading DeepFace model...")
    _ = DeepFace.build_model("Emotion")
    app.logger.info("Model pre-loaded successfully.")
except Exception as e:
    app.logger.error("FATAL: Could not pre-load model.")
    app.logger.error(traceback.format_exc())
# ----------------------------------------------------

def analyze_emotion(image_file):
    """
    Analyzes the emotion from an image file stream.
    """
    try:
        filestr = image_file.read()
        npimg = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        return dominant_emotion

    except Exception as e:
        app.logger.error(f"Error during analysis: {e}")
        return "neutral"

# --- IMPROVEMENT 2: Add a health check endpoint ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running."}), 200
# ------------------------------------------------

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
        app.logger.error(f"Server error during /predict: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to process image on server'}), 500


if __name__ == '__main__':
    app.logger.info("Starting Flask server for local development...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))