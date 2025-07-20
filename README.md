REAL-TIME DUAL EMOTION RECOGNITION APP
======================================

This is a web application designed to help autistic individuals learn and recognize human emotions. It provides real-time analysis of both FACIAL EXPRESSIONS from a webcam and VOCAL TONE from a microphone, displaying the detected emotions in a simple and clear user interface.

Give this repository a star if you liked it, as it integrates multiple AI models into a full-stack web application.

Made with love by Team Getalife();

---
CORE FEATURES
-------------

- Dual-Modal Analysis: Simultaneously detects emotions from facial expressions (via webcam) and speech (via microphone) for a more comprehensive understanding.
- Dedicated AI Backends: Two separate, efficient Python servers powered by Flask serve the facial and speech emotion AI models independently.
- Modern Frontend: A fully responsive and interactive user interface built with Next.js and React.
- Device Selection: A polished, custom dropdown menu allows users to select specific camera and microphone sources.
- Emotion History: Tracks the last five detected facial emotions to show recent changes and patterns.

---
PROJECT ARCHITECTURE
--------------------

The application consists of a Next.js frontend that communicates with two separate Flask backend servers. This separation allows the services to be managed and scaled independently. The data flows as follows:

![WhatsApp Image 2025-07-20 at 08 33 27_7f3593f0](https://github.com/user-attachments/assets/94036406-1f28-468f-8f48-d3c163c934d5)

![WhatsApp Image 2025-07-20 at 08 34 36_4db58321](https://github.com/user-attachments/assets/0c6bd587-b43a-41e6-9de3-6d7b453206a9)


---
HOW THE AI MODELS WORK
----------------------

The application uses two distinct AI pipelines running on the backend to process the video and audio streams.

### Facial Emotion Recognition

The facial analysis pipeline is a multi-step process that identifies a face and classifies its expression using a lightweight Convolutional Neural Network (CNN).

[Image: Facial Emotion Recognition Pipeline at path docs/facial_emotion_diagram.png]

The process works as follows:
1. Face Detection: The system first scans the incoming video frame using a pre-built Haar Cascade classifier, which is a fast and efficient algorithm for locating faces.
2. Cropping & Preprocessing: Once a face is detected, it is cropped from the main frame and converted into a standardized 64x64 pixel grayscale image.
3. The Mini-Xception CNN Model: The core of the analysis is a compact CNN used by the DEEPFACE library. It uses efficient techniques like depthwise separable convolutions to reduce parameters, making it fast enough for real-time analysis.
4. Classification: The final layer uses a Softmax function to classify the features into one of 7 emotion categories.

### Speech Emotion Recognition

The speech analysis pipeline works by converting spoken words into text and then analyzing that text for emotional content.

[Image: Speech Emotion Recognition Pipeline at path docs/speech_emotion_diagram.png]

The process works as follows:
1. Audio Capture: The frontend captures a 5-second packet of audio from the user's selected microphone.
2. Speech-to-Text Conversion: The audio clip is sent to the backend, where the SPEECHRECOGNITION library uses Google's API to transcribe the spoken words into text.
3. Text Classification: The transcribed text is then analyzed by a pre-trained TRANSFORMERS model (DistilBERT) to classify the emotion conveyed by the text's content.
4. Emotion Output: The model's top prediction is returned as the final vocal emotion.

---
TECHNOLOGY STACK
----------------

- Frontend: Next.js, React
- Backends: Python, Flask, Gunicorn
- AI Models: DeepFace (Facial), Hugging Face Transformers & SpeechRecognition (Vocal)
- Deployment: Render / Hugging Face Spaces (Backends), Vercel / Netlify (Frontend)

---
LOCAL DEVELOPMENT SETUP
-----------------------

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Node.js (v18 or later)
- Python (v3.10 or v3.11 recommended) & pip
- Git
- FFmpeg: A required dependency for the backend audio processing.

### Installation

1. Clone the repository:
   (run in terminal) git clone <your-repository-url>
   (run in terminal) cd <your-project-directory>

2. Setup the Python Backend:
   (run in terminal) python -m venv .venv
   (run in terminal) source .venv/bin/activate  (On Windows, use: .venv\Scripts\activate)
   (run in terminal) pip install -r requirements.txt

### Running the Application

You need to run THREE separate servers in three separate terminals.

1. Start the Facial Emotion Backend:
   - From the project's ROOT directory, run:
     (run in terminal) python deepface_api.py

2. Start the Speech Emotion Backend:
   - Open a NEW terminal. From the project's ROOT directory, run:
     (run in terminal) python speech_api.py

3. Start the Frontend:
   - Open a THIRD terminal. Navigate to the `frontend` directory and run:
     (run in terminal) npm run dev

4. Open the App:
   - Open your web browser and go to http://localhost:3000
