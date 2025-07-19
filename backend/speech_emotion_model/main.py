# Suggested filename: realtime_speech_emotion.py

import sys
import queue
import threading
import sounddevice as sd
from transformers import pipeline
import numpy as np
from collections import Counter # ADDED: Import Counter for mode calculation

# --- Configuration ---
MODEL_PATH = "./speech-emotion-model"
DEVICE_ID = None  # Or set a specific device ID, e.g., 3
SAMPLE_RATE = 16000
BLOCK_SIZE = 16000  # Analyze audio in 1-second chunks (16000 frames)

# A queue to hold audio chunks between the listener and analyzer threads
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This function is called by the sounddevice stream for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Add the incoming audio data (a NumPy array) to the queue
    audio_queue.put(indata.copy())

def main():
    """
    Loads the model and starts the listener and analyzer threads.
    """
    # 1. Load the model once at the beginning
    print("Loading speech emotion model... (This may take a moment)")
    try:
        classifier = pipeline("audio-classification", model=MODEL_PATH)
        print("✅ Model loaded. Starting real-time analysis.")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
        
    print("\n🎤 Your microphone is now live.")
    print("The program will report the most common emotion every 5 seconds.")
    print("Press Ctrl+C to stop the program.")

    try:
        # ADDED: A list to buffer predictions for 5 seconds
        prediction_buffer = []

        # 2. Start the microphone input stream in a background thread
        with sd.InputStream(device=DEVICE_ID,
                            samplerate=SAMPLE_RATE,
                            blocksize=BLOCK_SIZE,
                            channels=1,
                            dtype='float32',
                            callback=audio_callback):
            
            # 3. The main thread will be the analyzer
            while True:
                # Get the next audio chunk from the queue
                audio_chunk = audio_queue.get()

                # The pipeline expects a 1D array, so we flatten the chunk
                audio_array = audio_chunk.flatten()
                
                # Analyze the audio chunk
                predictions = classifier(audio_array)
                
                # Get the top prediction's label
                top_emotion = predictions[0]['label']
                
                # CHANGED: Instead of printing, add the prediction to our buffer
                prediction_buffer.append(top_emotion)
                
                # Update the display to show progress
                print(f"\rAnalyzing... [{len(prediction_buffer)}/5]", end="")

                # If the buffer has 5 seconds of predictions, process it
                if len(prediction_buffer) == 5:
                    # Use Counter to find the most common emotion (the mode)
                    emotion_counts = Counter(prediction_buffer)
                    mode_emotion = emotion_counts.most_common(1)[0][0]
                    
                    # Clear the line and print the final result
                    # The extra spaces at the end clear the previous "Analyzing..." text
                    print(f"\rDetected Emotion: {mode_emotion:<15}", end="\n")
                    
                    # Clear the buffer to start the next 5-second window
                    prediction_buffer.clear()

    except KeyboardInterrupt:
        print("\nExiting program.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    main()