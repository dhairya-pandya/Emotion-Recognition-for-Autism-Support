// page.js

"use client";
import { useRef, useState, useEffect } from "react";

const emotionData = {
  happy: { emoji: "😊", explanation: "A smile and raised cheeks usually mean someone is happy." },
  sad: { emoji: "😢", explanation: "Downturned lips and raised inner eyebrows can show sadness." },
  surprise: { emoji: "😲", explanation: "Wide eyes and an open mouth often signal surprise." },
  neutral: { emoji: "😐", explanation: "A relaxed face with no strong expression is typically neutral." },
  angry: { emoji: "😠", explanation: "Lowered eyebrows and tense lips can indicate anger." },
  fear: { emoji: "😨", explanation: "Raised eyebrows and a slightly open mouth can show fear." },
  disgust: { emoji: "🤢", explanation: "A wrinkled nose and raised upper lip often express disgust." },
};

export default function HomePage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  // const mediaRecorderRef = useRef(null);
  // const audioChunksRef = useRef([]);
  
  const cameraSelectRef = useRef(null);
  // const audioSelectRef = useRef(null);

  const [isCameraOn, setIsCameraOn] = useState(false);
  const [facialEmotion, setFacialEmotion] = useState("");
  // const [speechEmotion, setSpeechEmotion] = useState("");
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [error, setError] = useState("");
  const [stream, setStream] = useState(null);
  
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  
  // const [audioDevices, setAudioDevices] = useState([]);
  // const [selectedAudioDeviceId, setSelectedAudioDeviceId] = useState("");

  const [isCameraMenuOpen, setCameraMenuOpen] = useState(false);
  // const [isAudioMenuOpen, setAudioMenuOpen] = useState(false);

  const [isMirrored, setIsMirrored] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (cameraSelectRef.current && !cameraSelectRef.current.contains(event.target)) {
        setCameraMenuOpen(false);
      }
      // if (audioSelectRef.current && !audioSelectRef.current.contains(event.target)) {
      //   setAudioMenuOpen(false);
      // }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const updateDeviceList = () => {
    navigator.mediaDevices.enumerateDevices().then((deviceInfos) => {
      const videoDevices = deviceInfos.filter((device) => device.kind === "videoinput");
      // const audioInputDevices = deviceInfos.filter((device) => device.kind === "audioinput");
      
      setDevices(videoDevices);
      // setAudioDevices(audioInputDevices);

      if (!selectedDeviceId && videoDevices.length > 0) {
        setSelectedDeviceId(videoDevices[0].deviceId);
      }
      // if (!selectedAudioDeviceId && audioInputDevices.length > 0) {
      //   setSelectedAudioDeviceId(audioInputDevices[0].deviceId);
      // }
    });
  };

  useEffect(() => {
    updateDeviceList();
  }, []);

  useEffect(() => {
    if (!isCameraOn) return;
    const analysisInterval = setInterval(() => {
      analyzeFacialEmotion();
      // analyzeVocalEmotion();
    }, 5000);
    return () => clearInterval(analysisInterval);
  }, [isCameraOn]);

  const analyzeFacialEmotion = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    
    if (video.readyState < 2) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const formData = new FormData();
      formData.append('image', blob, 'webcam-frame.jpg');

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL_DEEPFACE}/predict`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Facial API Error');
        const data = await response.json();
        const detectedEmotion = data.emotion;
        
        setFacialEmotion(detectedEmotion);
        setEmotionHistory((prev) => [detectedEmotion, ...prev].slice(0, 5));
      } catch (e) {
        console.error("Facial analysis error:", e);
      }
    }, 'image/jpeg');
  };

  // const analyzeVocalEmotion = () => {
  //   if (!stream) return;
  //   try {
  //     mediaRecorderRef.current = new MediaRecorder(stream);
  //     audioChunksRef.current = [];

  //     mediaRecorderRef.current.ondataavailable = (event) => {
  //       audioChunksRef.current.push(event.data);
  //     };

  //     mediaRecorderRef.current.onstop = async () => {
  //       const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
  //       const formData = new FormData();
  //       formData.append('audio', audioBlob, 'speech.wav');

  //       try {
  //         const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL_SPEECH}/predict_speech`, { method: 'POST', body: formData });
  //         if (!response.ok) throw new Error('Speech API Error');
  //         const data = await response.json();
  //         setSpeechEmotion(data.emotion);
  //       } catch (e) {
  //         console.error("Speech analysis error:", e);
  //       }
  //     };

  //     mediaRecorderRef.current.start();
  //     setTimeout(() => {
  //       if(mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
  //           mediaRecorderRef.current.stop();
  //       }
  //     }, 4800);

  //   } catch(e) {
  //     console.error("MediaRecorder setup failed:", e);
  //   }
  // };
  
  const startCamera = async (videoDeviceId = selectedDeviceId) => {
    setError("");
    if (stream) stream.getTracks().forEach((track) => track.stop());

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: videoDeviceId ? { exact: videoDeviceId } : undefined },
        // audio: { deviceId: audioDeviceId ? { exact: audioDeviceId } : undefined },
      });
      if (videoRef.current) videoRef.current.srcObject = mediaStream;
      setStream(mediaStream);
      setIsCameraOn(true);
      updateDeviceList();
    } catch (err) {
      console.error("Error starting media:", err);
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
    setFacialEmotion("");
    // setSpeechEmotion("");
    setEmotionHistory([]);
  };
  
  const toggleMirror = () => setIsMirrored((prev) => !prev);

  const handleDeviceChange = (newVideoDeviceId) => {
    setSelectedDeviceId(newVideoDeviceId);
    if (isCameraOn) {
      startCamera(newVideoDeviceId);
    }
    setCameraMenuOpen(false);
  };

  // const handleAudioDeviceChange = (newAudioDeviceId) => {
  //   setSelectedAudioDeviceId(newAudioDeviceId);
  //   if (isCameraOn) {
  //     startCamera(selectedDeviceId, newAudioDeviceId);
  //   }
  //   setAudioMenuOpen(false);
  // };
  
  const getSelectedDeviceLabel = (devices, id, type) => {
    const device = devices.find(d => d.deviceId === id);
    if (device && device.label) return device.label;
    if (devices.length > 0) return `${type} 1`;
    return `No ${type} found`;
  };

  const currentFacialEmotionData = emotionData[facialEmotion];
  // const currentSpeechEmotionData = emotionData[speechEmotion];

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
                  <div className="custom-select-container" ref={cameraSelectRef}>
                    <button className="custom-select-button" onClick={() => setCameraMenuOpen(prev => !prev)}>
                      <span className="select-icon">📷</span>
                      <span>{getSelectedDeviceLabel(devices, selectedDeviceId, 'Camera')}</span>
                    </button>
                    {isCameraMenuOpen && (
                      <ul className="custom-select-menu">
                        {devices.map((device) => (
                          <li key={device.deviceId} className={`custom-select-option ${selectedDeviceId === device.deviceId ? 'selected' : ''}`} onClick={() => handleDeviceChange(device.deviceId)}>
                            {device.label || `Camera ${device.deviceId.slice(0, 8)}`}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {/* <div className="settings-item">
                  <label>Microphone Source</label>
                   <div className="custom-select-container" ref={audioSelectRef}>
                    <button className="custom-select-button" onClick={() => setAudioMenuOpen(prev => !prev)}>
                      <span className="select-icon">🎤</span>
                      <span>{getSelectedDeviceLabel(audioDevices, selectedAudioDeviceId, 'Microphone')}</span>
                    </button>
                    {isAudioMenuOpen && (
                      <ul className="custom-select-menu">
                        {audioDevices.map((device) => (
                          <li key={device.deviceId} className={`custom-select-option ${selectedAudioDeviceId === device.deviceId ? 'selected' : ''}`} onClick={() => handleAudioDeviceChange(device.deviceId)}>
                            {device.label || `Microphone ${device.deviceId.slice(0, 8)}`}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div> */}
                
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
            <h2>Facial Emotion</h2>
            {isCameraOn && currentFacialEmotionData ? (
              <div className="emotion-info">
                <span className="emoji">{currentFacialEmotionData.emoji}</span>
                <span className="emotion-text">{facialEmotion.charAt(0).toUpperCase() + facialEmotion.slice(1)}</span>
                <p className="explanation">{currentFacialEmotionData.explanation}</p>
              </div>
            ) : ( <p className="placeholder-text">{isCameraOn ? "Detecting..." : "Start camera"}</p> )}
          </section>

          {/* <section className="emotion-display vocal-emotion-section">
            <h2>Vocal Emotion</h2>
            {isCameraOn && currentSpeechEmotionData ? (
              <div className="emotion-info">
                <span className="emoji">{currentSpeechEmotionData.emoji}</span>
                <span className="emotion-text">{speechEmotion.charAt(0).toUpperCase() + speechEmotion.slice(1)}</span>
              </div>
            ) : ( <p className="placeholder-text">{isCameraOn ? "Listening..." : "Start camera"}</p> )}
          </section> */}

          <section className="history-section">
            <h3>Facial Emotion History</h3>
            {emotionHistory.length > 0 ? (
              <ul className="history-list">
                {emotionHistory.map((item, index) => (
                    <li key={`${item}-${index}`} className="history-item">
                        <span className="emoji-small">{emotionData[item]?.emoji}</span>
                        <span>{item.charAt(0).toUpperCase() + item.slice(1)}</span>
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