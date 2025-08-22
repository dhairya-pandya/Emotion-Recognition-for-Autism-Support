# speech_model.py - AUDIO RECOGNITION DISABLED

# import speech_recognition as sr
# from transformers import pipeline
# from googletrans import Translator
# import time

# # Load emotion classification pipeline
# print("🔁 Loading emotion detection model...")
# emotion_model = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# # Initialize recognizer, microphone, and translator
# recognizer = sr.Recognizer()
# mic = sr.Microphone()
# translator = Translator()  # ADDED: Create an instance of the Translator class

# print("🎙 Real-time Speech Emotion Detector Started")
# print("Speak something... (Ctrl+C to stop)\n")

# try:
#     while True:
#         with mic as source:
#             print("🟢 Listening for 5 seconds...")
#             recognizer.adjust_for_ambient_noise(source, duration=0.5)
#             audio = recognizer.listen(source, phrase_time_limit=5)

#         try:
#             print("🔠 Converting to text...")
#             text = recognizer.recognize_google(audio)
            
#             # CHANGED: Call the translate method on the translator object
#             translated_result = translator.translate(text, dest='en')
#             translated_text = translated_result.text
#             print(f"📝 Transcription: \"{translated_text}\"")

#             print("🔍 Predicting emotion...")
#             # Analyze the original English text
#             predictions = emotion_model(text)
#             top_prediction = predictions[0]

#             print(f"🎭 Emotion: {top_prediction['label']} (Confidence: {top_prediction['score']:.2f})")

#         except sr.UnknownValueError:
#             print("⚠ Could not understand audio.")
#         except sr.RequestError as e:
#             print(f"❌ Could not request results from Google API: {e}")

#         time.sleep(0.5)

# except KeyboardInterrupt:
#     print("\n🛑 Program stopped by user.")