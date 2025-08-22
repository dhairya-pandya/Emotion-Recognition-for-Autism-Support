# speech_api.py - AUDIO RECOGNITION DISABLED

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import speech_recognition as sr
# from transformers import pipeline
# import io
# from pydub import AudioSegment # CHANGED: Reverted to pydub

# app = Flask(__name__)
# CORS(app)

# # Load the model once when the server starts
# try:
#     print("🔁 Loading speech emotion model...")
#     emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
#     print("✅ Speech emotion model loaded.")
# except Exception as e:
#     print(f"Error loading model: {e}")
#     emotion_model = None

# recognizer = sr.Recognizer()

# def analyze_speech_emotion(audio_file):
#     """
#     Analyzes emotion from an audio file stream using pydub for robust conversion.
#     """
#     if not emotion_model:
#         raise RuntimeError("Emotion model is not available.")

#     # CHANGED: Use pydub to reliably process the audio file from the browser
#     try:
#         audio = AudioSegment.from_file(io.BytesIO(audio_file.read()))
#         wav_in_memory = io.BytesIO()
#         audio.export(wav_in_memory, format="wav")
#         wav_in_memory.seek(0)
#     except Exception as pydub_error:
#         print(f"Error with pydub processing: {pydub_error}")
#         return {'emotion': 'neutral', 'text': 'Audio processing error'}

#     with sr.AudioFile(wav_in_memory) as source:
#         audio_data = recognizer.record(source)

#     try:
#         text = recognizer.recognize_google(audio_data)
#         print(f"✅ Recognized Text: \"{text}\"")
        
#         predictions = emotion_model(text)
#         dominant_emotion = predictions[0]['label']
        
#         return {'emotion': dominant_emotion, 'text': text}
#     except sr.UnknownValueError:
#         return {'emotion': 'neutral', 'text': 'Could not understand audio'}
#     except sr.RequestError as e:
#         print(f"API Error: {e}")
#         return {'emotion': 'neutral', 'text': 'API request error'}

# @app.route('/predict_speech', methods=['POST'])
# def predict_speech():
#     if 'audio' not in request.files:
#         return jsonify({'error': 'No audio file in request'}), 400
    
#     file = request.files['audio']
    
#     try:
#         result = analyze_speech_emotion(file)
#         return jsonify(result)
#     except Exception as e:
#         print(f"Server error during speech analysis: {e}")
#         return jsonify({'error': 'Failed to process audio'}), 500

# if __name__ == '__main__':
#     print("Starting Flask server for Speech Emotion API...")
#     app.run(host='127.0.0.1', port=5001)