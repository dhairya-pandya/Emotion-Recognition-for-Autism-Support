// page.js

"use client";
import { useRef, useState, useEffect } from "react";

// The rest of your component code remains the same...

export default function HomePage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [emotion, setEmotion] = useState("");
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [error, setError] = useState("");
  const [stream, setStream] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [isMirrored, setIsMirrored] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then((deviceInfos) => {
      const videoDevices = deviceInfos.filter(
        (device) => device.kind === "videoinput"
      );
      setDevices(videoDevices);
      if (videoDevices.length > 0) {
        setSelectedDeviceId(videoDevices[0].deviceId);
      }
    });
  }, []);

  useEffect(() => {
    if (!isCameraOn || !videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d', { willReadFrequently: true });

    const intervalId = setInterval(() => {
      if (video.readyState < 2) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(async (blob) => {
        if (!blob) return;

        const formData = new FormData();
        formData.append('image', blob, 'webcam-frame.jpg');

        try {
          const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
          }

          const data = await response.json();
          const detectedEmotion = data.emotion;

          setEmotion(detectedEmotion);
          setEmotionHistory((prevHistory) => {
            if (prevHistory[0]?.emotion !== detectedEmotion) {
              const newEntry = { emotion: detectedEmotion, timestamp: Date.now() };
              return [newEntry, ...prevHistory].slice(0, 5);
            }
            return prevHistory;
          });

        } catch (apiError) {
          console.error("Error predicting emotion:", apiError);
          setError("Could not connect to the AI model.");
        }
      }, 'image/jpeg');
    }, 2000);

    return () => clearInterval(intervalId);
  }, [isCameraOn]);

  const startCamera = async (deviceId = selectedDeviceId) => {
    setError("");
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: deviceId ? { deviceId: { exact: deviceId } } : true,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setStream(mediaStream);
      setIsCameraOn(true);
    } catch (err) {
      console.error("Error starting camera:", err);
      if (err.name === "NotAllowedError") {
        setError("Camera access was denied. Please check browser permissions.");
      } else if (err.name === "NotFoundError") {
        setError("No camera was found. Please ensure a webcam is connected.");
      } else if (err.name === "NotReadableError") {
        setError("The camera is in use by another application or process.");
      } else {
        setError("Could not start video source. The selected camera may be unavailable.");
      }
      setIsCameraOn(false);
    }
  };
  
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    setIsCameraOn(false);
    setStream(null);
    setEmotion("");
    setEmotionHistory([]);
  };
  const toggleMirror = () => setIsMirrored((prev) => !prev);
  const handleDeviceChange = (e) => {
    const deviceId = e.target.value;
    setSelectedDeviceId(deviceId);
    if (isCameraOn) {
      startCamera(deviceId);
    }
  };

  // CHANGED: Added an entry for "surprise" to match the backend's output
  const emotionData = {
    happy: { emoji: "😊", explanation: "A smile and raised cheeks usually mean someone is happy." },
    sad: { emoji: "😢", explanation: "Downturned lips and raised inner eyebrows can show sadness." },
    surprise: { emoji: "😲", explanation: "Wide eyes and an open mouth often signal surprise." },
    neutral: { emoji: "😐", explanation: "A relaxed face with no strong expression is typically neutral." },
    angry: { emoji: "😠", explanation: "Lowered eyebrows and tense lips can indicate anger." },
    fear: { emoji: "😨", explanation: "Raised eyebrows and a slightly open mouth can show fear." },
    disgust: { emoji: "🤢", explanation: "A wrinkled nose and raised upper lip often express disgust." },
  };

  const currentEmotionData = emotionData[emotion];

  return (
    <div className="container">
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <header className="header">
        <h1>Learn Emotions through Expressions</h1>
        <p>
          Helping autistic individuals recognize non-verbal gestures through live
          emotion detection.
        </p>
      </header>
      <div className="main-content">
        <div className="left-panel">
           <section className="video-section">
            <div className="video-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`video-feed ${isMirrored ? "mirrored" : ""}`}
              />
            </div>
            <div className="controls-area">
                <div className="main-controls">
                    {!isCameraOn ? (
                        <button onClick={() => startCamera()} className="start-button">
                        Start Camera
                        </button>
                    ) : (
                        <button onClick={stopCamera} className="secondary-button">
                        Stop Camera
                        </button>
                    )}
                </div>
                <div className="settings-control">
                    <button onClick={() => setShowSettings((prev) => !prev)} className="settings-button" title="Settings">
                        ⚙️
                    </button>
                </div>
            </div>
            {error && <p className="error-text">{error}</p>}

            {showSettings && (
              <div className="settings-menu">
                <div className="settings-item">
                  <label>Camera Source</label>
                  <div className="camera-source-list">
                    {devices.map((device) => (
                      <label key={device.deviceId} className={`camera-option ${selectedDeviceId === device.deviceId ? 'selected' : ''}`}>
                        <input
                          type="radio"
                          name="camera-source"
                          value={device.deviceId}
                          checked={selectedDeviceId === device.deviceId}
                          onChange={handleDeviceChange}
                        />
                        <span className="camera-icon">📷</span>
                        <span className="camera-name">{device.label || `Camera ${device.deviceId.slice(0, 8)}`}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="settings-item">
                  <label>Mirror Video:</label>
                  <button onClick={toggleMirror} className="toggle-button">
                     {isMirrored ? "On" : "Off"}
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>

        <div className="right-panel">
          <section className="emotion-display">
            <h2>Detected Emotion</h2>
            {isCameraOn && currentEmotionData ? (
              <div className="emotion-info">
                <span className="emoji">{currentEmotionData.emoji}</span>
                <span className="emotion-text">{emotion.charAt(0).toUpperCase() + emotion.slice(1)}</span>
                <p className="explanation">{currentEmotionData.explanation}</p>
              </div>
            ) : (
              <p className="placeholder-text">
                {isCameraOn ? "Detecting..." : "Start the camera to begin."}
              </p>
            )}
          </section>

          <section className="history-section">
            <h3>Recent History</h3>
            {emotionHistory.length > 0 ? (
              <ul className="history-list">
                {emotionHistory.map((item) => (
                  <li key={item.timestamp} className="history-item">
                    <span className="emoji-small">{emotionData[item.emotion]?.emoji}</span>
                    <span>{item.emotion.charAt(0).toUpperCase() + item.emotion.slice(1)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="placeholder-text-small">No history yet.</p>
            )}
          </section>
        </div>
      </div>
      <footer className="footer">
        <p>Made with ❤️ for Autism Support</p>
      </footer>
    </div>
  );
}